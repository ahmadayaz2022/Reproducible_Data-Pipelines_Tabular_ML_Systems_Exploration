# Name: <YOUR NAME> | Roll no: <YOUR ROLL NO> | Date: <DATE>
"""Part B: split FIRST -> one Pipeline (features + preprocessing + model) -> compare -> test once -> save.

Run:  python -m src.train        (after python -m src.run_part_a)
"""
import json

import joblib
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src import config
from src.features import TIME_FEATURES, add_time_features

CLS = config.TASK == "classification"
INPUT_COLS = ["created_at"] + config.NUMERIC_COLS + config.CATEGORICAL_COLS   # what a NEW row must contain


def load_and_split():
    """Load cleaned data, drop leaking columns, and split BEFORE fitting anything."""
    df = pd.read_csv(config.CLEAN_FILE)
    y = df[config.TARGET]
    X = df[INPUT_COLS]                      # leak columns (closed_at, resolution_hours...) never enter X
    assert not set(config.LEAK_COLS) & set(X.columns), "leaking column in features!"
    if config.SPLIT == "time":              # train on the past, test on the future
        order = pd.to_datetime(df["created_at"]).argsort().to_numpy()
        cut = int(len(df) * (1 - config.TEST_SIZE))
        tr, te = order[:cut], order[cut:]
        return X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
    return train_test_split(X, y, test_size=config.TEST_SIZE, random_state=config.SEED,
                            stratify=y if CLS else None)


def make_pipeline(model):
    """features -> impute/scale/encode -> model, all in ONE object (fitted on training data only)."""
    num = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    cat = Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="unknown")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=20))])
    pre = ColumnTransformer([("num", num, config.NUMERIC_COLS + TIME_FEATURES),
                             ("cat", cat, config.CATEGORICAL_COLS)], remainder="drop")
    return Pipeline([("time", FunctionTransformer(add_time_features)), ("pre", pre), ("model", model)])


def candidate_models():
    s = config.SEED
    if CLS:
        return {"dummy (most frequent)": DummyClassifier(strategy="most_frequent"),
                "baseline: logistic regression": LogisticRegression(max_iter=1000),
                "random forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=5, random_state=s, n_jobs=-1),
                "gradient boosting": HistGradientBoostingClassifier(random_state=s)}
    return {"dummy (mean)": DummyRegressor(),
            "baseline: linear regression": LinearRegression(),
            "random forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=s, n_jobs=-1),
            "gradient boosting": HistGradientBoostingRegressor(random_state=s)}


SCORING = ({"f1": "f1", "roc_auc": "roc_auc", "pr_auc": "average_precision"} if CLS else
           {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"})
MAIN_METRIC = "pr_auc" if CLS else "rmse"
SEARCH_SCORING = "average_precision" if CLS else "neg_root_mean_squared_error"


def test_metrics(pipe, X, y):
    if CLS:
        pred, proba = pipe.predict(X), pipe.predict_proba(X)[:, 1]
        return {"precision": precision_score(y, pred, zero_division=0), "recall": recall_score(y, pred, zero_division=0),
                "f1": f1_score(y, pred, zero_division=0), "roc_auc": roc_auc_score(y, proba),
                "pr_auc": average_precision_score(y, proba)}
    pred = pipe.predict(X)
    return {"mae": mean_absolute_error(y, pred), "rmse": mean_squared_error(y, pred) ** 0.5, "r2": r2_score(y, pred)}


def main():
    config.REPORT_DIR.mkdir(parents=True, exist_ok=True); config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    X_train, X_test, y_train, y_test = load_and_split()
    print(f"train {len(X_train)} rows, test {len(X_test)} rows (test untouched until the end)")
    cv = (StratifiedKFold if CLS else KFold)(5, shuffle=True, random_state=config.SEED)

    # ---- compare every model on the SAME training data and SAME folds ----
    rows = []
    for name, model in candidate_models().items():
        res = cross_validate(make_pipeline(model), X_train, y_train, cv=cv, scoring=SCORING, n_jobs=1)
        rows.append({"model": name, **{m: res[f"test_{m}"].mean() * (-1 if m in ("mae", "rmse") else 1) for m in SCORING}})
    table = pd.DataFrame(rows).round(4)
    table.to_csv(config.REPORT_DIR / "model_comparison_cv.csv", index=False)
    print(table.to_string(index=False))

    # ---- small hyper-parameter search on training data only (best candidate family: random forest) ----
    grid = {"model__min_samples_leaf": [2, 5, 10], "model__max_depth": [None, 8, 14]}
    search = GridSearchCV(make_pipeline(candidate_models()["random forest"]), grid, cv=3,
                          scoring=SEARCH_SCORING, n_jobs=1)
    search.fit(X_train, y_train)
    tuned_cv = search.best_score_ * (-1 if not CLS else 1)
    print("tuned random forest", search.best_params_, round(tuned_cv, 4))

    # ---- choose the final model from CV only (never from the test set) ----
    pool = {r["model"]: r[MAIN_METRIC] for r in rows if r["model"] in ("random forest", "gradient boosting")}  # candidates only
    pool["random forest (tuned)"] = tuned_cv
    best_name = (max if CLS else min)(pool, key=pool.get)
    final = search.best_estimator_ if best_name == "random forest (tuned)" else make_pipeline(candidate_models()[best_name])
    final.fit(X_train, y_train)
    print("chosen:", best_name)

    # ---- the ONE look at the test set ----
    results = {"chosen_model": best_name, "test": {k: round(float(v), 4) for k, v in test_metrics(final, X_test, y_test).items()}}
    baseline_name = next(n for n in candidate_models() if n.startswith("baseline"))
    base = make_pipeline(candidate_models()[baseline_name]).fit(X_train, y_train)
    results["baseline_test"] = {k: round(float(v), 4) for k, v in test_metrics(base, X_test, y_test).items()}
    (config.REPORT_DIR / "test_results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

    # ---- error analysis ----
    pred = final.predict(X_test)
    err = X_test.copy(); err["actual"] = y_test.values; err["predicted"] = pred
    if CLS:
        err["p_breach"] = final.predict_proba(X_test)[:, 1].round(3)
        err["wrong"] = err["actual"] != err["predicted"]
        err[err["wrong"]].sort_values("p_breach").to_csv(config.REPORT_DIR / "misclassified_rows.csv", index=False)
        fig, ax = plt.subplots(figsize=(4.5, 4))
        ConfusionMatrixDisplay(confusion_matrix(y_test, pred), display_labels=["on time", "breached"]).plot(ax=ax, colorbar=False)
        ax.set_title("Confusion matrix (test set)"); fig.tight_layout()
        fig.savefig(config.FIG_DIR / "fig4_confusion_matrix.png", dpi=120); plt.close(fig)
        sub = err.groupby("category").apply(lambda g: pd.Series({
            "n": len(g), "error_rate": g["wrong"].mean(),
            "recall": recall_score(g["actual"], g["predicted"], zero_division=0),
            "precision": precision_score(g["actual"], g["predicted"], zero_division=0)}), include_groups=False).round(3)
    else:
        err["residual"] = err["actual"] - err["predicted"]
        err.reindex(err["residual"].abs().sort_values(ascending=False).index).head(50)\
           .to_csv(config.REPORT_DIR / "high_residual_rows.csv", index=False)
        fig, ax = plt.subplots(figsize=(6, 4)); ax.scatter(err["predicted"], err["residual"], s=6, alpha=.4); ax.axhline(0, c="k")
        ax.set(title="Residuals (test set)", xlabel="Predicted value", ylabel="Residual (actual - predicted)")
        fig.tight_layout(); fig.savefig(config.FIG_DIR / "fig4_residuals.png", dpi=120); plt.close(fig)
        err["abs_err"] = err["residual"].abs()
        sub = err.groupby("category")["abs_err"].agg(["count", "mean"]).round(3)
    sub.to_csv(config.REPORT_DIR / "subgroup_by_category.csv")
    print(sub)

    # ---- which features matter? (permutation importance on RAW input columns) ----
    imp = permutation_importance(final, X_test, y_test, n_repeats=5, random_state=config.SEED,
                                 scoring=SEARCH_SCORING)
    pd.Series(imp.importances_mean, index=X_test.columns).sort_values(ascending=False).round(4)\
      .to_csv(config.REPORT_DIR / "permutation_importance.csv", header=["importance"])

    # ---- save the single fitted pipeline + the columns a new row must have ----
    joblib.dump(final, config.MODEL_FILE)
    (config.MODEL_DIR / "input_columns.json").write_text(json.dumps(INPUT_COLS))
    print("saved", config.MODEL_FILE)


if __name__ == "__main__":
    main()
