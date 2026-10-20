import pandas as pd

from app.utils.io import build_preview, read_upload_dataframe


def test_excel_numeric_headers_are_normalized_for_mapping(monkeypatch):
    source = pd.DataFrame([[101, "Ada"]], columns=[0, "Full name"])
    monkeypatch.setattr(pd, "read_excel", lambda path: source.copy())

    df = read_upload_dataframe("students.xls", "xls")
    preview = build_preview(df)

    assert df.columns.tolist() == ["0", "Full name"]
    assert preview["columns"] == ["0", "Full name"]
    assert preview["suggested_mapping"]["Full name"] == "name"
    assert preview["sample_rows"] == [{"0": 101, "Full name": "Ada"}]
