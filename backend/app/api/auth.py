import hashlib
import hmac
import logging
import secrets
import smtplib
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User, Organization, RoleEnum
from app.models.login_otp import LoginOTPChallenge
from app.models.registration_otp import RegistrationOTPChallenge
from app.schemas.auth import (
    RegisterRequest, RegistrationOTPRequest, RegistrationOTPVerifyRequest, LoginRequest, LoginOTPRequest, LoginOTPVerifyRequest,
    ChangePasswordRequest, TokenResponse, UserOut,
)
from app.security import hash_password, verify_password, create_access_token
from app.services.email import send_login_code

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)
OTP_MAX_ATTEMPTS = 5
OTP_REQUEST_MESSAGE = "If an active account exists for that email, a sign-in code has been sent."
REGISTRATION_OTP_MESSAGE = "If this email is available, a verification code has been sent."


def _require_email_delivery(settings):
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        raise HTTPException(status_code=503, detail="Email verification is not configured. Contact your administrator.")
    if getattr(settings, "SMTP_USERNAME", "") and not getattr(settings, "SMTP_PASSWORD", ""):
        raise HTTPException(status_code=503, detail="SMTP_PASSWORD is missing. Configure your email provider's app password.")


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role.value,
        organization_id=user.organization_id,
        organization_name=user.organization.name if user.organization else None,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    now = datetime.utcnow()
    challenge = (
        db.query(RegistrationOTPChallenge)
        .filter(
            RegistrationOTPChallenge.email == payload.email,
            RegistrationOTPChallenge.consumed.is_(False),
            RegistrationOTPChallenge.verified.is_(True),
        )
        .order_by(RegistrationOTPChallenge.created_at.desc())
        .first()
    )
    if not challenge or challenge.expires_at <= now or challenge.attempts >= OTP_MAX_ATTEMPTS:
        if challenge and not challenge.consumed:
            challenge.consumed = True
            db.commit()
        raise HTTPException(status_code=400, detail="Request a new email verification code.")

    challenge.consumed = True
    org = Organization(name=payload.organization_name)
    db.add(org)
    db.flush()  # get org.id without a separate commit

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=RoleEnum.admin,  # first user of a new org is the admin
        organization_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, extra_claims={"org_id": user.organization_id, "role": user.role.value})
    return TokenResponse(access_token=token, user=_to_user_out(user))


@router.post("/register/otp/verify")
def verify_registration_otp(payload: RegistrationOTPVerifyRequest, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    challenge = (
        db.query(RegistrationOTPChallenge)
        .filter(
            RegistrationOTPChallenge.email == payload.email,
            RegistrationOTPChallenge.consumed.is_(False),
        )
        .order_by(RegistrationOTPChallenge.created_at.desc())
        .first()
    )
    if not challenge or challenge.expires_at <= now or challenge.attempts >= OTP_MAX_ATTEMPTS:
        if challenge and not challenge.consumed:
            challenge.consumed = True
            db.commit()
        raise HTTPException(status_code=400, detail="Request a new email verification code.")

    expected = _login_code_hash(challenge.id, payload.code)
    if not hmac.compare_digest(challenge.code_hash, expected):
        challenge.attempts += 1
        if challenge.attempts >= OTP_MAX_ATTEMPTS:
            challenge.consumed = True
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid email verification code.")

    challenge.verified = True
    db.commit()
    return {"detail": "Email verified. You can now create your workspace."}


@router.post("/register/otp/request")
def request_registration_otp(payload: RegistrationOTPRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    _require_email_delivery(settings)

    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        return {"detail": REGISTRATION_OTP_MESSAGE}

    now = datetime.utcnow()
    recent = (
        db.query(RegistrationOTPChallenge)
        .filter(RegistrationOTPChallenge.email == payload.email)
        .order_by(RegistrationOTPChallenge.created_at.desc())
        .first()
    )
    if recent and recent.created_at > now - timedelta(seconds=settings.LOGIN_OTP_RESEND_SECONDS):
        raise HTTPException(status_code=429, detail="Please wait before requesting another verification code.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    db.query(RegistrationOTPChallenge).filter(
        RegistrationOTPChallenge.email == payload.email,
        RegistrationOTPChallenge.consumed.is_(False),
    ).update({"consumed": True}, synchronize_session=False)
    challenge = RegistrationOTPChallenge(
        email=payload.email,
        code_hash="",
        expires_at=now + timedelta(minutes=settings.LOGIN_OTP_EXPIRE_MINUTES),
    )
    db.add(challenge)
    db.flush()
    challenge.code_hash = _login_code_hash(challenge.id, code)
    db.commit()

    try:
        send_login_code(payload.email, code)
    except (OSError, RuntimeError, smtplib.SMTPException) as exc:
        logger.error("Could not deliver registration verification code: %s", exc)
        db.delete(challenge)
        db.commit()
        raise HTTPException(status_code=503, detail="Could not send the verification code. Please try again later.") from exc

    return {"detail": REGISTRATION_OTP_MESSAGE}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated.")

    token = create_access_token(subject=user.id, extra_claims={"org_id": user.organization_id, "role": user.role.value})
    return TokenResponse(access_token=token, user=_to_user_out(user))


def _login_code_hash(challenge_id: str, code: str) -> str:
    secret = get_settings().JWT_SECRET_KEY.encode("utf-8")
    message = f"{challenge_id}:{code}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


@router.post("/login/otp/request")
def request_login_otp(payload: LoginOTPRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    _require_email_delivery(settings)

    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.is_active:
        return {"detail": OTP_REQUEST_MESSAGE}

    now = datetime.utcnow()
    recent = (
        db.query(LoginOTPChallenge)
        .filter(LoginOTPChallenge.user_id == user.id)
        .order_by(LoginOTPChallenge.created_at.desc())
        .first()
    )
    if recent and recent.created_at > now - timedelta(seconds=settings.LOGIN_OTP_RESEND_SECONDS):
        return {"detail": OTP_REQUEST_MESSAGE}

    code = f"{secrets.randbelow(1_000_000):06d}"
    db.query(LoginOTPChallenge).filter(
        LoginOTPChallenge.user_id == user.id,
        LoginOTPChallenge.consumed.is_(False),
    ).update({"consumed": True}, synchronize_session=False)
    challenge = LoginOTPChallenge(
        user_id=user.id,
        code_hash="",
        expires_at=now + timedelta(minutes=settings.LOGIN_OTP_EXPIRE_MINUTES),
    )
    db.add(challenge)
    db.flush()
    challenge.code_hash = _login_code_hash(challenge.id, code)
    db.commit()

    try:
        send_login_code(user.email, code)
    except (OSError, RuntimeError, smtplib.SMTPException) as exc:
        logger.error("Could not deliver login code: %s", exc)
        db.delete(challenge)
        db.commit()
        raise HTTPException(status_code=503, detail="Could not send the sign-in code. Please try again later.") from exc

    return {"detail": OTP_REQUEST_MESSAGE}


@router.post("/login/otp/verify", response_model=TokenResponse)
def verify_login_otp(payload: LoginOTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired sign-in code.")

    now = datetime.utcnow()
    challenge = (
        db.query(LoginOTPChallenge)
        .filter(
            LoginOTPChallenge.user_id == user.id,
            LoginOTPChallenge.consumed.is_(False),
        )
        .order_by(LoginOTPChallenge.created_at.desc())
        .first()
    )
    if not challenge or challenge.expires_at <= now or challenge.attempts >= OTP_MAX_ATTEMPTS:
        if challenge and not challenge.consumed:
            challenge.consumed = True
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid or expired sign-in code.")

    expected = _login_code_hash(challenge.id, payload.code)
    if not hmac.compare_digest(challenge.code_hash, expected):
        challenge.attempts += 1
        if challenge.attempts >= OTP_MAX_ATTEMPTS:
            challenge.consumed = True
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid or expired sign-in code.")

    challenge.consumed = True
    db.commit()
    token = create_access_token(subject=user.id, extra_claims={"org_id": user.organization_id, "role": user.role.value})
    return TokenResponse(access_token=token, user=_to_user_out(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _to_user_out(current_user)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    if verify_password(payload.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Choose a new password that you have not used before.")

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"detail": "Password changed successfully."}


@router.post("/logout")
def logout():
    # JWTs are stateless; logout is handled client-side by discarding the
    # token. This endpoint exists so the frontend has a clean call to make
    # (and is the natural place to add token blacklisting later).
    return {"detail": "Logged out. Discard the access token on the client."}
