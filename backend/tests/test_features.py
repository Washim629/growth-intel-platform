from datetime import datetime

import pandas as pd

from app.analytics.features import engineer_features


def test_days_signup_to_activation():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"]),
        "activation_date": pd.to_datetime(["2024-01-06"]),
        "trial_start": pd.to_datetime(["2024-01-01"]),
        "payment_date": pd.to_datetime([None]),
    })
    out = engineer_features(df, now=datetime(2024, 2, 1))
    assert out.loc[0, "days_signup_to_activation"] == 5.0


def test_is_converted_true_when_payment_present():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"]),
        "payment_date": pd.to_datetime(["2024-01-10"]),
        "revenue": [50.0],
    })
    out = engineer_features(df)
    assert bool(out.loc[0, "is_converted"]) is True


def test_funnel_completion_pct_is_0_to_100():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"]),
        "trial_start": pd.to_datetime([None]),
        "activation_date": pd.to_datetime([None]),
        "payment_date": pd.to_datetime([None]),
    })
    out = engineer_features(df)
    assert 0 <= out.loc[0, "funnel_completion_pct"] <= 100
