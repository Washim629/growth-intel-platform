from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import AnomalyResponse, AnomalyOut
from app.services.dataset_query import load_lead_dataframe
from app.analytics.trends import build_all_trends
from app.analytics.anomalies import detect_all_anomalies
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("/{dataset_id}", response_model=AnomalyResponse)
def get_anomalies(dataset_id: str, days: int = 90, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_dataset(db, dataset_id, current_user)
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    trends = build_all_trends(df, days=days)
    anomalies = detect_all_anomalies(trends)
    return AnomalyResponse(dataset_id=dataset_id, anomalies=[AnomalyOut(**a) for a in anomalies])
