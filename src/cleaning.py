# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Small, testable cleaning functions. Each takes a DataFrame and returns a NEW one."""
import numpy as np
import pandas as pd


def standardise_text(series: pd.Series) -> pd.Series:
    """Lower-case, strip and collapse repeated spaces so 'Noise ', 'NOISE' and 'noise' match.

    Missing values stay missing (they are not turned into the string 'nan').
    """
    out = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True).str.lower()
    return out.astype(object).where(out.notna(), np.nan)   # plain NaN: scikit-learn imputers cannot handle pd.NA


def parse_dates(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Convert columns to datetime. Unparseable text (e.g. 'N/A') becomes NaT instead of crashing.

    Two passes, because a column can mix styles:
      1. ISO style (2025-01-11 19:16:00) parsed strictly, so the month/day order is never guessed.
      2. Whatever is left is tried as day/month/year (31/03/2025 09:04).
    A single dayfirst=True pass would misread ISO '2025-01-11' as 1 November - a classic bug.
    """
    out = df.copy()
    for col in cols:
        text = out[col].astype("string")
        first = pd.to_datetime(text, errors="coerce", format="ISO8601")
        rest = text.where(first.isna())
        second = pd.to_datetime(rest, errors="coerce", format="%d/%m/%Y %H:%M")
        out[col] = first.fillna(second)
    return out


def to_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Force columns to numbers; non-numeric junk becomes NaN."""
    out = df.copy()
    for col in cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def drop_duplicates(df: pd.DataFrame, subset=None):
    """Remove exact duplicate rows (or duplicates on `subset`). Returns (clean_df, n_removed)."""
    before = len(df)
    out = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    return out, before - len(out)


def null_out_of_range(df: pd.DataFrame, ranges: dict) -> pd.DataFrame:
    """Outlier handling: values outside the allowed (low, high) range become NaN.

    We do NOT delete the row - the other columns are still useful. The value is
    imputed later, inside the ML pipeline, using training data only.
    """
    out = df.copy()
    for col, (lo, hi) in ranges.items():
        if col in out:
            out[col] = out[col].where(out[col].between(lo, hi))
    return out


def fill_missing_categories(df: pd.DataFrame, cols: list, label: str = "unknown") -> pd.DataFrame:
    """Missing categories become an explicit 'unknown' level (missingness can be informative)."""
    out = df.copy()
    for col in cols:
        out[col] = out[col].fillna(label)
    return out


def missing_percent(df: pd.DataFrame) -> pd.Series:
    """Percentage of missing values per column (used for the before/after quality report)."""
    return (df.isna().mean() * 100).round(2)


def iqr_outlier_mask(values: np.ndarray, k: float = 1.5) -> np.ndarray:
    """NumPy (vectorised) IQR rule: True where a value is an outlier. NaNs are ignored."""
    q1, q3 = np.nanpercentile(values, [25, 75])
    iqr = q3 - q1
    return (values < q1 - k * iqr) | (values > q3 + k * iqr)
