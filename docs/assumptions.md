# Assumptions, limitations, risks and model card  (fill in with YOUR real dataset)

## Cleaning assumptions (Part A)
- Rows with a missing/unparseable start date or an end date before the start date are REJECTED (saved in `data/rejected/`), not fixed: we cannot know the true date.
- Out-of-range values (e.g. latitude 999) are set to missing, not deleted: the rest of the row is still useful.
- Missing categories become the level `unknown`; missing numbers are LEFT missing and imputed inside the ML pipeline from training data only (imputing in Part A would leak test information).
- Exact duplicates are removed (keep first).
- What I chose NOT to fix and why: <e.g. IQR outliers in resolution time - they are real slow cases, not errors>.

## Model card (Part B)
- **Task / target:** <...>  **Intended use:** <who uses it, for what decision>
- **Leaking columns excluded:** closed_at, resolution_hours (known only after the outcome).
- **Split:** <random stratified / time-based> because <reason>. Test set used once at the end.
- **Metrics:** PR-AUC, F1, recall because <the positive class is the costly one / imbalance>. Accuracy alone is misleading.
- **Limitations:** <data from one period/city; categories unseen at training; noisy dates ...>
- **Risks:** <unfair treatment of districts/categories, over-trusting predictions, data drift ...>
- **Not intended for:** <...>
