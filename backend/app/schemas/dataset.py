from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: str
    filename: str
    file_type: str
    row_count: int
    column_names: List[str]
    column_mapping: Dict[str, Any]
    status: str
    data_quality_report: Dict[str, Any]
    created_at: str

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    dataset_id: str
    columns: List[str]
    sample_rows: List[Dict[str, Any]]
    suggested_mapping: Dict[str, Optional[str]]
    detected_dtypes: Dict[str, str]
    missing_value_pct: Dict[str, float]
    duplicate_row_count: int
    total_rows: int


class ColumnMappingRequest(BaseModel):
    mapping: Dict[str, str]  # source_column -> canonical_field ("lead_id", "revenue", ...)


class AnalysisRunOut(BaseModel):
    id: str
    dataset_id: str
    status: str
    progress: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
