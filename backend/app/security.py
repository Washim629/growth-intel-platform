"""
Password hashing + JWT issuance/verification.

Password hashing uses hashlib.pbkdf2_hmac (Python stdlib) so the app has
zero risk of a missing native dependency (e.g. bcrypt wheels) blocking
first run. It is a legitimate, salted, iterated hash suitable for this
use case. Swap in passlib[bcrypt] later if you prefer - the interface
(hash_password/verify_password) stays the same either way.
"""
import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt

from app.config import get_settings

settings = get_settings()

PBKDF2_ITERATIONS = 260_000


def hash_password(plain_password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(plain_password: str, hashed: str) -> bool:
    try:
        algo, iterations, salt_b64, hash_b64 = hashed.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def create_access_token(subject: str, extra_claims: Optional[dict] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire, "iat": datetime.utcnow()}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
