# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Part A pipeline: raw CSV -> validate -> clean -> summaries -> charts -> SQLite -> metrics.json.

Run:  python -m src.run_part_a            (uses data/raw file from config)
      python -m src.run_part_a --raw path/to/other.csv
"""
import argparse
import json
import sqlite3

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt

from src import cleaning, config, features, validation


def run(raw_path, threshold=config.MIN_PASS_RATE):
    for d in (config.CLEAN_FILE.parent, config.REJECTED_FILE.parent, config.FIG_DIR, config.REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # 1. load (raw stays untouched: we only read it)
    raw = pd.read_csv(raw_path)
    validation.check_required_columns(raw, [config.ID_COL] + config.DATE_COLS + config.NUMERIC_COLS + config.CATEGORICAL_COLS)
    metrics = {"rows_raw": len(raw), "missing_pct_before": cleaning.missing_percent(raw).to_dict()}

    # 2. type fixes + duplicates
    df = cleaning.to_numeric(raw, config.NUMERIC_COLS)
    df = cleaning.parse_dates(df, config.DATE_COLS)
    df, n_dup = cleaning.drop_duplicates(df)
    metrics["duplicates_removed"] = n_dup

    # 3. validation -> quality gate -> reject bad rows
    valid = validation.row_validity(df, config.ID_COL, "created_at", "closed_at")
    rate = validation.pass_rate(valid)
    metrics.update(validation_pass_rate=round(rate, 4), rows_rejected=int((~valid).sum()), gate_threshold=threshold)
    metrics_path = config.REPORT_DIR / "metrics.json"
    try:
        validation.quality_gate(rate, threshold)
    except validation.ValidationError:
        metrics["gate"] = "FAILED"
        metrics_path.write_text(json.dumps(metrics, indent=2))  # metrics are written even on failure
        raise
    metrics["gate"] = "PASSED"
    df[~valid].to_csv(config.REJECTED_FILE, index=False)
    df = df[valid].reset_index(drop=True)

    # 4. standardise categories, outliers, missing categories
    for col in config.CATEGORICAL_COLS:
        df[col] = cleaning.standardise_text(df[col])
    df = cleaning.null_out_of_range(df, config.RANGES)
    df = cleaning.fill_missing_categories(df, config.CATEGORICAL_COLS)
    validation.check_unique(df, config.ID_COL)          # these raise if cleaning failed
    validation.check_no_nulls(df, [config.ID_COL, "created_at", "closed_at"] + config.CATEGORICAL_COLS)
    for col, (lo, hi) in config.RANGES.items():
        validation.check_range(df, col, lo, hi)
    df = features.derive_columns(df)

    # 5. NumPy vectorised operations
    df["log_hours"] = np.log1p(df["resolution_hours"].to_numpy())                      # vectorised transform
    df["is_weekend"] = np.where(df["created_at"].dt.dayofweek.to_numpy() >= 5, 1, 0)   # vectorised condition
    metrics["hours_iqr_outliers"] = int(cleaning.iqr_outlier_mask(df["resolution_hours"].to_numpy()).sum())

    df.to_csv(config.CLEAN_FILE, index=False)
    metrics["rows_clean"] = len(df)
    metrics["missing_pct_after"] = cleaning.missing_percent(df[config.NUMERIC_COLS + config.CATEGORICAL_COLS]).to_dict()
    metrics["breach_rate"] = round(float(df[config.TARGET].mean()), 4)
    metrics_path.write_text(json.dumps(metrics, indent=2))

    # 6. Pandas summaries -> files
    df.groupby("category").agg(n=("request_id", "count"), mean_hours=("resolution_hours", "mean"),
                               median_hours=("resolution_hours", "median"),
                               breach_rate=(config.TARGET, "mean")).round(3).to_csv(config.REPORT_DIR / "summary_by_category.csv")
    df.pivot_table(index="category", columns="priority", values="resolution_hours", aggfunc="median").round(1)\
      .to_csv(config.REPORT_DIR / "pivot_category_priority.csv")
    df["channel"].value_counts().to_csv(config.REPORT_DIR / "channel_counts.csv")

    # 7. three charts (title, labelled axes with units, one-line takeaway in README)
    by_cat = df.groupby("category")[config.TARGET].mean().mul(100).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4)); by_cat.plot.barh(ax=ax)
    ax.set(title="SLA breach rate by category", xlabel="Requests closed after 72 h (%)", ylabel="Category")
    fig.tight_layout(); fig.savefig(config.FIG_DIR / "fig1_breach_by_category.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4)); ax.hist(df["resolution_hours"].clip(upper=300), bins=50)
    ax.set(title="Distribution of resolution time", xlabel="Hours to close (clipped at 300 h)", ylabel="Number of requests")
    fig.tight_layout(); fig.savefig(config.FIG_DIR / "fig2_resolution_hist.png", dpi=120); plt.close(fig)

    monthly = df.set_index("created_at").resample("MS").size()
    fig, ax = plt.subplots(figsize=(7, 4)); ax.plot(monthly.index, monthly.values, marker="o")
    ax.set(title="Requests created per month", xlabel="Month", ylabel="Number of requests")
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(config.FIG_DIR / "fig3_monthly_volume.png", dpi=120); plt.close(fig)

    # 8. SQLite: load cleaned table, answer one question with GROUP BY
    with sqlite3.connect(config.DB_FILE) as con:
        df.assign(created_at=df["created_at"].astype(str), closed_at=df["closed_at"].astype(str))\
          .to_sql("requests", con, if_exists="replace", index=False)
        sql = (config.SQL_DIR / "requests_by_category.sql").read_text()
        result = pd.read_sql_query(sql, con)
    result.to_csv(config.REPORT_DIR / "sql_requests_by_category.csv", index=False)

    print(f"Part A OK | pass rate {rate:.1%} | rejected {metrics['rows_rejected']} | duplicates {n_dup} | clean rows {len(df)}")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(config.RAW_FILE))
    ap.add_argument("--threshold", type=float, default=config.MIN_PASS_RATE)
    a = ap.parse_args()
    try:
        run(a.raw, a.threshold)
    except validation.ValidationError as e:
        raise SystemExit(f"ERROR: {e}")
