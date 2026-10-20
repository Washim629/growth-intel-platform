"""
Builds the structured analytical context handed to the LLM.

Per spec section 32 ("AI Reliability"), the LLM never sees raw rows and
never invents metrics - it only reasons over facts we've already
calculated. Every number here is labeled FACT or CALCULATION so the
model (and the UI) can distinguish observed data from interpretation.
"""
from __future__ import annotations

from typing import Any, Dict, List


def build_analysis_context(
    kpis: Dict[str, Any],
    funnel: Dict[str, Any],
    segments: List[Dict[str, Any]],
    trends: List[Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    data_quality: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "label": "This is the ONLY data you may reason over. Do not invent numbers.",
        "data_quality": {
            "label": "FACT",
            "total_rows": data_quality.get("total_rows"),
            "valid_rows": data_quality.get("valid_rows"),
            "data_quality_score": data_quality.get("data_quality_score"),
        },
        "kpis": {"label": "CALCULATION", **kpis},
        "funnel": {
            "label": "CALCULATION",
            "stages": funnel.get("stages", []),
            "biggest_drop_off": funnel.get("biggest_drop_off"),
            "overall_conversion_rate": funnel.get("overall_conversion_rate"),
        },
        "segments": {"label": "CALCULATION", "items": segments},
        "trends": {"label": "CALCULATION", "items": [
            {
                "metric": t["metric"],
                "current_period_total": t["current_period_total"],
                "previous_period_total": t["previous_period_total"],
                "pct_change": t["pct_change"],
            } for t in trends
        ]},
        "anomalies": {
            "label": "CALCULATION (statistical z-score outliers, not a confirmed cause)",
            "items": anomalies,
        },
    }
