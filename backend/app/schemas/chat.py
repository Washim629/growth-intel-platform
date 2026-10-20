from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    dataset_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    tool_used: Optional[str] = None
    evidence: Dict[str, Any] = {}
    source: str = "rule_based"  # rule_based | llm


class InsightsRequest(BaseModel):
    dataset_id: str


class InsightsResponse(BaseModel):
    executive_summary: str
    key_findings: List[str]
    problems: List[str]
    opportunities: List[str]
    recommended_actions: List[str]
    experiment_ideas: List[Dict[str, str]]
    source: str
