from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.ai import AIInsight
from app.schemas.chat import InsightsRequest, InsightsResponse, ChatRequest, ChatResponse
from app.services.dataset_query import load_lead_dataframe
from app.analytics.kpis import compute_kpis
from app.analytics.funnel import compute_funnel
from app.analytics.segmentation import assign_rule_based_segments, summarize_segments
from app.analytics.trends import build_all_trends
from app.analytics.anomalies import detect_all_anomalies
from app.ai.context_builder import build_analysis_context
from app.ai.insights import generate_ai_insights
from app.agents.agent import ask_agent
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _build_context_for_dataset(db: Session, dataset_id: str):
    from app.models.dataset import Dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    df = df.copy()
    df["segment"] = assign_rule_based_segments(df)
    kpis = compute_kpis(df)
    funnel = compute_funnel(df)
    segments = summarize_segments(df)
    trends = build_all_trends(df, days=90)
    anomalies = detect_all_anomalies(trends)
    quality = dataset.data_quality_report if dataset else {}

    context = build_analysis_context(kpis, funnel, segments, trends, anomalies, quality)
    return context, df


@router.post("/insights/{dataset_id}", response_model=InsightsResponse)
def generate_insights(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_dataset(db, dataset_id, current_user)
    context, _ = _build_context_for_dataset(db, dataset_id)
    result = generate_ai_insights(context)

    insight = AIInsight(
        dataset_id=dataset_id,
        executive_summary=result.get("executive_summary"),
        key_findings=result.get("key_findings", []),
        problems=result.get("problems", []),
        opportunities=result.get("opportunities", []),
        recommended_actions=result.get("recommended_actions", []),
        experiment_ideas=result.get("experiment_ideas", []),
        source=result.get("source", "rule_based"),
        raw_context=context,
    )
    db.add(insight)
    db.commit()

    return InsightsResponse(
        executive_summary=result.get("executive_summary", ""),
        key_findings=result.get("key_findings", []),
        problems=result.get("problems", []),
        opportunities=result.get("opportunities", []),
        recommended_actions=result.get("recommended_actions", []),
        experiment_ideas=result.get("experiment_ideas", []),
        source=result.get("source", "rule_based"),
    )


@router.get("/insights/{dataset_id}/latest", response_model=InsightsResponse)
def get_latest_insights(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_dataset(db, dataset_id, current_user)
    insight = (
        db.query(AIInsight)
        .filter(AIInsight.dataset_id == dataset_id)
        .order_by(AIInsight.created_at.desc())
        .first()
    )
    if not insight:
        raise HTTPException(status_code=404, detail="No AI insights generated yet for this dataset.")
    return InsightsResponse(
        executive_summary=insight.executive_summary or "",
        key_findings=insight.key_findings or [],
        problems=insight.problems or [],
        opportunities=insight.opportunities or [],
        recommended_actions=insight.recommended_actions or [],
        experiment_ideas=insight.experiment_ideas or [],
        source=insight.source,
    )


@router.post("/chat", response_model=ChatResponse)
def chat_with_analyst(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_dataset(db, payload.dataset_id, current_user)
    df = load_lead_dataframe(db, payload.dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    result = ask_agent(df, payload.question)
    return ChatResponse(**result)
