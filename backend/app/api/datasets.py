from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.config import get_settings
from app.models.user import User
from app.models.dataset import Dataset, DatasetStatus
from app.schemas.dataset import DatasetOut, DatasetPreview, ColumnMappingRequest
from app.utils.io import save_upload, read_upload_dataframe, build_preview

router = APIRouter(prefix="/api/datasets", tags=["datasets"])
settings = get_settings()


def _dataset_out(ds: Dataset) -> DatasetOut:
    return DatasetOut(
        id=ds.id, filename=ds.filename, file_type=ds.file_type, row_count=ds.row_count or 0,
        column_names=ds.column_names or [], column_mapping=ds.column_mapping or {},
        status=ds.status.value, data_quality_report=ds.data_quality_report or {},
        created_at=ds.created_at.isoformat(),
    )


@router.post("/upload", response_model=DatasetPreview, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename = file.filename or "upload"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Only .csv and .xlsx/.xls files are supported.")

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_MB}MB upload limit.")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    dataset = Dataset(
        organization_id=current_user.organization_id,
        uploaded_by_id=current_user.id,
        filename=filename,
        file_type="xlsx" if ext in ("xlsx", "xls") else "csv",
        storage_path="",  # set after we know the dataset id
        status=DatasetStatus.uploaded,
    )
    db.add(dataset)
    db.flush()

    try:
        storage_path = save_upload(dataset.id, filename, content)
        df = read_upload_dataframe(storage_path, dataset.file_type)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Could not read file: {exc}") from exc

    if df.empty or len(df.columns) == 0:
        db.rollback()
        raise HTTPException(status_code=422, detail="The uploaded file has no readable columns or rows.")

    preview = build_preview(df)

    dataset.storage_path = storage_path
    dataset.row_count = len(df)
    dataset.column_names = preview["columns"]
    db.commit()
    db.refresh(dataset)

    return DatasetPreview(dataset_id=dataset.id, **preview)


@router.post("/{dataset_id}/mapping", response_model=DatasetOut)
def confirm_mapping(
    dataset_id: str,
    payload: ColumnMappingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = _get_owned_dataset(db, dataset_id, current_user)
    dataset.column_mapping = payload.mapping
    dataset.status = DatasetStatus.mapped
    db.commit()
    db.refresh(dataset)
    return _dataset_out(dataset)


@router.get("", response_model=List[DatasetOut])
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    datasets = (
        db.query(Dataset)
        .filter(Dataset.organization_id == current_user.organization_id)
        .order_by(Dataset.created_at.desc())
        .all()
    )
    return [_dataset_out(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, dataset_id, current_user)
    return _dataset_out(dataset)


@router.get("/{dataset_id}/rows")
def get_dataset_rows(
    dataset_id: str,
    page: int = 1,
    page_size: int = 50,
    search: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Paginated Data Explorer endpoint - never loads the whole dataset
    into the response at once."""
    from app.models.records import LeadRecord

    dataset = _get_owned_dataset(db, dataset_id, current_user)
    query = db.query(LeadRecord).filter(LeadRecord.dataset_id == dataset.id)
    if search:
        like = f"%{search}%"
        query = query.filter((LeadRecord.email.ilike(like)) | (LeadRecord.name.ilike(like)))

    total = query.count()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    rows = query.offset((page - 1) * page_size).limit(page_size).all()

    def row_out(r):
        return {c.name: getattr(r, c.name) for c in r.__table__.columns if c.name not in ("extra",)}

    return {
        "dataset_id": dataset.id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "rows": [row_out(r) for r in rows],
    }


def _get_owned_dataset(db: Session, dataset_id: str, current_user: User) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this dataset.")
    return dataset
