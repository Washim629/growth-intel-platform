from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.analysis import KPIResponse, KPIItem
from app.services.dataset_query import load_lead_dataframe
from app.analytics.kpis import compute_kpis, apply_filters, KPI_LABELS
from app.api.datasets import _get_owned_dataset

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("/{dataset_id}", response_model=KPIResponse)
def get_kpis(
    dataset_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    source: Optional[str] = None,
    campaign: Optional[str] = None,
    industry: Optional[str] = None,
    country: Optional[str] = None,
    plan: Optional[str] = None,
    segment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_dataset(db, dataset_id, current_user)
    df = load_lead_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analyzed data found for this dataset yet. Run analysis first.")

    filtered = apply_filters(
        df, date_from=date_from, date_to=date_to, source=source, campaign=campaign,
        industry=industry, country=country, plan=plan, segment=segment,
    )
    kpis = compute_kpis(filtered)

    return KPIResponse(
        dataset_id=dataset_id,
        kpis=[KPIItem(metric=k, value=v, label=KPI_LABELS.get(k, k)) for k, v in kpis.items()],
        filters_applied={
            "date_from": date_from, "date_to": date_to, "source": source, "campaign": campaign,
            "industry": industry, "country": country, "plan": plan, "segment": segment,
        },
    )
