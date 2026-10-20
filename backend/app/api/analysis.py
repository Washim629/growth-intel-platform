from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.dataset import Dataset, AnalysisRun, JobStatus
from app.schemas.dataset import AnalysisRunOut
from app.workers.jobs import submit_job

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/{dataset_id}", response_model=AnalysisRunOut, status_code=202)
def start_analysis(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this dataset.")
    if not dataset.column_mapping:
        raise HTTPException(status_code=400, detail="Confirm column mapping before running analysis.")

    run = AnalysisRun(dataset_id=dataset.id, status=JobStatus.queued, progress=0)
    db.add(run)
    db.commit()
    db.refresh(run)

    submit_job(run.id)  # runs in a background thread; see app/workers/jobs.py

    return AnalysisRunOut(id=run.id, dataset_id=run.dataset_id, status=run.status.value, progress=run.progress)


@router.get("/{run_id}", response_model=AnalysisRunOut)
def get_analysis_status(run_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found.")
    dataset = db.query(Dataset).filter(Dataset.id == run.dataset_id).first()
    if not dataset or dataset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this analysis run.")

    return AnalysisRunOut(
        id=run.id, dataset_id=run.dataset_id, status=run.status.value,
        progress=run.progress, error_message=run.error_message,
    )
