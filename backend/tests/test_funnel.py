import pandas as pd

from app.analytics.funnel import compute_funnel


def test_funnel_counts_are_monotonically_non_increasing():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"] * 10),
        "trial_start": pd.to_datetime(["2024-01-01"] * 6 + [None] * 4),
        "activation_date": pd.to_datetime(["2024-01-02"] * 3 + [None] * 7),
        "payment_date": pd.to_datetime(["2024-01-03"] * 1 + [None] * 9),
    })
    result = compute_funnel(df)
    counts = [s["user_count"] for s in result["stages"]]
    assert counts == sorted(counts, reverse=True)


def test_biggest_drop_off_identified_correctly():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"] * 100),
        "trial_start": pd.to_datetime(["2024-01-01"] * 90 + [None] * 10),
        "activation_date": pd.to_datetime(["2024-01-02"] * 80 + [None] * 20),
        "payment_date": pd.to_datetime(["2024-01-03"] * 10 + [None] * 90),  # big drop here
    })
    result = compute_funnel(df)
    assert result["biggest_drop_off"]["to_stage"] == "Payment"


def test_overall_conversion_rate():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"] * 10),
        "payment_date": pd.to_datetime(["2024-01-02"] * 2 + [None] * 8),
    })
    result = compute_funnel(df, stage_definitions=[
        {"name": "Signup", "condition": lambda d: d["signup_date"].notna()},
        {"name": "Payment", "condition": lambda d: d["payment_date"].notna()},
    ])
    assert result["overall_conversion_rate"] == 20.0
