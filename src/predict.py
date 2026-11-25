# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Score new rows with the saved pipeline.

Usage:  python -m src.predict data/new_rows/new_rows.csv predictions.csv
"""
import argparse
import json

import joblib
import pandas as pd

from src import cleaning, config


def predict_file(in_csv, out_csv):
    cols = json.loads((config.MODEL_DIR / "input_columns.json").read_text())
    new = pd.read_csv(in_csv)
    missing = [c for c in cols if c not in new.columns]
    if missing:
        raise SystemExit(f"ERROR: input file is missing required columns: {missing}")
    # apply the SAME light cleaning used on the training data (see src/cleaning.py)
    new = cleaning.to_numeric(new, config.NUMERIC_COLS)
    new = cleaning.null_out_of_range(new, config.RANGES)
    for c in config.CATEGORICAL_COLS:
        new[c] = cleaning.standardise_text(new[c])
    pipe = joblib.load(config.MODEL_FILE)
    out = new.copy()
    out["prediction"] = pipe.predict(new[cols])
    if config.TASK == "classification":
        out["probability"] = pipe.predict_proba(new[cols])[:, 1].round(3)
    out.to_csv(out_csv, index=False)
    print(f"wrote {len(out)} predictions to {out_csv}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv"); ap.add_argument("output_csv")
    a = ap.parse_args()
    predict_file(a.input_csv, a.output_csv)
