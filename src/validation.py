# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Validation functions. They FAIL LOUDLY (raise) when data is not acceptable."""
import pandas as pd


class ValidationError(Exception):
    """Raised when data does not meet the quality rules."""


def check_required_columns(df: pd.DataFrame, required: list) -> None:
    """Raise if any required column is missing from the file."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValidationError(f"Missing required columns: {missing}")


def check_unique(df: pd.DataFrame, col: str) -> None:
    """Raise if the key column contains repeated values."""
    n_dup = int(df[col].duplicated().sum())
    if n_dup:
        raise ValidationError(f"Column '{col}' has {n_dup} duplicate values")


def check_no_nulls(df: pd.DataFrame, cols: list) -> None:
    """Raise if any of the given columns has missing values."""
    bad = {c: int(df[c].isna().sum()) for c in cols if df[c].isna().any()}
    if bad:
        raise ValidationError(f"Nulls found: {bad}")


def check_range(df: pd.DataFrame, col: str, lo: float, hi: float) -> None:
    """Raise if any non-missing value of `col` lies outside [lo, hi]."""
    s = df[col].dropna()
    n_bad = int((~s.between(lo, hi)).sum())
    if n_bad:
        raise ValidationError(f"Column '{col}': {n_bad} values outside [{lo}, {hi}]")


def row_validity(df: pd.DataFrame, id_col: str, created_col: str, closed_col: str) -> pd.Series:
    """True for rows that are usable: has an id, a valid start date, and an end date not before the start.

    Rows failing this are REJECTED (saved separately), not silently fixed.
    """
    ok = df[id_col].notna() & df[created_col].notna() & df[closed_col].notna()
    ok &= df[closed_col] >= df[created_col]
    return ok


def pass_rate(valid_mask: pd.Series) -> float:
    """Share of rows (0-1) that passed validation."""
    return float(valid_mask.mean()) if len(valid_mask) else 0.0


def quality_gate(rate: float, threshold: float) -> None:
    """Quality gate: stop the whole pipeline with a clear error when too many rows are bad."""
    if rate < threshold:
        raise ValidationError(
            f"QUALITY GATE FAILED: validation pass rate {rate:.1%} is below the required {threshold:.0%}"
        )
