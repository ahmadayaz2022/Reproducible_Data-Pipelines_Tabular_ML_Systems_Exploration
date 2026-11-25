# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Create a SYNTHETIC messy dataset so you can test the pipeline end to end.

!! This is NOT your assignment dataset. The assignment needs a REAL, raw,
TA-approved dataset. Use this file only to check that the code runs, then
replace data/raw/ with your real data and edit src/config.py.
"""
import numpy as np
import pandas as pd

from src import config


def make(n=8000, seed=0, with_target_info=True):
    rng = np.random.default_rng(seed)
    cats = ["noise", "water leak", "pothole", "garbage", "street light", "stray animal"]
    agencies = ["wasa", "lda", "tma", "pdma"]
    districts = ["north", "south", "east", "west", "central"]
    channels = ["app", "phone", "web", "walk-in"]
    prio = ["low", "medium", "high"]

    created = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365 * 24 * 60, n), unit="m")
    cat = rng.choice(cats, n, p=[.2, .15, .2, .25, .1, .1])
    pr = rng.choice(prio, n, p=[.4, .4, .2])
    ag = rng.choice(agencies, n)
    # hidden rule for how long a request takes (so ML has real signal + noise)
    base = {"noise": 20, "water leak": 60, "pothole": 90, "garbage": 30, "street light": 70, "stray animal": 40}
    hours = np.array([base[c] for c in cat], float)
    hours *= np.where(pr == "high", 0.6, np.where(pr == "low", 1.4, 1.0))
    hours *= np.where(ag == "lda", 1.3, 1.0)
    hours *= np.where(created.dayofweek >= 5, 1.25, 1.0)
    hours *= rng.lognormal(0, 0.45, n)
    closed = created + pd.to_timedelta(hours, unit="h")

    df = pd.DataFrame({
        "request_id": np.arange(100000, 100000 + n),
        "created_at": created, "closed_at": closed,
        "agency": ag, "category": cat, "district": rng.choice(districts, n),
        "channel": rng.choice(channels, n), "priority": pr,
        "latitude": rng.normal(31.52, 0.08, n), "longitude": rng.normal(74.35, 0.08, n),
        "description_len": rng.integers(5, 600, n).astype(float),
        "num_updates": rng.poisson(2, n).astype(float),
    })

    # ---- inject realistic mess ----
    df["category"] = [rng.choice([c, c.upper(), c.title(), " " + c + " "], p=[.7, .1, .1, .1]) for c in df["category"]]
    df["agency"] = [a.upper() if rng.random() < .15 else a for a in df["agency"]]
    df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    swap = rng.random(n) < .2                                  # mixed date format
    df.loc[swap, "created_at"] = pd.to_datetime(df.loc[swap, "created_at"]).dt.strftime("%d/%m/%Y %H:%M")
    df["closed_at"] = df["closed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df.loc[rng.random(n) < .06, "closed_at"] = "N/A"           # invalid entries
    df.loc[rng.random(n) < .02, "created_at"] = "not recorded"
    bad = rng.random(n) < .015                                 # closed before created
    df.loc[bad, "closed_at"] = "2024-01-01 00:00:00"
    for col, p in [("district", .08), ("channel", .05), ("latitude", .04), ("longitude", .04), ("description_len", .03)]:
        df.loc[rng.random(n) < p, col] = np.nan
    df.loc[rng.random(n) < .01, "latitude"] = 999.0            # outliers
    df.loc[rng.random(n) < .01, "description_len"] = -5.0
    df.loc[rng.random(n) < .01, "num_updates"] = 5000.0
    dup = df.sample(int(n * .03), random_state=seed)            # duplicates
    return pd.concat([df, dup], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    config.RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    make().to_csv(config.RAW_FILE, index=False)
    new = make(60, seed=99)
    new = new[["created_at"] + config.NUMERIC_COLS + config.CATEGORICAL_COLS].drop_duplicates()
    out = config.ROOT / "data" / "new_rows" / "new_rows.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    new.to_csv(out, index=False)
    print("wrote", config.RAW_FILE, "and", out)
