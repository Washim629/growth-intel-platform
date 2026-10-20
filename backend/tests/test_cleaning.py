import numpy as np
import pandas as pd

from app.analytics.cleaning import suggest_column_mapping, apply_mapping, clean_dataframe


def test_suggest_column_mapping_recognizes_aliases():
    mapping = suggest_column_mapping(["Lead ID", "Email", "UTM_Source", "MRR"])
    assert mapping["Lead ID"] == "lead_id"
    assert mapping["Email"] == "email"
    assert mapping["UTM_Source"] == "source"
    assert mapping["MRR"] == "revenue"


def test_clean_dataframe_flags_duplicates_without_dropping_rows():
    df = pd.DataFrame({
        "email": ["a@x.com", "a@x.com", "b@x.com"],
        "revenue": [100, 100, 50],
        "signup_date": ["2024-01-01", "2024-01-01", "2024-01-02"],
    })
    cleaned, report = clean_dataframe(df)
    assert len(cleaned) == 3  # no rows dropped
    assert report["duplicate_count"] == 1
    assert cleaned["_is_duplicate"].sum() == 1


def test_clean_dataframe_coerces_invalid_numeric_and_dates():
    df = pd.DataFrame({
        "revenue": ["100", "abc", "-50"],
        "signup_date": ["2024-01-01", "not-a-date", "2024-01-03"],
        "engagement_score": [50, 500, -10],
    })
    cleaned, report = clean_dataframe(df)
    assert pd.isna(cleaned.loc[1, "revenue"])
    assert pd.isna(cleaned.loc[1, "signup_date"])
    assert pd.isna(cleaned.loc[2, "revenue"])  # negative revenue -> missing
    assert cleaned.loc[1, "engagement_score"] == 100  # clipped
    assert cleaned.loc[2, "engagement_score"] == 0    # clipped


def test_quality_score_between_0_and_100():
    df = pd.DataFrame({"email": ["a@x.com", None, "c@x.com"], "revenue": [10, 20, None]})
    _, report = clean_dataframe(df)
    assert 0 <= report["data_quality_score"] <= 100
