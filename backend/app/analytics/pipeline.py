"""Runs the full DATA -> CLEAN -> FEATURES -> ANALYTICS pipeline over a
single dataset's dataframe and returns one consolidated results dict.
Used by both the upload flow and the background analysis job."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from app.analytics.cleaning import clean_dataframe
from app.analytics.features import engineer_features
from app.analytics.segmentation import assign_rule_based_segments, summarize_segments
from app.analytics.funnel import compute_funnel
from app.analytics.kpis import compute_kpis
from app.analytics.trends import build_all_trends
from app.analytics.anomalies import detect_all_anomalies


def run_full_pipeline(mapped_df: pd.DataFrame) -> Dict[str, Any]:
    """mapped_df must already have canonical column names (see
    analytics.cleaning.apply_mapping)."""
    cleaned_df, quality_report = clean_dataframe(mapped_df)

    # Analysis proceeds on non-duplicate rows only; duplicates stay
    # visible in the Data Explorer but don't skew metrics.
    analysis_df = cleaned_df[~cleaned_df["_is_duplicate"]].copy()

    featured_df = engineer_features(analysis_df)
    featured_df["segment"] = assign_rule_based_segments(featured_df)

    kpis = compute_kpis(featured_df)
    funnel = compute_funnel(featured_df)
    segments = summarize_segments(featured_df)
    trends = build_all_trends(featured_df, days=90)
    anomalies = detect_all_anomalies(trends)

    return {
        "cleaned_df": cleaned_df,       # includes _is_duplicate / _is_valid / all rows
        "featured_df": featured_df,     # analysis-ready rows only
        "quality_report": quality_report,
        "kpis": kpis,
        "funnel": funnel,
        "segments": segments,
        "trends": trends,
        "anomalies": anomalies,
    }
