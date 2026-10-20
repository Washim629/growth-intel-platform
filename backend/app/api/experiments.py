from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.ai import Experiment, ExperimentStatus, ExperimentPriority
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentOut

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentOut, status_code=201)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        priority = ExperimentPriority(payload.priority or "medium")
    except ValueError:
        raise HTTPException(status_code=400, detail="priority must be one of: low, medium, high")

    exp = Experiment(
        organization_id=current_user.organization_id,
        dataset_id=payload.dataset_id,
        name=payload.name,
        problem=payload.problem,
        hypothesis=payload.hypothesis,
        target_segment=payload.target_segment,
        proposed_change=payload.proposed_change,
        primary_kpi=payload.primary_kpi,
        secondary_kpi=payload.secondary_kpi,
        expected_impact=payload.expected_impact,
        priority=priority,
        reason=payload.reason,
        success_criteria=payload.success_criteria,
        status=ExperimentStatus.proposed,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _out(exp)


@router.get("", response_model=List[ExperimentOut])
def list_experiments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exps = (
        db.query(Experiment)
        .filter(Experiment.organization_id == current_user.organization_id)
        .order_by(Experiment.created_at.desc())
        .all()
    )
    return [_out(e) for e in exps]


@router.patch("/{experiment_id}", response_model=ExperimentOut)
def update_experiment(experiment_id: str, payload: ExperimentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exp = _get_owned(db, experiment_id, current_user)
    data = payload.model_dump(exclude_unset=True)

    if "priority" in data and data["priority"] is not None:
        try:
            data["priority"] = ExperimentPriority(data["priority"])
        except ValueError:
            raise HTTPException(status_code=400, detail="priority must be one of: low, medium, high")
    if "status" in data and data["status"] is not None:
        try:
            data["status"] = ExperimentStatus(data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="status must be one of: proposed, planned, running, completed")

    for field, value in data.items():
        setattr(exp, field, value)

    db.commit()
    db.refresh(exp)
    return _out(exp)


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exp = _get_owned(db, experiment_id, current_user)
    db.delete(exp)
    db.commit()
    return None


def _get_owned(db: Session, experiment_id: str, current_user: User) -> Experiment:
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    if exp.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this experiment.")
    return exp


def _out(exp: Experiment) -> ExperimentOut:
    return ExperimentOut(
        id=exp.id, name=exp.name, problem=exp.problem, hypothesis=exp.hypothesis,
        target_segment=exp.target_segment, proposed_change=exp.proposed_change,
        primary_kpi=exp.primary_kpi, secondary_kpi=exp.secondary_kpi,
        expected_impact=exp.expected_impact, priority=exp.priority.value,
        reason=exp.reason, success_criteria=exp.success_criteria, status=exp.status.value,
    )
