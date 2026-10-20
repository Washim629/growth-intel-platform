from app.analytics.anomalies import detect_anomalies_in_series


def test_no_anomalies_in_flat_series():
    points = [{"period": f"2024-01-{i:02d}", "value": 100.0} for i in range(1, 15)]
    anomalies = detect_anomalies_in_series(points, "leads")
    assert anomalies == []


def test_detects_spike():
    points = [{"period": f"2024-01-{i:02d}", "value": 100.0} for i in range(1, 15)]
    points[10]["value"] = 1000.0  # inject a clear spike
    anomalies = detect_anomalies_in_series(points, "leads")
    assert len(anomalies) >= 1
    assert anomalies[0]["metric"] == "leads"
    assert anomalies[0]["change_pct"] > 0


def test_short_series_returns_no_anomalies():
    points = [{"period": "2024-01-01", "value": 10.0}]
    assert detect_anomalies_in_series(points, "leads") == []
