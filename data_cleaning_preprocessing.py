import pandas as pd

# Create an outlier detection function
def find_outliers(data, col):
    q1 = data[col].quantile(0.25)
    q3 = data[col].quantile(0.75)

    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    data[col + "_outlier"] = ((data[col] < lower_limit) | (data[col] > upper_limit)).astype(int)

    print(f"\nOutlier limits for {col}=")
    print(f"Lower bound: {lower_limit}")
    print(f"Upper Bound: {upper_limit}")

    print(f"Number of Outliers = {data[col + '_outlier'].sum()}")

    return data

# Load the GSCPI dataset
gscpi = pd.read_csv('datasets/gscpi_data.csv')

# Remove values for 
gscpi = gscpi.dropna(how='all')

gscpi = gscpi[['date', 'GSCPI']]

# Convert data types of the attributes
gscpi['date'] = pd.to_datetime(gscpi['date'], errors="coerce")
gscpi['GSCPI'] = pd.to_numeric(gscpi['GSCPI'], errors="coerce")

gscpi = gscpi.dropna(subset=['date'])

# Deal with the duplicates

print(f"GSCPI duplicated dates: {gscpi['date'].duplicated().sum()}")

gscpi = gscpi.drop_duplicates(subset='date', keep='last')

# Deal with missing values
print(f"GSCPI missing values: {gscpi.isnull().sum()}")

gscpi = gscpi.sort_values("date")

gscpi['GSCPI'] = gscpi['GSCPI'].interpolate()

# Deal with outliers
gscpi = find_outliers(gscpi, 'GSCPI')

# We avoid removing outliers as extreme GSCPI values may represent real supply-chain values

# Load the commodity dataset
commodity = pd.read_csv('datasets/commodity.csv')

# Remove values for 
commodity = commodity.dropna(how='all')

commodity = commodity[['date', 'commodity_index']]

# Convert data types of the attributes
commodity['date'] = pd.to_datetime(commodity['date'], errors="coerce")
commodity['commodity_index'] = pd.to_numeric(commodity['commodity_index'], errors="coerce")

commodity = commodity.dropna(subset=['date'])

# Deal with the duplicates
print(f"Commodity duplicated dates: {commodity['date'].duplicated().sum()}")

commodity = commodity.drop_duplicates(subset='date', keep='last')

# Deal with missing values
print(f"Commodity missing values: {commodity.isnull().sum()}")

commodity = commodity.sort_values("date")

commodity['commodity_index'] = commodity['commodity_index'].interpolate()

# Deal with outliers
commodity = find_outliers(commodity, 'commodity_index')

# Load the commodity dataset
freight = pd.read_csv('datasets/freight.csv', dtype={'date':'string'})

# Remove values for 
freight = freight.dropna(how='all')

freight = freight[['date', 'freight_prices']]

# Convert data types of the attributes
freight['date'] = pd.to_datetime(freight['date'].astype(str), format="%Y-%m-%d", errors="coerce")
freight['freight_prices'] = pd.to_numeric(freight['freight_prices'], errors="coerce")
freight = freight.dropna(subset=['date', 'freight_prices'])

# Deal with the duplicates
print(f"Freight duplicated dates: {freight['date'].duplicated().sum()}")
freight = freight.drop_duplicates(subset='date', keep='last')

# Deal with missing values
print(f"Freight missing values: {freight.isnull().sum()}")
freight = freight.sort_values("date")
freight['freight_prices'] = freight['freight_prices'].interpolate()

# Deal with outliers
freight = find_outliers(freight, 'freight_prices')

# Create a month column for each dataset
gscpi["month"] = (gscpi["date"].dt.to_period("M"))
commodity["month"] = (commodity["date"].dt.to_period("M"))
freight["month"] = (freight["date"].dt.to_period("M"))

gscpi_monthly = gscpi[
    [
        "month",
        "GSCPI",
        "GSCPI_outlier",
    ]
]

commodity_monthly = commodity[
    [
        "month",
        "commodity_index",
        "commodity_index_outlier",
    ]
]

freight_monthly = freight[
    [
        "month",
        "freight_prices",
        "freight_prices_outlier",
    ]
]

# Merge the monthly datasets
monthly_data = pd.merge(gscpi_monthly, commodity_monthly, on='month', how='inner')
monthly_data = pd.merge(monthly_data, freight_monthly, on='month', how='inner')

# Check duplicates after merging
monthly_data = monthly_data.drop_duplicates(subset="month")

# Handle missing data after merging
print(f"\nMissing value after merging: {monthly_data.isnull().sum()}")

num_cols = ["GSCPI","commodity_index","freight_prices"]

monthly_data[num_cols] = monthly_data[num_cols].interpolate()

# Average GSCPI by month for the project period.
# GSCPI remains a predictor; documented event windows define the target.
monthly_gscpi = (gscpi[gscpi["date"].between("2020-01-01", "2025-12-31")].groupby("month", as_index=False).agg(GSCPI=("GSCPI", "mean")))

# Documented event windows used to create the monthly target.
# These are month-level project windows; verify them against the sources you cite.
events = [
    ("2020-04", "2020-06"),  # COVID-19 supply-chain shock period
    ("2021-03", "2021-03"),  # Ever Given blockage of the Suez Canal
    ("2021-07", "2021-09"),  # Semiconductor shortage period
    ("2021-10", "2021-12"),  # Global port congestion period
    ("2022-03", "2022-06"),  # Shanghai COVID-19 lockdown and logistics disruption
    ("2023-11", "2025-07"),  # Red Sea/Suez rerouting crisis; documented continuation into July 2025
    ("2024-01", "2024-04"),  # Panama Canal drought-related transit restrictions
    ("2024-10", "2024-10"),  # U.S. East/Gulf Coast port strike; localized to affected U.S. ports
    ("2025-04", "2025-05"),  # Tariff-related shipping disruption and blank sailings
]

monthly_gscpi["documented_event"] = 0

for start, end in events:
    start_month = pd.Period(start, freq="M")
    end_month = pd.Period(end, freq="M")
    in_window = monthly_gscpi["month"].between(start_month, end_month)
    monthly_gscpi.loc[in_window, "documented_event"] = 1

monthly_gscpi["Disruption"] = monthly_gscpi["documented_event"].astype(int)
monthly_gscpi["target_next_month"] = monthly_gscpi["Disruption"].shift(-1)

# Replace monthly GSCPI values and labels in the merged monthly dataset
monthly_data = monthly_data.drop(columns=["GSCPI"], errors="ignore")
monthly_data = monthly_data.merge(
    monthly_gscpi[["month", "GSCPI", "Disruption", "target_next_month"]],
    on="month",
    how="left",
)

# Conver monthly data to weekly data
week_dates = pd.date_range(start='2020-01-01', end='2025-12-31', freq=" W-MON")
weekly_data = pd.DataFrame({"week":week_dates})
weekly_data['month'] = weekly_data['week'].dt.to_period("M")
weekly_data = pd.merge(weekly_data, monthly_data, on="month", how="left")

# Remove missing values in the weekly data
weekly_data[num_cols] = weekly_data[num_cols].ffill()

#Load the datasets of the ports
port_data = pd.concat([
    pd.read_csv("datasets/port_data/port_data_2020_2021.csv"),
    pd.read_csv("datasets/port_data/port_data_2022_2023.csv"),
    pd.read_csv("datasets/port_data/port_data_2024_2025.csv")
], ignore_index=True)

port_data["week"] = pd.to_datetime(port_data["date"]).dt.to_period("W-SUN").dt.start_time

weekly_ports = (port_data.groupby(["week", "portid"])[["portcalls", "import", "export"]].sum().unstack("portid", fill_value=0))

weekly_ports.columns = [f"{measure}_{port}" for measure, port in weekly_ports.columns]
weekly_ports = weekly_ports.reset_index()

weekly_data = weekly_data.merge(weekly_ports, on="week", how="left")

# Load the global weather dataset
weather = pd.read_csv("datasets/global_weather.csv")

weather["week"] = (pd.to_datetime(weather["time"]).dt.to_period("W-SUN").dt.start_time)
weather_cols = ["precipitation_sum", "wind_gusts_10m_max", "wind_speed_10m_max"]

weekly_weather = (weather.groupby(["week", "location_name"])[weather_cols].mean().unstack("location_name"))
weekly_weather.columns = [
    f"{measure}_{location.replace(' ', '_').replace('-', '_')}"
    for measure, location in weekly_weather.columns
]
weekly_weather = weekly_weather.reset_index()

weekly_data = weekly_data.merge(weekly_weather, on="week", how="left")

port_feature_cols = [col for col in weekly_data.columns if col.startswith(("portcalls_", "import_", "export_"))]

weekly_data = weekly_data.sort_values("week")

weekly_data[port_feature_cols] = (weekly_data[port_feature_cols].shift(1))

portcall_columns = [column for column in weekly_data.columns if column.startswith("portcalls_")]

weekly_data["total_portcalls"] = weekly_data[portcall_columns].sum(axis=1)

weekly_data["previous_8_week_average"] = (weekly_data["total_portcalls"].shift(1).rolling(window=8, min_periods=8).mean())


# Final check for duplicates
print(f"Duplicate weeks {weekly_data['week'].duplicated().sum()}")
weekly_data = weekly_data.drop_duplicates(subset="week")

# Final check for missing data
print(f"Final missing values: {weekly_data.isnull().sum()}")

# Display final data
print(f"\nFinal Weekly Dataset\n{weekly_data.head(20)}")
print(f"\nDataset shape: {weekly_data.shape}")
print(f"\nDataset shape: {weekly_data['Disruption'].value_counts(dropna=False)}")
print(weekly_data.loc[weekly_data["Disruption"] == 1].groupby(weekly_data["week"].dt.year).size())

# Save weekly data
weekly_data.to_csv("cleaned_data/weekly_economic_data.csv", index=False)

print("\nCleaned data saved successfully.")
