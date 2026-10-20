from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import TrendResponse, TrendSeries, TrendPoint
from app.services.dataset_query import load_lead_dataframe
from app.analytics.trends import build_all_trends
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/{dataset_id}", response_model=TrendResponse)
def get_trends(
    dataset_id: str,
    days: int = 30,
    granularity: str = "day",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_dataset(db, dataset_id, current_user)
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    series = build_all_trends(df, granularity=granularity, days=days)
    return TrendResponse(
        dataset_id=dataset_id,
        granularity=granularity,
        series=[TrendSeries(metric=s["metric"], points=[TrendPoint(**p) for p in s["points"]],
                             current_period_total=s["current_period_total"],
                             previous_period_total=s["previous_period_total"],
                             pct_change=s["pct_change"]) for s in series],
    )
