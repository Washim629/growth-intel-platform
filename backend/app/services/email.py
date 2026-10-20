import smtplib
from email.message import EmailMessage

from app.config import get_settings


def send_login_code(recipient: str, code: str) -> None:
    settings = get_settings()
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        raise RuntimeError("Email delivery is not configured. Set SMTP_HOST and SMTP_FROM_EMAIL.")
    if settings.SMTP_USERNAME and not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is missing. Set the email provider's app password in the backend environment.")

    message = EmailMessage()
    message["Subject"] = "Your Growth Intel verification code"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        f"Your Growth Intel verification code is {code}.\n\n"
        f"It expires in {settings.LOGIN_OTP_EXPIRE_MINUTES} minutes. "
        "If you did not request this code, you can ignore this email."
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)
