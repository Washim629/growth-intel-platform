import io
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.models.ai import Report, AIInsight, Experiment
from app.schemas.report import ReportCreateRequest, ReportOut
from app.services.dataset_query import load_lead_dataframe
from app.analytics.kpis import compute_kpis
from app.analytics.funnel import compute_funnel
from app.analytics.segmentation import assign_rule_based_segments, summarize_segments
from app.analytics.trends import build_all_trends
from app.analytics.anomalies import detect_all_anomalies
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _build_report_content(db: Session, dataset: Dataset) -> dict:
    df = load_lead_dataframe(db, dataset.id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    df = df.copy()
    df["segment"] = assign_rule_based_segments(df)
    kpis = compute_kpis(df)
    funnel = compute_funnel(df)
    segments = summarize_segments(df)
    trends = build_all_trends(df, days=90)
    anomalies = detect_all_anomalies(trends)

    latest_insight = (
        db.query(AIInsight)
        .filter(AIInsight.dataset_id == dataset.id)
        .order_by(AIInsight.created_at.desc())
        .first()
    )
    experiments = (
        db.query(Experiment)
        .filter(Experiment.dataset_id == dataset.id)
        .order_by(Experiment.created_at.desc())
        .all()
    )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "dataset_filename": dataset.filename,
        "data_quality": dataset.data_quality_report or {},
        "kpis": kpis,
        "funnel": funnel,
        "segments": segments,
        "trends": [{"metric": t["metric"], "current_period_total": t["current_period_total"],
                     "previous_period_total": t["previous_period_total"], "pct_change": t["pct_change"]} for t in trends],
        "anomalies": anomalies,
        "ai_insights": {
            "executive_summary": latest_insight.executive_summary if latest_insight else None,
            "key_findings": latest_insight.key_findings if latest_insight else [],
            "problems": latest_insight.problems if latest_insight else [],
            "opportunities": latest_insight.opportunities if latest_insight else [],
            "recommended_actions": latest_insight.recommended_actions if latest_insight else [],
            "experiment_ideas": latest_insight.experiment_ideas if latest_insight else [],
        } if latest_insight else None,
        "experiments": [
            {"name": e.name, "status": e.status.value, "priority": e.priority.value, "hypothesis": e.hypothesis}
            for e in experiments
        ],
    }


@router.post("", response_model=ReportOut, status_code=201)
def create_report(payload: ReportCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, payload.dataset_id, current_user)
    content = _build_report_content(db, dataset)

    report = Report(
        organization_id=current_user.organization_id,
        dataset_id=dataset.id,
        title=payload.title or f"Growth Report - {dataset.filename} - {datetime.utcnow().strftime('%Y-%m-%d')}",
        content=content,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportOut(id=report.id, title=report.title, content=report.content, dataset_id=report.dataset_id)


@router.get("", response_model=List[ReportOut])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = (
        db.query(Report)
        .filter(Report.organization_id == current_user.organization_id)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [ReportOut(id=r.id, title=r.title, content=r.content, dataset_id=r.dataset_id) for r in reports]


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(db, report_id, current_user)
    return ReportOut(id=report.id, title=report.title, content=report.content, dataset_id=report.dataset_id)


@router.get("/{report_id}/export")
def export_report(
    report_id: str,
    fmt: str = "csv",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_owned_report(db, report_id, current_user)
    content = report.content or {}

    if fmt == "csv":
        import pandas as pd
        kpi_rows = [{"metric": k, "value": v} for k, v in (content.get("kpis") or {}).items()]
        buf = io.StringIO()
        pd.DataFrame(kpi_rows).to_csv(buf, index=False)
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]), media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{report.title}.csv"'},
        )

    if fmt == "xlsx":
        import pandas as pd
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            pd.DataFrame([{"metric": k, "value": v} for k, v in (content.get("kpis") or {}).items()]).to_excel(writer, sheet_name="KPIs", index=False)
            pd.DataFrame(content.get("segments") or []).to_excel(writer, sheet_name="Segments", index=False)
            pd.DataFrame((content.get("funnel") or {}).get("stages") or []).to_excel(writer, sheet_name="Funnel", index=False)
            pd.DataFrame(content.get("anomalies") or []).to_excel(writer, sheet_name="Anomalies", index=False)
        buf.seek(0)
        return StreamingResponse(
            buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{report.title}.xlsx"'},
        )

    if fmt == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(report.title, styles["Title"]), Spacer(1, 12)]

        summary = (content.get("ai_insights") or {}).get("executive_summary")
        if summary:
            story += [Paragraph("Executive Summary", styles["Heading2"]), Paragraph(summary, styles["BodyText"]), Spacer(1, 12)]

        story.append(Paragraph("KPI Overview", styles["Heading2"]))
        for k, v in (content.get("kpis") or {}).items():
            story.append(Paragraph(f"{k}: {v}", styles["BodyText"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Funnel Performance", styles["Heading2"]))
        for stage in (content.get("funnel") or {}).get("stages", []):
            story.append(Paragraph(
                f"{stage['name']}: {stage['user_count']} users "
                f"({stage.get('conversion_from_start')}% of start)", styles["BodyText"]
            ))

        doc.build(story)
        buf.seek(0)
        return StreamingResponse(
            buf, media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report.title}.pdf"'},
        )

    raise HTTPException(status_code=400, detail="fmt must be one of: csv, xlsx, pdf")


def _get_owned_report(db: Session, report_id: str, current_user: User) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this report.")
    return report
