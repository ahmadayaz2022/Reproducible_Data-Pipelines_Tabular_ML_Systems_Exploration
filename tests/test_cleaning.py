# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
import numpy as np
import pandas as pd

from src import cleaning


def test_standardise_text_merges_variants_and_keeps_missing():
    s = pd.Series([" Noise ", "NOISE", "noise", None])
    out = cleaning.standardise_text(s)
    assert list(out[:3]) == ["noise"] * 3
    assert out.isna().iloc[3]


def test_parse_dates_handles_iso_dayfirst_and_junk():
    df = pd.DataFrame({"d": ["2025-01-11 10:00:00", "31/03/2025 09:04", "N/A"]})
    out = cleaning.parse_dates(df, ["d"])
    assert out["d"].iloc[0] == pd.Timestamp("2025-01-11 10:00")   # NOT 1 November
    assert out["d"].iloc[1] == pd.Timestamp("2025-03-31 09:04")
    assert out["d"].isna().iloc[2]


def test_to_numeric_turns_text_into_nan():
    out = cleaning.to_numeric(pd.DataFrame({"x": ["1", "abc", "3.5"]}), ["x"])
    assert out["x"].isna().sum() == 1 and out["x"].iloc[2] == 3.5


def test_drop_duplicates_counts_removed_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    out, n = cleaning.drop_duplicates(df)
    assert n == 1 and len(out) == 2


def test_null_out_of_range_keeps_row_but_blanks_value():
    out = cleaning.null_out_of_range(pd.DataFrame({"lat": [31.5, 999.0]}), {"lat": (24, 37)})
    assert len(out) == 2 and out["lat"].isna().tolist() == [False, True]


def test_fill_missing_categories():
    out = cleaning.fill_missing_categories(pd.DataFrame({"c": ["a", None]}), ["c"])
    assert out["c"].tolist() == ["a", "unknown"]


def test_missing_percent():
    assert cleaning.missing_percent(pd.DataFrame({"a": [1, None, 3, None]}))["a"] == 50.0


def test_iqr_outlier_mask_flags_extreme_value():
    mask = cleaning.iqr_outlier_mask(np.array([1, 2, 3, 2, 1, 100.0]))
    assert mask.tolist() == [False] * 5 + [True]
