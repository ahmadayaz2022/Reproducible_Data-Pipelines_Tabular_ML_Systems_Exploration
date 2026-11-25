# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""All dataset-specific settings live here.

When you switch from the demo data to YOUR real dataset, this file (plus
`features.derive_columns`) is the main thing you edit. The rest of the code
reads these values instead of hard-coding column names.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- paths (raw is never overwritten; cleaned goes to a separate folder) ----
RAW_FILE = ROOT / "data" / "raw" / "service_requests_raw.csv"
CLEAN_FILE = ROOT / "data" / "cleaned" / "service_requests_clean.csv"
REJECTED_FILE = ROOT / "data" / "rejected" / "rejected_rows.csv"
DB_FILE = ROOT / "data" / "cleaned" / "requests.db"
FIG_DIR = ROOT / "outputs" / "figures"
REPORT_DIR = ROOT / "outputs" / "reports"
MODEL_DIR = ROOT / "outputs" / "models"
MODEL_FILE = MODEL_DIR / "pipeline.joblib"
SQL_DIR = ROOT / "sql"

# ---- column roles ----
ID_COL = "request_id"
DATE_COLS = ["created_at", "closed_at"]
NUMERIC_COLS = ["latitude", "longitude", "description_len", "num_updates"]
CATEGORICAL_COLS = ["agency", "category", "district", "channel", "priority"]

# ---- plausible ranges (anything outside becomes missing = outlier handling) ----
RANGES = {
    "latitude": (24.0, 37.0),
    "longitude": (60.0, 78.0),
    "description_len": (0, 5000),
    "num_updates": (0, 100),
}

# ---- Part B settings ----
TASK = "classification"          # or "regression"
TARGET = "sla_breached"          # 1 = request took more than SLA_HOURS to close
SLA_HOURS = 72
# columns that would leak the answer (they are only known AFTER the outcome)
LEAK_COLS = ["closed_at", "resolution_hours"]
SPLIT = "random"                 # "random" (stratified) or "time"
TEST_SIZE = 0.2
SEED = 42

# ---- Part A quality gate ----
MIN_PASS_RATE = 0.80
