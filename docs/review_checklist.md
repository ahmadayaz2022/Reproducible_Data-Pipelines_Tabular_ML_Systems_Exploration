# Code review checklist
- Does it do what the PR description says? Is there a test that would fail without it?
- Data: is raw data left untouched? Any hard-coded paths or secrets?
- ML: is anything fitted (scaler, imputer, encoder) before the train/test split? Is the test set used only once?
- Readability: clear names, docstrings, no dead code.
- Errors: what happens with missing or wrong input?
- Size: is the PR small enough to review in about 20 minutes?
