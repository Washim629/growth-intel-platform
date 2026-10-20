from __future__ import annotations

import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.analytics.cleaning import suggest_column_mapping

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(dataset_id: str, filename: str, content: bytes) -> str:
    safe_name = f"{dataset_id}_{os.path.basename(filename)}"
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(content)
    return path


def read_upload_dataframe(path: str, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        df = pd.read_csv(path)
    elif file_type in ("xlsx", "xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    df.columns = df.columns.map(str)
    return df


def build_preview(df: pd.DataFrame, sample_size: int = 10) -> Dict[str, Any]:
    columns = list(df.columns)
    suggested_mapping = suggest_column_mapping(columns)

    dtypes = {c: str(df[c].dtype) for c in columns}
    missing_pct = {c: round(float(df[c].isna().mean() * 100), 2) for c in columns}
    duplicate_count = int(df.duplicated().sum())

    sample = df.head(sample_size).replace({np.nan: None})
    sample_rows: List[Dict[str, Any]] = sample.astype(object).to_dict(orient="records")

    return {
        "columns": columns,
        "sample_rows": sample_rows,
        "suggested_mapping": suggested_mapping,
        "detected_dtypes": dtypes,
        "missing_value_pct": missing_pct,
        "duplicate_row_count": duplicate_count,
        "total_rows": len(df),
    }
