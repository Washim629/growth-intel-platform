"""Modular feature engineering on a cleaned, canonical-column dataframe."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def _days_between(a: pd.Series, b: pd.Series) -> pd.Series:
    delta = (a - b).dt.total_seconds() / 86400.0
    return delta.where(delta >= 0)  # negative deltas are treated as bad data -> NaN


def engineer_features(df: pd.DataFrame, now: datetime | None = None) -> pd.DataFrame:
    now = now or datetime.utcnow()
    out = df.copy()

    for col in ["signup_date", "trial_start", "activation_date", "payment_date"]:
        if col not in out.columns:
            out[col] = pd.NaT
        elif not pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(out[col], errors="coerce")

    # Days from signup to activation / payment
    out["days_signup_to_activation"] = _days_between(out["activation_date"], out["signup_date"])
    out["days_signup_to_payment"] = _days_between(out["payment_date"], out["signup_date"])

    # Trial duration
    if "trial_start" in out.columns:
        trial_end = out["activation_date"].fillna(out["payment_date"])
        out["trial_duration_days"] = _days_between(trial_end, out["trial_start"])
    else:
        out["trial_duration_days"] = np.nan

    # Engagement rate: normalize engagement_score (0-100) to 0-1, blended with session activity
    engagement_score = out.get("engagement_score", pd.Series(np.nan, index=out.index))
    sessions = out.get("number_of_sessions", pd.Series(np.nan, index=out.index)).fillna(0)
    pages = out.get("pages_viewed", pd.Series(np.nan, index=out.index)).fillna(0)
    activity_component = np.tanh((sessions + 0.5 * pages) / 20.0)  # squashes to 0-1, diminishing returns
    out["engagement_rate"] = np.where(
        engagement_score.notna(),
        (engagement_score.fillna(0) / 100.0 * 0.7) + (activity_component * 0.3),
        activity_component,
    )
    out["engagement_rate"] = out["engagement_rate"].round(4)

    # Conversion flag + revenue-based
    out["is_converted"] = out["payment_date"].notna() | (out.get("revenue", 0).fillna(0) > 0)

    # Lead age (days since signup, or since first seen if no signup date)
    reference = out["signup_date"]
    out["lead_age_days"] = (pd.Timestamp(now) - reference).dt.total_seconds() / 86400.0
    out["lead_age_days"] = out["lead_age_days"].clip(lower=0)

    # Funnel completion percentage: fraction of the 4 canonical stages reached
    stage_cols = ["signup_date", "trial_start", "activation_date", "payment_date"]
    present = [c for c in stage_cols if c in out.columns]
    reached = sum(out[c].notna().astype(int) for c in present) if present else pd.Series(0, index=out.index)
    out["funnel_completion_pct"] = (reached / max(len(present), 1) * 100).round(1)

    # Activity frequency: sessions per day since signup (guard divide-by-zero)
    denom = out["lead_age_days"].replace(0, np.nan)
    out["activity_frequency"] = (sessions / denom).round(4)
    out["activity_frequency"] = out["activity_frequency"].replace([np.inf, -np.inf], np.nan)

    return out
