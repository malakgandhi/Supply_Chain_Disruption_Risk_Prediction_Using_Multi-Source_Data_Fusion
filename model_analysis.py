import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier


# Load and sort the weekly data
df = pd.read_csv("cleaned_data/weekly_economic_data.csv")
df["week"] = pd.to_datetime(df["week"])
df = df.sort_values("week").reset_index(drop=True)

if "Disruption" not in df.columns:
    raise ValueError("The cleaned CSV must contain a 'Disruption' column.")

# Use this week's data to predict next week's disruption label
y = df["Disruption"].shift(-1)

# Use numeric columns as predictors, excluding target and label columns
features = df.select_dtypes(include="number").drop(columns="Disruption")
    features = features.drop(columns="target_next_month")
if "target_next_week" in features.columns:
    features = features.drop(columns="target_next_week")

valid = y.notna() & features.notna().all(axis=1)
x = features.loc[valid]
y = y.loc[valid].astype(int)
weeks = df.loc[valid, "week"]
current_disruption = df.loc[valid, "Disruption"].astype(int)

print("Weekly next-week target counts:")
print(y.value_counts().sort_index())
print(f"\nWeekly observations: {len(x)}")
print(f"Predictor columns: {x.shape[1]}")

# Keep the latest 20% of weeks for the final test
split = int(len(x) * 0.8)
x_train = x.iloc[:split]
x_test = x.iloc[split:]
y_train = y.iloc[:split]
y_test = y.iloc[split:]

if y_train.nunique() < 2:
    raise ValueError("The training period needs both target classes.")

# Compare models using chronological cross-validation
logistic = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight="balanced", max_iter=2000),
)

xgboost = XGBClassifier(
    n_estimators=100,
    max_depth=2,
    learning_rate=0.05,
    eval_metric="logloss",
    random_state=42,
)

time_cv = TimeSeriesSplit(n_splits=5)
logistic_ap = cross_val_score(
    logistic, x_train, y_train, cv=time_cv, scoring="average_precision"
).mean()
xgboost_ap = cross_val_score(
    xgboost, x_train, y_train, cv=time_cv, scoring="average_precision"
).mean()

print(f"\nLogistic Regression CV average precision: {logistic_ap:.3f}")
print(f"XGBoost CV average precision: {xgboost_ap:.3f}")

if logistic_ap >= xgboost_ap:
    selected_model = logistic
    selected_name = "Logistic Regression"
else:
    selected_model = xgboost
    selected_name = "XGBoost"

print(f"Selected model: {selected_name}")

# Fit both models so they can be compared on the same future test weeks
logistic.fit(x_train, y_train)
xgboost.fit(x_train, y_train)

logistic_probability = logistic.predict_proba(x_test)[:, 1]
xgboost_probability = xgboost.predict_proba(x_test)[:, 1]
persistence_probability = current_disruption.iloc[split:].to_numpy()
selected_probability = selected_model.predict_proba(x_test)[:, 1]

print("\nFinal chronological test results")
print("Test target counts:")
print(y_test.value_counts().sort_index())

if y_test.nunique() < 2:
    print("The test set has only one class, so these test metrics aren't informative.")
else:
    threshold = 0.5
    predictions = (selected_probability >= threshold).astype(int)

    print(f"\nSelected model: {selected_name}")
    print(f"Decision threshold: {threshold}")
    print("Confusion matrix (rows = actual, columns = predicted; order 0, 1):")
    print(confusion_matrix(y_test, predictions))
    print(f"Precision:{precision_score(y_test, predictions, zero_division=0):.3f}")
    print(f"Recall:{recall_score(y_test, predictions, zero_division=0):.3f}")
    print(f"F1 score:{f1_score(y_test, predictions, zero_division=0):.3f}")
    print(f"ROC-AUC:{roc_auc_score(y_test, selected_probability):.3f}")
    print(f"Average precision:{average_precision_score(y_test, selected_probability):.3f}")

    importance = permutation_importance(selected_model, x_test, y_test, scoring="average_precision", n_repeats=20, random_state=42,)

    importance_df = pd.DataFrame()
    importance_df["feature"] = x.columns
    importance_df["importance"] = importance.importances_mean
    importance_df = importance_df.sort_values("importance", ascending=False)

    print("\nTop 10 exploratory feature importances:")
    print(importance_df.head(10).to_string(index=False))

    # Also report the baselines on the same final test period.
    print(f"Logistic Regression AUROC: {roc_auc_score(y_test, logistic_probability):.3f}")
    print(f"Logistic Regression average precision: {average_precision_score(y_test, logistic_probability):.3f}")
    print(f"XGBoost AUROC: {roc_auc_score(y_test, xgboost_probability):.3f}")
    print(f"XGBoost average precision: {average_precision_score(y_test, xgboost_probability):.3f}")
    print(f"Persistence AUROC: {roc_auc_score(y_test, persistence_probability):.3f}")
    print(f"Persistence average precision: {average_precision_score(y_test, persistence_probability):.3f}")

# Save the selected model's predictions for the held-out weeks
forecast = pd.DataFrame()
forecast["forecast_week"] = weeks.iloc[split:].reset_index(drop=True) + pd.Timedelta(weeks=1)
forecast["actual_disruption"] = y_test.reset_index(drop=True)
forecast["predicted_risk"] = selected_probability
forecast.to_csv("cleaned_data/weekly_disruption_forecast.csv", index=False)

print("\nSaved test-period forecast to cleaned_data/weekly_disruption_forecast.csv")
