from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import FunnelResponse, FunnelStageOut
from app.services.dataset_query import load_lead_dataframe
from app.analytics.funnel import compute_funnel
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/funnel", tags=["funnel"])


@router.get("/{dataset_id}", response_model=FunnelResponse)
def get_funnel(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_dataset(db, dataset_id, current_user)
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    result = compute_funnel(df)
    return FunnelResponse(
        dataset_id=dataset_id,
        stages=[FunnelStageOut(**s) for s in result["stages"]],
        biggest_drop_off=result["biggest_drop_off"],
        overall_conversion_rate=result["overall_conversion_rate"],
    )
