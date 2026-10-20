from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSON, DateTime

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class FunnelStage(Base, UUIDMixin, TimestampMixin):
    """Configurable funnel stage definition + computed counts for a run."""
    __tablename__ = "funnel_stages"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    order_index = Column(Integer, nullable=False)
    user_count = Column(Integer, default=0)
    conversion_from_previous = Column(Float, nullable=True)
    drop_off_from_previous = Column(Float, nullable=True)
    conversion_from_start = Column(Float, nullable=True)


class Segment(Base, UUIDMixin, TimestampMixin):
    """A named lead/customer segment computed for a dataset."""
    __tablename__ = "segments"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)
    method = Column(String(40), default="rule_based")  # rule_based | kmeans
    size = Column(Integer, default=0)
    conversion_rate = Column(Float, nullable=True)
    avg_revenue = Column(Float, nullable=True)
    total_revenue = Column(Float, nullable=True)
    avg_engagement = Column(Float, nullable=True)
    characteristics = Column(JSON, default=dict)


class KPISnapshot(Base, UUIDMixin, TimestampMixin):
    """A calculated KPI value for a dataset, optionally scoped to filters
    (date range, source, campaign, etc.) and time bucket for trend charts."""
    __tablename__ = "kpis"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    metric_name = Column(String(120), nullable=False, index=True)
    value = Column(Float, nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    filters = Column(JSON, default=dict)
