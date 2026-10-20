"""
AI Insights Engine.

Tries the LLM first (structured JSON output over the labeled analytical
context). If no API key is configured or the call fails for any reason,
falls back to a transparent rule-based generator so the feature always
returns something useful - never a hardcoded, faked insight.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from app.ai.llm_client import get_llm_client

SYSTEM_PROMPT = """You are an AI growth analyst for a B2B SaaS company.
You will be given a JSON object of already-calculated facts (FACT) and
metrics (CALCULATION). You must reason ONLY over this data - never invent
numbers, and never present a hypothesis or recommendation as an observed
fact. If the data is insufficient to conclude something, say so plainly
("Insufficient data to determine this.").

Respond with a single JSON object with exactly these keys:
{
  "executive_summary": "2-4 sentence plain-English summary of business performance",
  "key_findings": ["short factual finding", ...],
  "problems": ["short problem statement grounded in the data", ...],
  "opportunities": ["short opportunity statement", ...],
  "recommended_actions": ["short, practical action", ...],
  "experiment_ideas": [
    {"hypothesis": "...", "experiment": "...", "metric": "...", "expected_direction": "increase|decrease"}
  ]
}
Keep each list to at most 5 items. Be specific and reference the actual
numbers from the context where relevant.
"""


def generate_ai_insights(context: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm_client()
    result = llm.complete_json(SYSTEM_PROMPT, json.dumps(context, default=str))
    if result:
        result["source"] = "llm"
        return result
    return {**generate_rule_based_insights(context), "source": "rule_based"}


def generate_rule_based_insights(context: Dict[str, Any]) -> Dict[str, Any]:
    kpis = context.get("kpis", {})
    funnel = context.get("funnel", {})
    anomalies = context.get("anomalies", {}).get("items", [])
    segments = context.get("segments", {}).get("items", [])
    trends = context.get("trends", {}).get("items", [])

    leads = kpis.get("leads") or 0
    overall_conv = kpis.get("overall_conversion")
    revenue = kpis.get("revenue")

    summary_parts = [f"The dataset contains {leads} leads/customers."]
    if overall_conv is not None:
        summary_parts.append(f"Overall conversion rate is {overall_conv}%.")
    if revenue is not None:
        summary_parts.append(f"Total tracked revenue is ${revenue:,.0f}.")
    executive_summary = " ".join(summary_parts) or "Insufficient data to determine this."

    key_findings: List[str] = []
    if kpis.get("activation_rate") is not None:
        key_findings.append(f"Activation rate is {kpis['activation_rate']}%.")
    if kpis.get("engagement_rate") is not None:
        key_findings.append(f"Average engagement rate is {kpis['engagement_rate']}%.")
    for t in trends:
        if t.get("pct_change") is not None:
            direction = "up" if t["pct_change"] >= 0 else "down"
            key_findings.append(f"{t['metric'].title()} is {direction} {abs(t['pct_change'])}% vs. the prior period.")
    if not key_findings:
        key_findings.append("Insufficient data to determine detailed trends.")

    problems: List[str] = []
    biggest_drop = funnel.get("biggest_drop_off")
    if biggest_drop:
        problems.append(
            f"{biggest_drop['from_stage']} \u2192 {biggest_drop['to_stage']} has the highest drop-off at "
            f"{biggest_drop['drop_off_from_previous']}%."
        )
    for a in anomalies[:3]:
        if a.get("severity") == "high":
            problems.append(f"High-severity anomaly detected in {a['metric']} on {a['date']} ({a['change_pct']}% change).")
    if not problems:
        problems.append("No major problems detected in the current data.")

    opportunities: List[str] = []
    if segments:
        best = max(segments, key=lambda s: (s.get("conversion_rate") or 0))
        if best.get("conversion_rate"):
            opportunities.append(
                f"The '{best['name']}' segment converts at {best['conversion_rate']}% - consider allocating more "
                f"budget toward acquiring similar leads."
            )
    if kpis.get("churn_rate"):
        opportunities.append(f"Churn rate is {kpis['churn_rate']}% - retention initiatives could recover meaningful revenue.")
    if not opportunities:
        opportunities.append("Insufficient data to determine this.")

    recommended_actions: List[str] = []
    if biggest_drop:
        recommended_actions.append(f"Investigate and reduce friction between {biggest_drop['from_stage']} and {biggest_drop['to_stage']}.")
    if kpis.get("activation_rate") is not None and kpis["activation_rate"] < 50:
        recommended_actions.append("Improve onboarding to lift activation rate, currently below 50%.")
    if not recommended_actions:
        recommended_actions.append("Continue monitoring KPIs; no urgent action indicated by current data.")

    experiment_ideas: List[Dict[str, str]] = []
    if biggest_drop:
        experiment_ideas.append({
            "hypothesis": f"Reducing friction at the {biggest_drop['to_stage']} step may reduce drop-off.",
            "experiment": f"A/B test a simplified {biggest_drop['to_stage']} flow against the current one.",
            "metric": f"{biggest_drop['to_stage']} conversion rate",
            "expected_direction": "increase",
        })
    if kpis.get("engagement_rate") is not None and kpis["engagement_rate"] < 50:
        experiment_ideas.append({
            "hypothesis": "Proactive in-app guidance may raise engagement for low-activity users.",
            "experiment": "Introduce a guided checklist for new users and measure engagement lift.",
            "metric": "Average engagement rate",
            "expected_direction": "increase",
        })
    if not experiment_ideas:
        experiment_ideas.append({
            "hypothesis": "Insufficient data to determine this.",
            "experiment": "Collect more funnel/engagement data before proposing experiments.",
            "metric": "N/A",
            "expected_direction": "N/A",
        })

    return {
        "executive_summary": executive_summary,
        "key_findings": key_findings[:5],
        "problems": problems[:5],
        "opportunities": opportunities[:5],
        "recommended_actions": recommended_actions[:5],
        "experiment_ideas": experiment_ideas[:5],
    }
