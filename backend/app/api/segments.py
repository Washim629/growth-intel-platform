from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import SegmentResponse, SegmentOut
from app.services.dataset_query import load_lead_dataframe
from app.analytics.segmentation import assign_rule_based_segments, summarize_segments, kmeans_segments
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/segments", tags=["segments"])


@router.get("/{dataset_id}", response_model=SegmentResponse)
def get_segments(
    dataset_id: str,
    method: str = "rule_based",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_dataset(db, dataset_id, current_user)
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    if method == "kmeans":
        try:
            df["segment"] = kmeans_segments(df)
        except (ImportError, ValueError):
            # scikit-learn missing or not enough data - fall back gracefully
            df["segment"] = assign_rule_based_segments(df)
            method = "rule_based"
    else:
        df["segment"] = assign_rule_based_segments(df)

    segments = summarize_segments(df, segment_col="segment")
    return SegmentResponse(dataset_id=dataset_id, segments=[SegmentOut(**s) for s in segments])
