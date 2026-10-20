"""
Lightweight background job system.

For this initial implementation, jobs run in a background thread inside
the same process so nothing extra (Redis, Celery workers) needs to be
deployed to demo the product. The public interface - `submit_job` /
job status stored on the `AnalysisRun` row - is intentionally identical
to what a Celery-backed version would look like, so swapping the
implementation later means changing only this file:

    from celery import shared_task

    @shared_task
    def run_analysis_job(analysis_run_id): ...

and calling `run_analysis_job.delay(analysis_run_id)` instead of
`submit_job(...)`.
"""
from __future__ import annotations

import logging
import threading
import traceback

import pandas as pd

from app.database import SessionLocal
from app.models.dataset import Dataset, AnalysisRun, JobStatus, DatasetStatus
from app.models.records import LeadRecord
from app.analytics.cleaning import apply_mapping
from app.analytics.pipeline import run_full_pipeline
from app.utils.io import read_upload_dataframe

logger = logging.getLogger("app.workers")


def submit_job(analysis_run_id: str) -> None:
    thread = threading.Thread(target=_run, args=(analysis_run_id,), daemon=True)
    thread.start()


def _run(analysis_run_id: str) -> None:
    db = SessionLocal()
    try:
        run = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_run_id).first()
        if not run:
            return
        run.status = JobStatus.processing
        run.progress = 5
        db.commit()

        dataset = db.query(Dataset).filter(Dataset.id == run.dataset_id).first()
        if not dataset:
            raise ValueError("Dataset not found")

        raw_df = read_upload_dataframe(dataset.storage_path, dataset.file_type)
        run.progress = 20
        db.commit()

        mapped_df, _ = apply_mapping(raw_df, dataset.column_mapping or {})
        run.progress = 35
        db.commit()

        results = run_full_pipeline(mapped_df)
        run.progress = 70
        db.commit()

        # Persist normalized rows (replace any previous rows for this dataset)
        db.query(LeadRecord).filter(LeadRecord.dataset_id == dataset.id).delete()
        featured_df: pd.DataFrame = results["featured_df"]
        records = []
        for row in featured_df.to_dict(orient="records"):
            records.append(LeadRecord(
                dataset_id=dataset.id,
                organization_id=dataset.organization_id,
                source_lead_id=_safe_str(row.get("lead_id")),
                source_customer_id=_safe_str(row.get("customer_id")),
                name=_safe_str(row.get("name")),
                email=_safe_str(row.get("email")),
                signup_date=_safe_dt(row.get("signup_date")),
                source=_safe_str(row.get("source")),
                campaign=_safe_str(row.get("campaign")),
                industry=_safe_str(row.get("industry")),
                country=_safe_str(row.get("country")),
                company_size=_safe_str(row.get("company_size")),
                product=_safe_str(row.get("product")),
                plan=_safe_str(row.get("plan")),
                trial_start=_safe_dt(row.get("trial_start")),
                activation_date=_safe_dt(row.get("activation_date")),
                payment_date=_safe_dt(row.get("payment_date")),
                revenue=_safe_float(row.get("revenue")),
                engagement_score=_safe_float(row.get("engagement_score")),
                number_of_sessions=_safe_int(row.get("number_of_sessions")),
                pages_viewed=_safe_int(row.get("pages_viewed")),
                emails_opened=_safe_int(row.get("emails_opened")),
                support_tickets=_safe_int(row.get("support_tickets")),
                churn=bool(row.get("churn")) if pd.notna(row.get("churn")) else None,
                status=_safe_str(row.get("status")),
                days_signup_to_activation=_safe_float(row.get("days_signup_to_activation")),
                days_signup_to_payment=_safe_float(row.get("days_signup_to_payment")),
                trial_duration_days=_safe_float(row.get("trial_duration_days")),
                engagement_rate=_safe_float(row.get("engagement_rate")),
                is_converted=bool(row.get("is_converted")) if pd.notna(row.get("is_converted")) else None,
                lead_age_days=_safe_float(row.get("lead_age_days")),
                funnel_completion_pct=_safe_float(row.get("funnel_completion_pct")),
                activity_frequency=_safe_float(row.get("activity_frequency")),
                segment=_safe_str(row.get("segment")),
                extra=row.get("extra") if isinstance(row.get("extra"), dict) else {},
            ))
        db.bulk_save_objects(records)
        run.progress = 90
        db.commit()

        # Cache the consolidated summary on the run + mark dataset analyzed
        run.result_summary = {
            "kpis": results["kpis"],
            "funnel": results["funnel"],
            "segments": results["segments"],
            "trends": results["trends"],
            "anomalies": results["anomalies"],
        }
        dataset.data_quality_report = results["quality_report"]
        dataset.row_count = len(featured_df)
        dataset.status = DatasetStatus.analyzed
        run.status = JobStatus.completed
        run.progress = 100
        db.commit()

    except Exception as exc:  # noqa: BLE001
        logger.error("Analysis job %s failed: %s\n%s", analysis_run_id, exc, traceback.format_exc())
        db.rollback()
        run = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_run_id).first()
        if run:
            run.status = JobStatus.failed
            run.error_message = str(exc)
            db.commit()
        dataset = db.query(Dataset).filter(Dataset.id == run.dataset_id).first() if run else None
        if dataset:
            dataset.status = DatasetStatus.failed
            db.commit()
    finally:
        db.close()


def _safe_str(v):
    return None if pd.isna(v) else str(v)


def _safe_float(v):
    try:
        return None if pd.isna(v) else float(v)
    except (TypeError, ValueError):
        return None


def _safe_int(v):
    try:
        return None if pd.isna(v) else int(v)
    except (TypeError, ValueError):
        return None


def _safe_dt(v):
    if v is None or pd.isna(v):
        return None
    return pd.to_datetime(v).to_pydatetime()
