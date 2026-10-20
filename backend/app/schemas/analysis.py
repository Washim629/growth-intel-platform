from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class KPIItem(BaseModel):
    metric: str
    value: Optional[float]
    label: str


class KPIResponse(BaseModel):
    dataset_id: str
    kpis: List[KPIItem]
    filters_applied: Dict[str, Any]


class FunnelStageOut(BaseModel):
    name: str
    order_index: int
    user_count: int
    conversion_from_previous: Optional[float]
    drop_off_from_previous: Optional[float]
    conversion_from_start: Optional[float]


class FunnelResponse(BaseModel):
    dataset_id: str
    stages: List[FunnelStageOut]
    biggest_drop_off: Optional[Dict[str, Any]]
    overall_conversion_rate: Optional[float]


class SegmentOut(BaseModel):
    name: str
    method: str
    size: int
    conversion_rate: Optional[float]
    avg_revenue: Optional[float]
    total_revenue: Optional[float]
    avg_engagement: Optional[float]
    characteristics: Dict[str, Any]


class SegmentResponse(BaseModel):
    dataset_id: str
    segments: List[SegmentOut]


class TrendPoint(BaseModel):
    period: str
    value: float


class TrendSeries(BaseModel):
    metric: str
    points: List[TrendPoint]
    current_period_total: float
    previous_period_total: float
    pct_change: Optional[float]


class TrendResponse(BaseModel):
    dataset_id: str
    granularity: str
    series: List[TrendSeries]


class AnomalyOut(BaseModel):
    metric: str
    date: str
    severity: str
    change_pct: float
    possible_explanation: str
    value: float
    baseline: float


class AnomalyResponse(BaseModel):
    dataset_id: str
    anomalies: List[AnomalyOut]


class DataQualityReport(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_value_pct: Dict[str, float]
    duplicate_count: int
    column_dtypes: Dict[str, str]
    data_quality_score: float
    transformations: List[str]
