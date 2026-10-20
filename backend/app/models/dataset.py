import enum

from sqlalchemy import Column, String, ForeignKey, Enum, Integer, Text, JSON
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class DatasetStatus(str, enum.Enum):
    uploaded = "uploaded"
    mapped = "mapped"
    cleaned = "cleaned"
    analyzed = "analyzed"
    failed = "failed"


class JobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Dataset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "datasets"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    filename = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv | xlsx
    row_count = Column(Integer, default=0)
    column_names = Column(JSON, default=list)
    column_mapping = Column(JSON, default=dict)   # source_col -> canonical field
    status = Column(Enum(DatasetStatus), default=DatasetStatus.uploaded, nullable=False)
    data_quality_report = Column(JSON, default=dict)
    storage_path = Column(String(1000), nullable=False)  # raw uploaded file
    cleaned_storage_path = Column(String(1000), nullable=True)  # cleaned parquet/csv

    organization = relationship("Organization", back_populates="datasets")
    analysis_runs = relationship("AnalysisRun", back_populates="dataset", cascade="all, delete-orphan")


class AnalysisRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analysis_runs"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.queued, nullable=False)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_summary = Column(JSON, default=dict)  # cached KPI/funnel/segment/anomaly summary

    dataset = relationship("Dataset", back_populates="analysis_runs")
