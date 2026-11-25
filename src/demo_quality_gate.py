# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Part A bonus: show the quality gate FAILING on a corrupted copy and PASSING on the real data.

Run: python -m src.demo_quality_gate
The corrupted copy goes to /tmp style temp location; data/raw is never touched.
"""
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src import config, run_part_a, validation

raw = pd.read_csv(config.RAW_FILE)
bad = raw.copy()
rng = np.random.default_rng(1)
bad.loc[rng.random(len(bad)) < 0.4, "closed_at"] = "N/A"      # destroy 40% of the end dates
with tempfile.TemporaryDirectory() as tmp:
    corrupted = Path(tmp) / "corrupted.csv"
    bad.to_csv(corrupted, index=False)
    try:
        run_part_a.run(corrupted)
        print("UNEXPECTED: corrupted data passed")
    except validation.ValidationError as e:
        print("Corrupted copy -> pipeline stopped as expected:", e)
print("Real data ->", end=" ")
run_part_a.run(config.RAW_FILE)
