from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.models.records import LeadRecord

RECORD_COLUMNS = [
    "source_lead_id", "source_customer_id", "name", "email", "signup_date", "source",
    "campaign", "industry", "country", "company_size", "product", "plan",
    "trial_start", "activation_date", "payment_date", "revenue", "engagement_score",
    "number_of_sessions", "pages_viewed", "emails_opened", "support_tickets",
    "churn", "status", "days_signup_to_activation", "days_signup_to_payment",
    "trial_duration_days", "engagement_rate", "is_converted", "lead_age_days",
    "funnel_completion_pct", "activity_frequency", "segment",
]

RENAME_FOR_ANALYTICS = {"source_lead_id": "lead_id", "source_customer_id": "customer_id"}


def load_lead_dataframe(db: Session, dataset_id: str) -> pd.DataFrame:
    """Reload the already-cleaned, feature-engineered rows for a dataset
    from Postgres/SQLite into a DataFrame so analytics + filters can be
    (re)applied live without re-processing the raw upload."""
    columns = [getattr(LeadRecord, col) for col in RECORD_COLUMNS]
    rows = db.query(*columns).filter(LeadRecord.dataset_id == dataset_id).all()
    if not rows:
        return pd.DataFrame(columns=list(RENAME_FOR_ANALYTICS.values()) + RECORD_COLUMNS)

    df = pd.DataFrame(rows, columns=RECORD_COLUMNS).rename(columns=RENAME_FOR_ANALYTICS)

    for col in ["signup_date", "trial_start", "activation_date", "payment_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
