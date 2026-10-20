import enum

from sqlalchemy import Column, String, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ExperimentStatus(str, enum.Enum):
    proposed = "proposed"
    planned = "planned"
    running = "running"
    completed = "completed"


class ExperimentPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AIInsight(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_insights"

    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    executive_summary = Column(Text, nullable=True)
    key_findings = Column(JSON, default=list)
    problems = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    recommended_actions = Column(JSON, default=list)
    experiment_ideas = Column(JSON, default=list)
    source = Column(String(30), default="rule_based")  # rule_based | llm
    raw_context = Column(JSON, default=dict)  # the structured facts sent to the LLM


class Experiment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "experiments"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=True, index=True)

    name = Column(String(255), nullable=False)
    problem = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    target_segment = Column(String(120), nullable=True)
    proposed_change = Column(Text, nullable=True)
    primary_kpi = Column(String(120), nullable=True)
    secondary_kpi = Column(String(120), nullable=True)
    expected_impact = Column(String(255), nullable=True)
    priority = Column(Enum(ExperimentPriority), default=ExperimentPriority.medium)
    reason = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.proposed)

    organization = relationship("Organization", back_populates="experiments")


class Report(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reports"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(JSON, default=dict)  # full structured report payload
    file_path = Column(String(1000), nullable=True)  # last exported file, if any

    organization = relationship("Organization", back_populates="reports")
