"""
Tools the AI Analyst Agent can call. Each tool takes a pandas DataFrame
(the cleaned+engineered dataset already loaded by the caller) plus
optional args, and returns a small structured JSON-serializable dict.

The LLM never queries the database directly and never invents numbers -
it can only call these functions and reason over what they return.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from app.analytics.kpis import compute_kpis, apply_filters
from app.analytics.funnel import compute_funnel
from app.analytics.segmentation import assign_rule_based_segments, summarize_segments
from app.analytics.trends import build_all_trends, build_time_series
from app.analytics.anomalies import detect_all_anomalies


def query_kpis(df: pd.DataFrame, source: Optional[str] = None, plan: Optional[str] = None, **_) -> Dict[str, Any]:
    filtered = apply_filters(df, source=source, plan=plan)
    return {"tool": "query_kpis", "filters": {"source": source, "plan": plan}, "kpis": compute_kpis(filtered)}


def analyze_funnel(df: pd.DataFrame, **_) -> Dict[str, Any]:
    result = compute_funnel(df)
    return {"tool": "analyze_funnel", **result}


def analyze_segments(df: pd.DataFrame, **_) -> Dict[str, Any]:
    working = df.copy()
    if "segment" not in working.columns or working["segment"].isna().all():
        working["segment"] = assign_rule_based_segments(working)
    return {"tool": "analyze_segments", "segments": summarize_segments(working)}


def compare_periods(df: pd.DataFrame, metric: str = "revenue", days: int = 30, **_) -> Dict[str, Any]:
    series = build_time_series(df, metric=metric, days=days)
    return {"tool": "compare_periods", "metric": metric, **series}


def analyze_revenue(df: pd.DataFrame, **_) -> Dict[str, Any]:
    kpis = compute_kpis(df)
    by_source = {}
    if "source" in df.columns and "revenue" in df.columns:
        by_source = df.groupby("source")["revenue"].sum().sort_values(ascending=False).round(2).to_dict()
    return {
        "tool": "analyze_revenue",
        "total_revenue": kpis.get("revenue"),
        "avg_revenue_per_customer": kpis.get("avg_revenue_per_customer"),
        "revenue_by_source": by_source,
    }


def detect_anomalies(df: pd.DataFrame, days: int = 60, **_) -> Dict[str, Any]:
    trends = build_all_trends(df, days=days)
    return {"tool": "detect_anomalies", "anomalies": detect_all_anomalies(trends)}


def get_top_sources(df: pd.DataFrame, top_n: int = 5, **_) -> Dict[str, Any]:
    if "source" not in df.columns:
        return {"tool": "get_top_sources", "sources": []}
    working = df.copy()
    if "is_converted" not in working.columns:
        working["is_converted"] = working.get("payment_date").notna() if "payment_date" in working else False
    grouped = working.groupby("source").agg(
        leads=("source", "count"),
        conversions=("is_converted", "sum"),
        revenue=("revenue", "sum") if "revenue" in working.columns else ("source", "count"),
    ).reset_index()
    grouped["conversion_rate"] = (grouped["conversions"] / grouped["leads"] * 100).round(2)
    grouped = grouped.sort_values("conversion_rate", ascending=False).head(top_n)
    return {"tool": "get_top_sources", "sources": grouped.round(2).to_dict(orient="records")}


def generate_experiment(df: pd.DataFrame, focus_area: Optional[str] = None, **_) -> Dict[str, Any]:
    """Deterministic experiment suggestion grounded in the funnel's
    biggest drop-off, used as a tool result the LLM can cite/explain."""
    funnel = compute_funnel(df)
    biggest = funnel.get("biggest_drop_off")
    if not biggest:
        return {"tool": "generate_experiment", "experiment": None, "note": "Insufficient data to determine this."}
    return {
        "tool": "generate_experiment",
        "experiment": {
            "hypothesis": f"Reducing friction at the {biggest['to_stage']} step may reduce drop-off from {biggest['from_stage']}.",
            "experiment": f"A/B test a simplified {biggest['to_stage']} flow against the current one.",
            "primary_kpi": f"{biggest['to_stage']} conversion rate",
            "expected_direction": "increase",
            "focus_area": focus_area or biggest["to_stage"],
        },
    }


TOOL_REGISTRY = {
    "query_kpis": query_kpis,
    "analyze_funnel": analyze_funnel,
    "analyze_segments": analyze_segments,
    "compare_periods": compare_periods,
    "analyze_revenue": analyze_revenue,
    "detect_anomalies": detect_anomalies,
    "get_top_sources": get_top_sources,
    "generate_experiment": generate_experiment,
}

# OpenAI function-calling tool schemas
TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "query_kpis", "description": "Get calculated KPIs (leads, conversion, revenue, etc.), optionally filtered by source or plan.",
        "parameters": {"type": "object", "properties": {
            "source": {"type": "string", "description": "Filter by lead source, e.g. 'google'"},
            "plan": {"type": "string", "description": "Filter by plan name"},
        }}}},
    {"type": "function", "function": {
        "name": "analyze_funnel", "description": "Get the conversion funnel stages, counts, conversion rates, and the biggest drop-off.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "analyze_segments", "description": "Get lead/customer segments with size, conversion rate, and revenue per segment.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "compare_periods", "description": "Compare a metric (leads, signups, conversions, revenue, engagement) over the current vs previous period.",
        "parameters": {"type": "object", "properties": {
            "metric": {"type": "string", "enum": ["leads", "signups", "conversions", "revenue", "engagement"]},
            "days": {"type": "integer", "description": "Period length in days, default 30"},
        }, "required": ["metric"]}}},
    {"type": "function", "function": {
        "name": "analyze_revenue", "description": "Get total revenue, average revenue per customer, and revenue broken down by source.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "detect_anomalies", "description": "Get statistically detected anomalies (unusual spikes/drops) in key metrics.",
        "parameters": {"type": "object", "properties": {
            "days": {"type": "integer", "description": "Lookback window in days, default 60"},
        }}}},
    {"type": "function", "function": {
        "name": "get_top_sources", "description": "Get the best-performing lead sources ranked by conversion rate.",
        "parameters": {"type": "object", "properties": {
            "top_n": {"type": "integer", "description": "How many sources to return, default 5"},
        }}}},
    {"type": "function", "function": {
        "name": "generate_experiment", "description": "Generate a growth experiment idea grounded in the current funnel data.",
        "parameters": {"type": "object", "properties": {
            "focus_area": {"type": "string", "description": "Optional area to focus the experiment on"},
        }}}},
]


def execute_tool(df: pd.DataFrame, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    fn = TOOL_REGISTRY.get(name)
    if not fn:
        return {"error": f"Unknown tool '{name}'"}
    return fn(df, **args)
