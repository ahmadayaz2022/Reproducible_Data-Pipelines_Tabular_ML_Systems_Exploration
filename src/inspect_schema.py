# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Inspect the RAW file and write docs/schema.md (names, types, missing counts, examples).

Run: python -m src.inspect_schema
You must still ADD by hand: units and allowed values - the code cannot know them.
"""
import pandas as pd

from src import config

df = pd.read_csv(config.RAW_FILE)
lines = [f"# Raw data schema\n\nFile: `{config.RAW_FILE.name}` | rows: {len(df)} | columns: {df.shape[1]}\n",
         "| column | pandas type | missing | missing % | unique | example values | units / allowed values (fill in) |",
         "|---|---|---|---|---|---|---|"]
for c in df.columns:
    ex = ", ".join(map(str, df[c].dropna().astype(str).unique()[:3]))
    lines.append(f"| {c} | {df[c].dtype} | {int(df[c].isna().sum())} | {df[c].isna().mean() * 100:.1f} | "
                 f"{df[c].nunique()} | {ex} |  |")
lines.append(f"\nExact duplicate rows: {int(df.duplicated().sum())}")
(config.ROOT / "docs").mkdir(exist_ok=True)
(config.ROOT / "docs" / "schema.md").write_text("\n".join(lines) + "\n")
print("wrote docs/schema.md")
