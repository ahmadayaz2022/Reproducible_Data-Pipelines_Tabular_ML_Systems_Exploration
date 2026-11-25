# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Dataset-specific derived columns. Edit for YOUR dataset."""
import pandas as pd

from src import config


def derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add resolution_hours and the target (sla_breached) from the two timestamps.

    Used in Part A (after validation). These are the columns that LEAK in Part B,
    because they are computed from closed_at, which is only known after the fact.
    """
    out = df.copy()
    out["resolution_hours"] = (out["closed_at"] - out["created_at"]).dt.total_seconds() / 3600
    out[config.TARGET] = (out["resolution_hours"] > config.SLA_HOURS).astype(int)
    return out


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Hour / weekday / month from created_at. Row-by-row, learns nothing from the data,
    so it is safe to use inside the pipeline and cannot leak.
    Accepts text or datetime so predict.py can feed a raw CSV."""
    out = df.copy()
    t = pd.to_datetime(out["created_at"], errors="coerce", format="mixed", dayfirst=True)
    out["created_hour"] = t.dt.hour
    out["created_dow"] = t.dt.dayofweek
    out["created_month"] = t.dt.month
    return out


TIME_FEATURES = ["created_hour", "created_dow", "created_month"]
