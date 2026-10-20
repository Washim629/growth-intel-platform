"""KPI calculation engine. Every KPI here is a real calculation over the
cleaned dataframe - nothing is hardcoded."""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

from app.analytics.funnel import get_funnel_stage_masks, has_lifecycle_status_data


def apply_filters(
    df: pd.DataFrame,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    source: Optional[str] = None,
    campaign: Optional[str] = None,
    industry: Optional[str] = None,
    country: Optional[str] = None,
    plan: Optional[str] = None,
    segment: Optional[str] = None,
) -> pd.DataFrame:
    out = df
    if date_from and "signup_date" in out:
        out = out[out["signup_date"] >= pd.to_datetime(date_from)]
    if date_to and "signup_date" in out:
        out = out[out["signup_date"] <= pd.to_datetime(date_to)]
    for col, val in [
        ("source", source), ("campaign", campaign), ("industry", industry),
        ("country", country), ("plan", plan), ("segment", segment),
    ]:
        if val and col in out.columns:
            out = out[out[col].astype(str).str.lower() == val.lower()]
    return out


def compute_kpis(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    total = len(df)
    if total == 0:
        return {k: None for k in [
            "leads", "signups", "trials", "activations", "payments",
            "activation_rate", "trial_conversion",
            "payment_conversion", "overall_conversion", "revenue",
            "avg_revenue_per_customer", "churn_rate", "engagement_rate",
        ]}

    leads = total
    stage_masks = get_funnel_stage_masks(df)
    status_data = has_lifecycle_status_data(df)

    def has_date_data(column: str) -> bool:
        return column in df and bool(df[column].notna().any())

    signups = int(stage_masks["signup"].sum()) if has_date_data("signup_date") or status_data or stage_masks["signup"].any() else None
    trials = int(stage_masks["trial"].sum()) if has_date_data("trial_start") or status_data or stage_masks["trial"].any() else None
    activations = int(stage_masks["activation"].sum()) if has_date_data("activation_date") or status_data or stage_masks["activation"].any() else None
    payments = int(stage_masks["payment"].sum()) if has_date_data("payment_date") or has_date_data("revenue") or status_data or stage_masks["payment"].any() else None
    converted = int(df["is_converted"].sum()) if "is_converted" in df else payments

    revenue_series = df["revenue"] if "revenue" in df else pd.Series(dtype=float)
    total_revenue = float(revenue_series.sum(skipna=True)) if revenue_series.notna().any() else 0.0
    paying_customers = converted or 0
    avg_rev_per_customer = round(total_revenue / paying_customers, 2) if paying_customers else 0.0

    churn_rate = None
    if "churn" in df and df["churn"].notna().any():
        churn_rate = round(float(df["churn"].fillna(False).mean() * 100), 2)

    engagement_rate = None
    if "engagement_rate" in df and df["engagement_rate"].notna().any():
        engagement_rate = round(float(df["engagement_rate"].mean() * 100), 2)

    activation_rate = round(activations / signups * 100, 2) if (signups and activations is not None) else None
    trial_conversion = round(payments / trials * 100, 2) if (trials and payments is not None) else None
    payment_conversion = round(payments / activations * 100, 2) if (activations and payments is not None) else None
    overall_conversion = round((converted or 0) / leads * 100, 2) if leads else None

    return {
        "leads": leads,
        "signups": signups,
        "trials": trials,
        "activations": activations,
        "payments": payments,
        "activation_rate": activation_rate,
        "trial_conversion": trial_conversion,
        "payment_conversion": payment_conversion,
        "overall_conversion": overall_conversion,
        "revenue": round(total_revenue, 2),
        "avg_revenue_per_customer": avg_rev_per_customer,
        "churn_rate": churn_rate,
        "engagement_rate": engagement_rate,
    }


KPI_LABELS = {
    "leads": "Total Leads",
    "signups": "Signups",
    "trials": "Trials",
    "activations": "Activations",
    "payments": "Payments",
    "activation_rate": "Activation Rate (%)",
    "trial_conversion": "Trial → Payment Conversion (%)",
    "payment_conversion": "Activation → Payment Conversion (%)",
    "overall_conversion": "Overall Conversion Rate (%)",
    "revenue": "Total Revenue ($)",
    "avg_revenue_per_customer": "Avg Revenue per Customer ($)",
    "churn_rate": "Churn Rate (%)",
    "engagement_rate": "Avg Engagement Rate (%)",
}
