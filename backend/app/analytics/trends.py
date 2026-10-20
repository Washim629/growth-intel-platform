"""Time-series analytics: metric-over-time series + period comparisons."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

METRIC_DATE_COL = {
    "leads": "signup_date",
    "signups": "signup_date",
    "conversions": "payment_date",
    "revenue": "payment_date",
    "engagement": "signup_date",
}


def _bucket(series: pd.Series, granularity: str) -> pd.Series:
    freq = {"day": "D", "week": "W", "month": "M"}.get(granularity, "D")
    return series.dt.to_period(freq).dt.start_time


def build_time_series(
    df: pd.DataFrame,
    metric: str,
    granularity: str = "day",
    days: int = 30,
) -> Dict:
    date_col = METRIC_DATE_COL.get(metric, "signup_date")
    if date_col not in df.columns:
        return {"metric": metric, "points": [], "current_period_total": 0.0, "previous_period_total": 0.0, "pct_change": None}

    now = df[date_col].max() if df[date_col].notna().any() else pd.Timestamp.utcnow()
    period_start = now - pd.Timedelta(days=days)
    prev_period_start = period_start - pd.Timedelta(days=days)

    working = df.copy()
    working = working[working[date_col].notna()]
    if working.empty:
        return {"metric": metric, "points": [], "current_period_total": 0.0, "previous_period_total": 0.0, "pct_change": None}

    if metric == "revenue":
        working["_value"] = working.get("revenue", 0).fillna(0)
    elif metric == "engagement":
        working["_value"] = working.get("engagement_rate", 0).fillna(0)
    else:
        working["_value"] = 1  # count of rows (leads/signups/conversions)

    current = working[(working[date_col] > period_start) & (working[date_col] <= now)]
    previous = working[(working[date_col] > prev_period_start) & (working[date_col] <= period_start)]

    current_total = float(current["_value"].sum())
    previous_total = float(previous["_value"].sum())
    pct_change = None
    if previous_total > 0:
        pct_change = round((current_total - previous_total) / previous_total * 100, 2)
    elif current_total > 0:
        pct_change = 100.0

    current = current.copy()
    current["_bucket"] = _bucket(current[date_col], granularity)
    agg = current.groupby("_bucket")["_value"].sum().reset_index().sort_values("_bucket")
    points = [{"period": row["_bucket"].strftime("%Y-%m-%d"), "value": round(float(row["_value"]), 2)} for _, row in agg.iterrows()]

    return {
        "metric": metric,
        "points": points,
        "current_period_total": round(current_total, 2),
        "previous_period_total": round(previous_total, 2),
        "pct_change": pct_change,
    }


def build_all_trends(df: pd.DataFrame, granularity: str = "day", days: int = 30) -> List[Dict]:
    return [build_time_series(df, m, granularity, days) for m in ["leads", "signups", "conversions", "revenue", "engagement"]]
