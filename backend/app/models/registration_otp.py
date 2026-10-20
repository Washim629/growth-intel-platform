from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class RegistrationOTPChallenge(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "registration_otp_challenges"

    email = Column(String(255), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    verified = Column(Boolean, nullable=False, default=False)
    consumed = Column(Boolean, nullable=False, default=False)
