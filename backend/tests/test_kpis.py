import pandas as pd
import numpy as np

from app.analytics.kpis import compute_kpis, apply_filters
from app.analytics.features import engineer_features
from app.analytics.funnel import compute_funnel


def _sample_df():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
        "activation_date": pd.to_datetime(["2024-01-02", None, "2024-01-05", None]),
        "payment_date": pd.to_datetime(["2024-01-05", None, None, None]),
        "revenue": [100.0, 0.0, 0.0, 0.0],
        "source": ["google", "google", "facebook", "facebook"],
    })
    return engineer_features(df)


def test_compute_kpis_basic_counts():
    df = _sample_df()
    kpis = compute_kpis(df)
    assert kpis["leads"] == 4
    assert kpis["signups"] == 4
    assert kpis["revenue"] == 100.0


def test_compute_kpis_empty_dataframe_returns_none_values():
    kpis = compute_kpis(pd.DataFrame())
    assert kpis["leads"] is None


def test_activation_and_trial_conversion_use_lifecycle_status_when_dates_are_missing():
    df = pd.DataFrame({
        "signup_date": [pd.NaT] * 5,
        "trial_start": [pd.NaT] * 5,
        "activation_date": [pd.NaT] * 5,
        "payment_date": [pd.NaT] * 5,
        "status": ["lead", "trial", "activated", "paying", "churned"],
    })

    kpis = compute_kpis(df)
    funnel = compute_funnel(df)

    assert kpis["signups"] == 4
    assert kpis["trials"] == 4
    assert kpis["activations"] == 3
    assert kpis["payments"] == 2
    assert kpis["activation_rate"] == 75.0
    assert kpis["trial_conversion"] == 50.0
    assert [stage["user_count"] for stage in funnel["stages"]] == [5, 5, 4, 4, 3, 2]


def test_revenue_also_counts_as_payment_when_payment_date_is_missing():
    df = pd.DataFrame({
        "trial_start": [pd.NaT, pd.Timestamp("2024-01-01")],
        "revenue": [100.0, 0.0],
    })

    kpis = compute_kpis(df)

    assert kpis["trial_conversion"] == 50.0


def test_lifecycle_status_can_indicate_zero_trial_to_payment_conversion():
    df = pd.DataFrame({"status": ["trial", "activated"]})

    assert compute_kpis(df)["trial_conversion"] == 0.0


def test_apply_filters_by_source():
    df = _sample_df()
    filtered = apply_filters(df, source="google")
    assert len(filtered) == 2
    assert set(filtered["source"]) == {"google"}
