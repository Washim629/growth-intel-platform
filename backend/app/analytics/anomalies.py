"""
Lightweight, purely statistical anomaly detection (rolling mean/std +
z-score). This is NOT a machine-learning model and the rest of the app
must never describe it as one - see spec section 14/32.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

Z_SCORE_THRESHOLD = 2.0
ROLLING_WINDOW = 7


def detect_anomalies_in_series(points: List[Dict], metric_name: str) -> List[Dict]:
    """points: [{period: 'YYYY-MM-DD', value: float}, ...] sorted ascending."""
    if len(points) < ROLLING_WINDOW + 2:
        return []

    df = pd.DataFrame(points)
    df["value"] = df["value"].astype(float)
    rolling_mean = df["value"].rolling(window=ROLLING_WINDOW, min_periods=3).mean()
    rolling_std = df["value"].rolling(window=ROLLING_WINDOW, min_periods=3).std().replace(0, np.nan)

    z_scores = (df["value"] - rolling_mean) / rolling_std
    anomalies = []
    for i in range(len(df)):
        z = z_scores.iloc[i]
        if pd.isna(z) or abs(z) < Z_SCORE_THRESHOLD:
            continue
        baseline = rolling_mean.iloc[i]
        value = df["value"].iloc[i]
        change_pct = round((value - baseline) / baseline * 100, 2) if baseline else None
        severity = "high" if abs(z) >= 3 else "medium"
        direction = "increase" if value > baseline else "decrease"

        explanation = (
            f"{metric_name.title()} showed an unusual {direction} of "
            f"{abs(change_pct) if change_pct is not None else 'N/A'}% versus its recent "
            f"{ROLLING_WINDOW}-day average. This is a statistical outlier (z-score {round(float(z), 2)}), "
            f"not a confirmed cause - investigate campaigns, outages, or data issues around this date."
        )

        anomalies.append({
            "metric": metric_name,
            "date": df["period"].iloc[i],
            "severity": severity,
            "change_pct": change_pct if change_pct is not None else 0.0,
            "possible_explanation": explanation,
            "value": round(float(value), 2),
            "baseline": round(float(baseline), 2) if baseline else 0.0,
        })
    return anomalies


def detect_all_anomalies(trend_series: List[Dict]) -> List[Dict]:
    all_anomalies = []
    for series in trend_series:
        all_anomalies.extend(detect_anomalies_in_series(series["points"], series["metric"]))
    all_anomalies.sort(key=lambda a: (a["severity"] != "high", a["date"]))
    return all_anomalies
