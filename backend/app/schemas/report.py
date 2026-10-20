from typing import Any, Dict, Optional
from pydantic import BaseModel


class ReportCreateRequest(BaseModel):
    dataset_id: str
    title: Optional[str] = None


class ReportOut(BaseModel):
    id: str
    title: str
    content: Dict[str, Any]
    dataset_id: Optional[str]

    class Config:
        from_attributes = True
