"""
AI Analyst Agent.

Workflow: USER QUESTION -> LLM interprets intent -> selects a tool ->
tool queries/analyzes the real dataframe -> result returned to LLM ->
LLM explains the result in plain English -> final answer.

If no LLM is configured (or the call fails), a lightweight keyword
router picks the most relevant tool itself and returns an evidence-backed
templated answer, so "Ask AI Analyst" always works.
"""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from app.ai.llm_client import get_llm_client
from app.agents.tools import TOOL_SCHEMAS, execute_tool

AGENT_SYSTEM_PROMPT = """You are an AI Analyst embedded in a growth-intelligence
product. Answer the user's question about their business data by calling
the appropriate tool(s) to fetch real, calculated numbers - never invent a
metric yourself. After you have the tool result, explain it in plain,
concise English (3-6 sentences), citing the actual numbers returned. If the
tool result shows insufficient data, say "Insufficient data to determine
this" rather than guessing.
"""

KEYWORD_TOOL_MAP = [
    (["funnel", "drop off", "drop-off", "biggest drop"], "analyze_funnel"),
    (["segment", "at risk", "highly engaged", "converted users"], "analyze_segments"),
    (["source", "channel", "campaign", "which lead source"], "get_top_sources"),
    (["revenue", "money", "arpu", "pricing"], "analyze_revenue"),
    (["anomaly", "anomalies", "spike", "drop", "unusual"], "detect_anomalies"),
    (["compare", "last month", "this month", "period", "vs previous"], "compare_periods"),
    (["experiment", "test next", "what should we test", "a/b test"], "generate_experiment"),
    (["kpi", "conversion", "activation rate", "how is", "performance"], "query_kpis"),
]


def _route_by_keyword(question: str) -> str:
    q = question.lower()
    for keywords, tool in KEYWORD_TOOL_MAP:
        if any(k in q for k in keywords):
            return tool
    return "query_kpis"


def _rule_based_answer(tool_name: str, result: Dict[str, Any]) -> str:
    if tool_name == "analyze_funnel":
        biggest = result.get("biggest_drop_off")
        overall = result.get("overall_conversion_rate")
        if not biggest:
            return "Insufficient data to determine funnel performance."
        return (
            f"The biggest drop-off is between {biggest['from_stage']} and {biggest['to_stage']} "
            f"at {biggest['drop_off_from_previous']}%. Overall conversion rate from the top of the "
            f"funnel is {overall}%."
        )
    if tool_name == "analyze_segments":
        segments = result.get("segments", [])
        if not segments:
            return "Insufficient data to determine segments."
        top = max(segments, key=lambda s: s.get("total_revenue") or 0)
        return (
            f"There are {len(segments)} segments. '{top['name']}' generates the most revenue "
            f"(${top.get('total_revenue', 0):,.0f}) across {top['size']} leads, with a "
            f"{top.get('conversion_rate', 0)}% conversion rate."
        )
    if tool_name == "get_top_sources":
        sources = result.get("sources", [])
        if not sources:
            return "Insufficient data to determine source performance."
        best = sources[0]
        return (
            f"'{best['source']}' is the best-performing source with a {best['conversion_rate']}% "
            f"conversion rate across {best['leads']} leads and ${best.get('revenue', 0):,.0f} in revenue."
        )
    if tool_name == "analyze_revenue":
        total = result.get("total_revenue")
        if total is None:
            return "Insufficient data to determine revenue."
        return (
            f"Total revenue is ${total:,.0f}, averaging ${result.get('avg_revenue_per_customer', 0):,.0f} "
            f"per paying customer."
        )
    if tool_name == "detect_anomalies":
        anomalies = result.get("anomalies", [])
        if not anomalies:
            return "No statistically significant anomalies were detected in the current data."
        a = anomalies[0]
        return f"The most notable anomaly: {a['possible_explanation']}"
    if tool_name == "compare_periods":
        cur, prev, pct = result.get("current_period_total"), result.get("previous_period_total"), result.get("pct_change")
        if pct is None:
            return "Insufficient data to compare periods."
        direction = "up" if pct >= 0 else "down"
        return f"{result.get('metric', 'This metric').title()} is {direction} {abs(pct)}% ({prev} -> {cur})."
    if tool_name == "generate_experiment":
        exp = result.get("experiment")
        if not exp:
            return "Insufficient data to determine this."
        return f"Hypothesis: {exp['hypothesis']} Experiment: {exp['experiment']} Primary KPI: {exp['primary_kpi']}."
    if tool_name == "query_kpis":
        kpis = result.get("kpis", {})
        return (
            f"Leads: {kpis.get('leads')}, overall conversion: {kpis.get('overall_conversion')}%, "
            f"revenue: ${kpis.get('revenue', 0):,.0f}."
        )
    return "Insufficient data to determine this."


def ask_agent(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    llm = get_llm_client()

    def tool_executor(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        return execute_tool(df, name, args)

    llm_result = llm.complete_with_tools(AGENT_SYSTEM_PROMPT, question, TOOL_SCHEMAS, tool_executor)
    if llm_result:
        return {
            "answer": llm_result["answer"],
            "tool_used": llm_result.get("tool_used"),
            "evidence": llm_result.get("evidence", {}),
            "source": "llm",
        }

    # Fallback: keyword-routed tool + templated explanation
    tool_name = _route_by_keyword(question)
    result = execute_tool(df, tool_name, {})
    answer = _rule_based_answer(tool_name, result)
    return {"answer": answer, "tool_used": tool_name, "evidence": result, "source": "rule_based"}
