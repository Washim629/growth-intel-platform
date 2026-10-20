"""
Data ingestion / cleaning engine.

Pure-pandas functions with no FastAPI or DB dependency so they are easy
to unit test in isolation (see backend/tests/test_cleaning.py).
"""
from __future__ import annotations

import difflib
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

CANONICAL_FIELDS = [
    "lead_id", "customer_id", "name", "email", "signup_date", "source",
    "campaign", "industry", "country", "company_size", "product", "plan",
    "trial_start", "activation_date", "payment_date", "revenue",
    "engagement_score", "number_of_sessions", "pages_viewed",
    "emails_opened", "support_tickets", "churn", "status",
]

DATE_FIELDS = {"signup_date", "trial_start", "activation_date", "payment_date"}
NUMERIC_FIELDS = {
    "revenue", "engagement_score", "number_of_sessions", "pages_viewed",
    "emails_opened", "support_tickets",
}
BOOL_FIELDS = {"churn"}

# Common alias -> canonical field, used to seed the fuzzy matcher.
ALIASES = {
    "lead id": "lead_id", "leadid": "lead_id", "id": "lead_id",
    "customer id": "customer_id", "customerid": "customer_id", "cust_id": "customer_id",
    "full name": "name", "fullname": "name", "contact name": "name",
    "e-mail": "email", "email address": "email",
    "signup": "signup_date", "sign up date": "signup_date", "created_at": "signup_date",
    "lead_source": "source", "utm_source": "source", "acquisition_source": "source",
    "utm_campaign": "campaign",
    "sector": "industry", "vertical": "industry",
    "region": "country", "location": "country",
    "employees": "company_size", "size": "company_size",
    "subscription": "plan", "tier": "plan",
    "trial_started_at": "trial_start", "trial start date": "trial_start",
    "activated_at": "activation_date", "activation": "activation_date",
    "paid_at": "payment_date", "purchase_date": "payment_date", "conversion_date": "payment_date",
    "mrr": "revenue", "arr": "revenue", "amount": "revenue", "total_revenue": "revenue",
    "engagement": "engagement_score", "engagement rate": "engagement_score",
    "sessions": "number_of_sessions", "num_sessions": "number_of_sessions", "visits": "number_of_sessions",
    "pageviews": "pages_viewed", "page_views": "pages_viewed",
    "opens": "emails_opened", "email_opens": "emails_opened",
    "tickets": "support_tickets", "support_requests": "support_tickets",
    "churned": "churn", "is_churned": "churn",
    "lifecycle_stage": "status", "stage": "status",
}


def _normalize(col: str) -> str:
    return re.sub(r"[\s_\-]+", " ", col.strip().lower())


def suggest_column_mapping(columns: List[str]) -> Dict[str, Optional[str]]:
    """Best-effort automatic mapping from source columns to canonical
    fields. Returns None for columns with no confident match - the user
    confirms/edits the mapping in the UI before cleaning proceeds."""
    mapping: Dict[str, Optional[str]] = {}
    normalized_targets = {f: _normalize(f) for f in CANONICAL_FIELDS}
    used_targets = set()

    for col in columns:
        norm = _normalize(col)
        candidate = None

        if norm in CANONICAL_FIELDS:
            candidate = norm
        elif norm in ALIASES:
            candidate = ALIASES[norm]
        else:
            # fuzzy match against canonical field names
            best = difflib.get_close_matches(norm, list(normalized_targets.values()), n=1, cutoff=0.72)
            if best:
                for field, normed in normalized_targets.items():
                    if normed == best[0]:
                        candidate = field
                        break

        if candidate and candidate in used_targets:
            candidate = None  # avoid mapping two source columns to the same field
        if candidate:
            used_targets.add(candidate)
        mapping[col] = candidate
    return mapping


def _coerce_bool(series: pd.Series) -> pd.Series:
    truthy = {"1", "true", "yes", "y", "churned", "t"}
    falsy = {"0", "false", "no", "n", "active", "f"}

    def conv(v):
        if pd.isna(v):
            return np.nan
        s = str(v).strip().lower()
        if s in truthy:
            return True
        if s in falsy:
            return False
        return np.nan

    return series.map(conv)


def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[pd.DataFrame, Dict]:
    """Rename mapped source columns to canonical names; stash unmapped
    columns in a JSON-serializable `extra` dict per row instead of
    dropping them."""
    rename = {src: tgt for src, tgt in mapping.items() if tgt}
    unmapped_cols = [c for c in df.columns if c not in mapping or not mapping.get(c)]

    out = df.rename(columns=rename).copy()

    if unmapped_cols:
        out["extra"] = df[unmapped_cols].to_dict(orient="records")
    else:
        out["extra"] = [{} for _ in range(len(df))]

    # Ensure every canonical field exists, even if not present in source.
    for field in CANONICAL_FIELDS:
        if field not in out.columns:
            out[field] = np.nan

    return out, {"unmapped_columns": unmapped_cols, "mapped_columns": rename}


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Clean an already-mapped dataframe (canonical column names).

    Returns (cleaned_df, quality_report). Never silently drops rows -
    duplicate/invalid rows are flagged in the report; only exact
    full-row duplicates are collapsed, and that count is reported.
    """
    transformations: List[str] = []
    total_rows = len(df)
    working = df.copy()

    # 1. Trim whitespace / normalize empty strings to NaN on object columns
    for col in working.select_dtypes(include="object").columns:
        working[col] = working[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
        working[col] = working[col].replace({"": np.nan, "nan": np.nan, "None": np.nan, "N/A": np.nan, "n/a": np.nan})
    transformations.append("Trimmed whitespace and normalized empty strings to missing values.")

    # 2. Parse dates
    for field in DATE_FIELDS:
        if field in working.columns:
            before_valid = working[field].notna().sum()
            working[field] = pd.to_datetime(working[field], errors="coerce", utc=False)
            after_valid = working[field].notna().sum()
            if before_valid != after_valid:
                transformations.append(
                    f"Parsed '{field}' as dates; {before_valid - after_valid} unparsable values set to missing."
                )

    # 3. Coerce numerics
    for field in NUMERIC_FIELDS:
        if field in working.columns:
            before_valid = working[field].notna().sum()
            working[field] = pd.to_numeric(working[field], errors="coerce")
            after_valid = working[field].notna().sum()
            if before_valid != after_valid:
                transformations.append(
                    f"Coerced '{field}' to numeric; {before_valid - after_valid} invalid values set to missing."
                )
            # revenue / counts should not be negative
            if field in {"revenue", "number_of_sessions", "pages_viewed", "emails_opened", "support_tickets"}:
                neg_mask = working[field] < 0
                if neg_mask.any():
                    working.loc[neg_mask, field] = np.nan
                    transformations.append(f"Set {int(neg_mask.sum())} negative '{field}' values to missing.")

    # 4. Engagement score should be within 0-100; clip out-of-range instead of dropping
    if "engagement_score" in working.columns:
        oob = working["engagement_score"].notna() & ((working["engagement_score"] < 0) | (working["engagement_score"] > 100))
        if oob.any():
            working.loc[oob, "engagement_score"] = working.loc[oob, "engagement_score"].clip(0, 100)
            transformations.append(f"Clipped {int(oob.sum())} out-of-range engagement scores to [0, 100].")

    # 5. Booleans
    for field in BOOL_FIELDS:
        if field in working.columns:
            working[field] = _coerce_bool(working[field])

    # 6. Normalize categorical casing/whitespace inconsistencies
    for field in ["source", "campaign", "industry", "country", "plan", "status", "product", "company_size"]:
        if field in working.columns:
            working[field] = working[field].apply(
                lambda v: v.strip().replace("_", " ").replace("-", " ").title() if isinstance(v, str) else v
            )

    # 7. Detect duplicates (based on business key when available, else full row)
    dedupe_keys = [k for k in ["email", "source_lead_id", "source_customer_id"] if k in working.columns]
    if dedupe_keys and working[dedupe_keys].notna().any().any():
        dup_mask = working.duplicated(subset=dedupe_keys, keep="first") & working[dedupe_keys].notna().any(axis=1)
    else:
        dup_mask = working.drop(columns=["extra"], errors="ignore").duplicated(keep="first")
    duplicate_count = int(dup_mask.sum())
    if duplicate_count:
        transformations.append(f"Flagged {duplicate_count} duplicate rows (kept first occurrence, others marked).")
    working["_is_duplicate"] = dup_mask

    # 8. Outlier flags (IQR) for revenue - informational only, not removed
    outlier_count = 0
    if "revenue" in working.columns and working["revenue"].notna().sum() > 10:
        q1, q3 = working["revenue"].quantile([0.25, 0.75])
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        lower = q1 - 1.5 * iqr
        outlier_mask = working["revenue"].notna() & ((working["revenue"] > upper) | (working["revenue"] < lower))
        outlier_count = int(outlier_mask.sum())
        working["_revenue_outlier"] = outlier_mask
        if outlier_count:
            transformations.append(f"Flagged {outlier_count} revenue values as statistical outliers (IQR method).")
    else:
        working["_revenue_outlier"] = False

    # 9. Row validity = has at least an identifying key and no critical corruption
    has_identity = working[[c for c in ["email", "source_lead_id", "source_customer_id", "name"] if c in working.columns]].notna().any(axis=1)
    working["_is_valid"] = has_identity & ~working["_is_duplicate"]
    valid_rows = int(working["_is_valid"].sum())
    invalid_rows = total_rows - valid_rows

    missing_pct = {
        col: round(float(working[col].isna().mean() * 100), 2)
        for col in CANONICAL_FIELDS
        if col in working.columns
    }
    dtypes = {col: str(working[col].dtype) for col in working.columns if col in CANONICAL_FIELDS}

    # Data quality score: weighted mix of completeness + validity + non-duplication
    avg_completeness = 100 - (sum(missing_pct.values()) / max(len(missing_pct), 1))
    validity_pct = (valid_rows / total_rows * 100) if total_rows else 0
    dup_penalty = (duplicate_count / total_rows * 100) if total_rows else 0
    quality_score = round(max(0, min(100, 0.5 * avg_completeness + 0.4 * validity_pct - 0.1 * dup_penalty)), 1)

    report = {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "missing_value_pct": missing_pct,
        "duplicate_count": duplicate_count,
        "outlier_count": outlier_count,
        "column_dtypes": dtypes,
        "data_quality_score": quality_score,
        "transformations": transformations,
    }
    return working, report
