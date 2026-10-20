"""Rule-based segmentation with an optional K-Means clustering path."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def assign_rule_based_segments(df: pd.DataFrame) -> pd.Series:
    """Assign each row exactly one segment name using simple, explainable
    business rules evaluated in priority order."""

    def classify(row) -> str:
        converted = bool(row.get("is_converted"))
        engagement = row.get("engagement_rate")
        engagement = 0.0 if pd.isna(engagement) else engagement
        lead_age = row.get("lead_age_days")
        lead_age = 0 if pd.isna(lead_age) else lead_age
        has_trial = pd.notna(row.get("trial_start"))
        churn = row.get("churn")

        if converted and churn is True:
            return "At Risk"
        if converted:
            return "Converted"
        if has_trial and not converted:
            if lead_age > 30:
                return "Dormant Users"
            return "Trial Users"
        if engagement >= 0.66:
            return "Highly Engaged"
        if engagement >= 0.4:
            return "High Intent"
        if engagement >= 0.2:
            return "Medium Intent"
        if lead_age > 60:
            return "Dormant Users"
        return "Low Intent"

    return df.apply(classify, axis=1)


def summarize_segments(df: pd.DataFrame, segment_col: str = "segment") -> List[Dict]:
    summaries = []
    for name, group in df.groupby(segment_col):
        size = len(group)
        conv_rate = float(group["is_converted"].mean() * 100) if "is_converted" in group else None
        avg_revenue = float(group["revenue"].mean()) if "revenue" in group and group["revenue"].notna().any() else None
        total_revenue = float(group["revenue"].sum()) if "revenue" in group and group["revenue"].notna().any() else None
        avg_engagement = float(group["engagement_rate"].mean()) if "engagement_rate" in group else None

        top_source = None
        if "source" in group and group["source"].notna().any():
            top_source = group["source"].value_counts().idxmax()

        summaries.append({
            "name": str(name),
            "method": "rule_based",
            "size": size,
            "conversion_rate": round(conv_rate, 2) if conv_rate is not None else None,
            "avg_revenue": round(avg_revenue, 2) if avg_revenue is not None else None,
            "total_revenue": round(total_revenue, 2) if total_revenue is not None else None,
            "avg_engagement": round(avg_engagement, 4) if avg_engagement is not None else None,
            "characteristics": {
                "top_source": top_source,
                "pct_of_total": round(size / len(df) * 100, 1) if len(df) else 0,
            },
        })
    summaries.sort(key=lambda s: s["size"], reverse=True)
    return summaries


def kmeans_segments(df: pd.DataFrame, n_clusters: int = 4) -> pd.Series:
    """Optional ML-based segmentation via K-Means on engagement/revenue/
    recency/frequency features. Falls back gracefully if scikit-learn
    isn't installed or there isn't enough numeric data - callers should
    catch ImportError/ValueError and use rule-based segments instead."""
    from sklearn.cluster import KMeans  # imported lazily - optional dependency
    from sklearn.preprocessing import StandardScaler

    feature_cols = ["engagement_rate", "revenue", "lead_age_days", "activity_frequency"]
    available = [c for c in feature_cols if c in df.columns]
    if not available:
        raise ValueError("No numeric features available for clustering")

    X = df[available].fillna(0).replace([np.inf, -np.inf], 0)
    if len(X) < n_clusters:
        raise ValueError("Not enough rows for the requested number of clusters")

    X_scaled = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    return pd.Series([f"Cluster {i}" for i in labels], index=df.index)
