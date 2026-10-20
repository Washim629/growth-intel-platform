from typing import Optional
from pydantic import BaseModel


class ExperimentCreate(BaseModel):
    name: str
    problem: Optional[str] = None
    hypothesis: Optional[str] = None
    target_segment: Optional[str] = None
    proposed_change: Optional[str] = None
    primary_kpi: Optional[str] = None
    secondary_kpi: Optional[str] = None
    expected_impact: Optional[str] = None
    priority: Optional[str] = "medium"
    reason: Optional[str] = None
    success_criteria: Optional[str] = None
    dataset_id: Optional[str] = None


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    problem: Optional[str] = None
    hypothesis: Optional[str] = None
    target_segment: Optional[str] = None
    proposed_change: Optional[str] = None
    primary_kpi: Optional[str] = None
    secondary_kpi: Optional[str] = None
    expected_impact: Optional[str] = None
    priority: Optional[str] = None
    reason: Optional[str] = None
    success_criteria: Optional[str] = None
    status: Optional[str] = None


class ExperimentOut(BaseModel):
    id: str
    name: str
    problem: Optional[str]
    hypothesis: Optional[str]
    target_segment: Optional[str]
    proposed_change: Optional[str]
    primary_kpi: Optional[str]
    secondary_kpi: Optional[str]
    expected_impact: Optional[str]
    priority: str
    reason: Optional[str]
    success_criteria: Optional[str]
    status: str

    class Config:
        from_attributes = True
