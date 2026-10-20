import pandas as pd

from app.analytics.segmentation import assign_rule_based_segments, summarize_segments
from app.analytics.features import engineer_features


def test_converted_leads_get_converted_segment():
    df = pd.DataFrame({
        "signup_date": pd.to_datetime(["2024-01-01"] * 3),
        "payment_date": pd.to_datetime(["2024-01-05", None, None]),
        "trial_start": pd.to_datetime([None, "2024-01-01", None]),
        "revenue": [100, 0, 0],
        "engagement_score": [80, 30, 10],
    })
    df = engineer_features(df)
    segments = assign_rule_based_segments(df)
    assert segments.iloc[0] == "Converted"


def test_summarize_segments_produces_expected_fields():
    df = pd.DataFrame({
        "segment": ["A", "A", "B"],
        "is_converted": [True, False, True],
        "revenue": [100, 0, 50],
        "engagement_rate": [0.8, 0.3, 0.6],
        "source": ["google", "google", "facebook"],
    })
    summaries = summarize_segments(df)
    names = {s["name"] for s in summaries}
    assert names == {"A", "B"}
    seg_a = next(s for s in summaries if s["name"] == "A")
    assert seg_a["size"] == 2
    assert seg_a["conversion_rate"] == 50.0
