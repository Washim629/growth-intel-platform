"""Configurable conversion funnel analysis."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

# Default funnel: stage name -> the boolean/presence condition that means
# a row has "reached" that stage.
# Chronological order (signup -> trial -> activation -> payment) so that
# each stage is a true subset of the previous one and counts are
# monotonically non-increasing, like a real funnel. The stage *names*
# follow the product brief; the ordering was adjusted from the brief's
# example to match how these timestamps actually occur in the data
# (activation normally happens during/after the trial, not before it).
# Fully configurable - pass your own stage_definitions to reorder/rename.
DEFAULT_STAGE_DEFINITIONS = [
    {"name": "Marketing", "condition": lambda df: pd.Series(True, index=df.index)},
    {"name": "Lead", "condition": lambda df: pd.Series(True, index=df.index)},
    {"name": "Signup", "condition": lambda df: df["signup_date"].notna() if "signup_date" in df else pd.Series(False, index=df.index)},
    {"name": "Trial", "condition": lambda df: df["trial_start"].notna() if "trial_start" in df else pd.Series(False, index=df.index)},
    {"name": "Activation", "condition": lambda df: df["activation_date"].notna() if "activation_date" in df else pd.Series(False, index=df.index)},
    {"name": "Payment", "condition": lambda df: df["payment_date"].notna() if "payment_date" in df else pd.Series(False, index=df.index)},
]

_TRIAL_STATUSES = {"trial", "activated", "paying", "paid", "converted", "customer", "churned"}
_ACTIVATION_STATUSES = {"activated", "paying", "paid", "converted", "customer", "churned"}
_PAYMENT_STATUSES = {"paying", "paid", "converted", "customer", "churned"}
_KNOWN_STATUSES = _TRIAL_STATUSES | {"lead"}


def has_lifecycle_status_data(df: pd.DataFrame) -> bool:
    if "status" not in df:
        return False
    status = df["status"].fillna("").astype(str).str.strip().str.lower()
    return bool(status.isin(_KNOWN_STATUSES).any())


def get_funnel_stage_masks(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Return stage membership using dates, with lifecycle status as a fallback."""
    empty = pd.Series(False, index=df.index)
    status = (
        df["status"].fillna("").astype(str).str.strip().str.lower()
        if "status" in df
        else pd.Series("", index=df.index, dtype=object)
    )
    payment_status = status.isin(_PAYMENT_STATUSES)
    activation_status = status.isin(_ACTIVATION_STATUSES) | payment_status
    trial_status = status.isin(_TRIAL_STATUSES) | activation_status

    def date_mask(column: str) -> pd.Series:
        return df[column].notna() if column in df else empty.copy()

    revenue_payment = (
        pd.to_numeric(df["revenue"], errors="coerce").fillna(0).gt(0)
        if "revenue" in df
        else empty.copy()
    )
    payment = date_mask("payment_date") | payment_status | revenue_payment
    activation = date_mask("activation_date") | activation_status | payment
    trial = date_mask("trial_start") | trial_status | activation
    signup = date_mask("signup_date") | trial
    return {"signup": signup, "trial": trial, "activation": activation, "payment": payment}


def compute_funnel(df: pd.DataFrame, stage_definitions: Optional[List[Dict]] = None, strict: bool = True) -> Dict:
    """Compute the funnel. When strict=True (default), each stage's
    membership is intersected with the previous stage's membership so
    counts never increase - the correct semantics for a funnel."""
    stage_definitions = stage_definitions or DEFAULT_STAGE_DEFINITIONS
    stages = []
    total = len(df)
    prev_count: Optional[int] = None
    start_count: Optional[int] = None
    cumulative_mask = pd.Series(True, index=df.index)
    stage_masks = get_funnel_stage_masks(df)

    for idx, stage in enumerate(stage_definitions):
        if stage_definitions is DEFAULT_STAGE_DEFINITIONS:
            raw_mask = stage_masks.get(stage["name"].lower(), stage["condition"](df))
        else:
            raw_mask = stage["condition"](df)
        if strict:
            cumulative_mask = cumulative_mask & raw_mask
            mask = cumulative_mask
        else:
            mask = raw_mask
        count = int(mask.sum())
        if idx == 0:
            start_count = count

        conv_from_prev = round(count / prev_count * 100, 2) if prev_count else (100.0 if idx == 0 else None)
        drop_from_prev = round(100 - conv_from_prev, 2) if conv_from_prev is not None else None
        conv_from_start = round(count / start_count * 100, 2) if start_count else None

        stages.append({
            "name": stage["name"],
            "order_index": idx,
            "user_count": count,
            "conversion_from_previous": conv_from_prev,
            "drop_off_from_previous": drop_from_prev,
            "conversion_from_start": conv_from_start,
        })
        prev_count = count

    # Find biggest drop-off (excluding the first stage, which has no "previous")
    biggest = None
    for i in range(1, len(stages)):
        d = stages[i]["drop_off_from_previous"]
        if d is not None and (biggest is None or d > biggest["drop_off_from_previous"]):
            biggest = {
                "from_stage": stages[i - 1]["name"],
                "to_stage": stages[i]["name"],
                "drop_off_from_previous": d,
            }

    overall_conversion = stages[-1]["conversion_from_start"] if stages else None

    return {
        "stages": stages,
        "biggest_drop_off": biggest,
        "overall_conversion_rate": overall_conversion,
        "total_rows": total,
    }
