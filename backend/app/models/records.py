from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class LeadRecord(Base, UUIDMixin, TimestampMixin):
    """A single normalized lead/customer row belonging to a dataset.

    Holds the canonical fields from the expected schema. Any field the
    source dataset didn't provide is simply left NULL - the rest of the
    pipeline is written to tolerate missing optional fields.
    """
    __tablename__ = "leads"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)

    source_lead_id = Column(String(255), nullable=True, index=True)
    source_customer_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)

    signup_date = Column(DateTime, nullable=True, index=True)
    source = Column(String(120), nullable=True, index=True)
    campaign = Column(String(120), nullable=True)
    industry = Column(String(120), nullable=True)
    country = Column(String(120), nullable=True)
    company_size = Column(String(60), nullable=True)
    product = Column(String(120), nullable=True)
    plan = Column(String(60), nullable=True, index=True)

    trial_start = Column(DateTime, nullable=True)
    activation_date = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)

    revenue = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=True)
    number_of_sessions = Column(Integer, nullable=True)
    pages_viewed = Column(Integer, nullable=True)
    emails_opened = Column(Integer, nullable=True)
    support_tickets = Column(Integer, nullable=True)
    churn = Column(Boolean, nullable=True)
    status = Column(String(60), nullable=True, index=True)

    # --- engineered features (computed, not raw input) ---
    days_signup_to_activation = Column(Float, nullable=True)
    days_signup_to_payment = Column(Float, nullable=True)
    trial_duration_days = Column(Float, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    is_converted = Column(Boolean, nullable=True)
    lead_age_days = Column(Float, nullable=True)
    funnel_completion_pct = Column(Float, nullable=True)
    activity_frequency = Column(Float, nullable=True)

    segment = Column(String(60), nullable=True, index=True)

    extra = Column(JSON, default=dict)  # any unmapped columns preserved here


class Event(Base, UUIDMixin, TimestampMixin):
    """Optional granular event stream (page view, email open, etc.)."""
    __tablename__ = "events"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=True, index=True)
    event_type = Column(String(120), nullable=False, index=True)
    event_time = Column(DateTime, nullable=True, index=True)
    properties = Column(JSON, default=dict)
