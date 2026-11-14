import pandas as pd

gscpi = pd.read_csv('datasets/gscpi_data.csv')
gscpi["date"] = pd.to_datetime(gscpi["date"])
gscpi["GSCPI"] = pd.to_numeric(gscpi["GSCPI"])

gscpi = gscpi.dropna(subset=["date", "GSCPI"])

baseline = gscpi.loc[gscpi["date"] < "2020-01-01", "GSCPI"]
threshold = baseline.mean() + 1.5 * baseline.std()

gscpi["month"] = gscpi["date"].dt.to_period("M")
monthly = (
    gscpi[gscpi["date"].between("2020-01-01", "2023-12-31")]
    .groupby("month", as_index=False)
    .agg(GSCPI=("GSCPI", "mean"))
)
monthly["gscpi_breach"] = (monthly["GSCPI"] >= threshold).astype(int)

events = [
    ("2020-04", "2020-06"),  # COVID supply shock
    ("2021-03", "2021-03"),  # Suez Canal blockage
    ("2021-07", "2021-09"),  # Semiconductor shortage
    ("2021-10", "2021-12"),  # Port congestion
    ("2023-10", "2023-12"),  # Red Sea disruption
]

monthly["documented_event"] = 0

for start, end in events:
    start_month = pd.Period(start, freq="M")
    end_month = pd.Period(end, freq="M")
    in_window = monthly["month"].between(start_month, end_month)
    monthly.loc[in_window, "documented_event"] = 1

monthly["disruption"] = (
    monthly["documented_event"] & monthly["gscpi_breach"]
).astype(int)

monthly["target_next_month"] = monthly["disruption"].shift(-1)

print("Threshold:", round(threshold, 3))
print(monthly[[
    "month", "GSCPI", "gscpi_breach",
    "documented_event", "disruption", "target_next_month"
]].to_string(index=False))

print("\nPositive target months:")
print(monthly.loc[
    monthly["target_next_month"] == 1,
    ["month", "target_next_month"]
].to_string(index=False))