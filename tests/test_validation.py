# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
import pandas as pd
import pytest

from src import validation as v


def test_required_columns_raises_when_missing():
    with pytest.raises(v.ValidationError):
        v.check_required_columns(pd.DataFrame({"a": [1]}), ["a", "b"])


def test_unique_raises_on_repeats_and_passes_otherwise():
    v.check_unique(pd.DataFrame({"id": [1, 2]}), "id")
    with pytest.raises(v.ValidationError):
        v.check_unique(pd.DataFrame({"id": [1, 1]}), "id")


def test_no_nulls():
    with pytest.raises(v.ValidationError):
        v.check_no_nulls(pd.DataFrame({"a": [1, None]}), ["a"])


def test_range_ignores_missing_but_rejects_outside():
    v.check_range(pd.DataFrame({"x": [1.0, None]}), "x", 0, 5)
    with pytest.raises(v.ValidationError):
        v.check_range(pd.DataFrame({"x": [10.0]}), "x", 0, 5)


def test_row_validity_and_pass_rate():
    t = pd.Timestamp
    df = pd.DataFrame({"id": [1, 2, 3], "c": [t("2025-01-01"), t("2025-01-02"), pd.NaT],
                       "e": [t("2025-01-03"), t("2025-01-01"), t("2025-01-05")]})
    ok = v.row_validity(df, "id", "c", "e")
    assert ok.tolist() == [True, False, False]       # row 2 closes before it opens, row 3 has no start
    assert v.pass_rate(ok) == pytest.approx(1 / 3)


def test_quality_gate_fails_below_threshold_and_passes_above():
    v.quality_gate(0.95, 0.9)
    with pytest.raises(v.ValidationError, match="QUALITY GATE FAILED"):
        v.quality_gate(0.5, 0.9)
