# Reproducible Data Pipeline & Tabular ML  (Name: Ahmad Ayaz | Trainee ID TRN-2026-000371)

## Setup and run
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.make_demo_data        
python -m src.inspect_schema      
python -m src.run_part_a            
python -m src.predict data/new_rows/new_rows.csv outputs/reports/predictions.csv
python -m src.demo_quality_gate    
pytest -q                           # tests
python exploration/c1_feed_index.py # Part C1 experiment
