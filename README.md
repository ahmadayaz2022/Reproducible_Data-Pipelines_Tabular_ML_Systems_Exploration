# Reproducible Data Pipeline & Tabular ML  (Name: Ahmad Ayaz | Trainee ID TRN-2026-000371)

## Setup and run
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.make_demo_data        # DEMO ONLY - skip when using real data (put the file in data/raw/)
python -m src.inspect_schema        # writes docs/schema.md
python -m src.run_part_a            # Part A: validate, clean, summaries, charts, SQLite, metrics.json
python -m src.train                 # Part B: split, compare models, error analysis, save pipeline
python -m src.predict data/new_rows/new_rows.csv outputs/reports/predictions.csv
python -m src.demo_quality_gate     # Part A bonus: gate fails on corrupted copy, passes on real data
pytest -q                           # tests
python exploration/c1_feed_index.py # Part C1 experiment
