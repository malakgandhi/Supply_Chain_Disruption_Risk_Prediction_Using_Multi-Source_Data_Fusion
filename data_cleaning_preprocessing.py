import pandas as pd
import numpy as np

# Create an outlier detection function
def find_outliers(data, col):
    q1 = data[col].quantile(0.25)
    q3 = data[col].quantile(0.75)

    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    data[col + "_Outlier"] = ((data[col] < lower_limit) | (data[col] > upper_limit)).astype(int)

    print(f"\nOutlier limits for {col}=")
    print(f"Lower bound: {lower_limit}")
    print(f"Upper Bound: {lower_limit}")

    print(f"Number of Outliers = {data[col + "_Outlier"].sum()}")

    return data

# Load the GSCPI dataset
gscpi = pd.read_csv('datasets/gscpi_data.csv')

# Remove values for 
gscpi.dropna(how='all')

gscpi = gscpi[['Date', 'GSCPI']]

# Convert data types of the attributes
gscpi['Date'] = pd.to_datetime(gscpi['Date'], errors="coerce")
gscpi['GSCPI'] = pd.to_numeric(gscpi['gscpi'], errors="coerce")

gscpi.dropna(subset=['Date'])

# Deal with the duplicates

print(f"GSCPI duplicated dates: {gscpi['Date'].duplicated().sum()}")

gscpi = gscpi.drop_duplicates(subset='Date', keep='last')

# Deal with missing values
print(f"GSCPI missing values: {gscpi.isnull().sum()}")

gscpi = gscpi.sort_values("Date")

gscpi['GSCPI'] = gscpi['GSCPI'].interpolate()

# Deal with outliers
gscpi = find_outliers(gscpi, 'GSCPI')

# We avoid removing outliers as extreme GSCPI values may represent real supply-chain values

# Load the commodity dataset
commodity = pd.read_csv('datasets/commodity.csv')

# Remove values for 
commodity.dropna(how='all')

commodity = commodity[['Date', 'Commodity_Index']]

# Convert data types of the attributes
commodity['Date'] = pd.to_datetime(commodity['Date'], errors="coerce")
commodity['Commodity_Index'] = pd.to_numeric(commodity['Commodity_Index'], errors="coerce")

commodity.dropna(subset=['Date'])

# Deal with the duplicates
print(f"GSCPI duplicated dates: {commodity['Date'].duplicated().sum()}")

commodity = commodity.drop_duplicates(subset='Date', keep='last')

# Deal with missing values
print(f"GSCPI missing values: {commodity.isnull().sum()}")

commodity = commodity.sort_values("Date")

commodity['GSCPI'] = commodity['GSCPI'].interpolate()

# Deal with outliers
commodity = find_outliers(commodity, 'Commodity_Index')

# Load the commodity dataset
freight = pd.read_csv('datasets/freight.csv')

# Remove values for 
freight.dropna(how='all')

freight = freight[['Date', 'Freight_Price']]

# Convert data types of the attributes
freight['Date'] = pd.to_datetime(freight['Date'].astype(str), format="%Y.%m", errors="coerce")
freight['Commodity_Index'] = pd.to_numeric(freight['Commodity_Index'], errors="coerce")
freight.dropna(subset=['Date'])

# Deal with the duplicates
print(f"GSCPI duplicated dates: {freight['Date'].duplicated().sum()}")
commodity = commodity.drop_duplicates(subset='Date', keep='last')

# Deal with missing values
print(f"GSCPI missing values: {freight.isnull().sum()}")
freight = freight.sort_values("Date")
freight['GSCPI'] = freight['GSCPI'].interpolate()

# Deal with outliers
freight = find_outliers(freight, 'Commodity_Index')

# Create a month column for each dataset
gscpi["Month"] = (gscpi["Date"].dt.to_period("M"))
commodity["Month"] = (commodity["Date"].dt.to_period("M"))
freight["Month"] = (freight["Date"].dt.to_period("M"))

gscpi_monthly = gscpi[
    [
        "Month",
        "GSCPI",
        "GSCPI_Outlier",
    ]
]

commodity_monthly = commodity[
    [
        "Month",
        "Commodity_Index",
        "Commodity_Index_Outlier",
    ]
]

freight_monthly = freight[
    [
        "Month",
        "Freight_Prices",
        "Freight_Prices_Outlier",
    ]
]

# Merge the monthly datasets
monthly_data = pd.merge(gscpi_monthly, commodity_monthly, on='Month', how='inner')
monthly_data = pd.merge(monthly_data, freight_monthly, on='Month', how='inner')

# Check duplicates after merging
monthly_data = monthly_data.drop_duplicates(subset="Month")

# Handle missing data after merging
print(f"\nMissing value after merging: {monthly_data.isnull().sum()}")

num_cols = [
    "GSCPI",
    "Commodity_Index",
    "Freight_Price"
]

monthly_data[num_cols] = monthly_data[num_cols].interpolate()

# Create GSCPI disruption threshold
gscpi_mean = gscpi['GSCPI'].mean()
gscpi_std = gscpi['GSCPI'].std()

threshold = gscpi_mean + 1.5 * gscpi_std

print(f"\nHistorical GSCPI mean: {gscpi_mean}")
print(f"\nHistorical GSCPI standard deviation: {gscpi_std}")
print(f"\nHistorical threshold: {threshold}")

# monthly disruption label
monthly_data['Disruption'] = (monthly_data['GSCPI'] >= threshold).astype(int)

# Conver monthly data to weekly data
week_dates = pd.date_range(start='2020-01-01', end='2023-12-31')
weekly_data = pd.DataFrame({"Week":week_dates})
weekly_data['Month'] = weekly_data['Week'].dt.to_period("M")
weekly_data = pd.merge(weekly_data, monthly_data, on="Month", how="left")

# Remove missing values in the weekly data
weekly_data[num_cols] = weekly_data[num_cols].ffill()

# Final check for duplicates
print(f"Duplicate weeks {weekly_data['Week'].duplicated().sum()}")
weekly_data = weekly_data.drop_duplicates(subset="Week")

# Final check for missing data
print(f"Final missing values: {weekly_data.isnull().sum()}")

# Display final data
print(f"\nFinal Weekly Dataset\n{weekly_data.head(20)}")
print(f"\nDataset shape: {weekly_data.shape}")
print(f"\nDataset shape: {weekly_data["Disruption"].value_counts()}")

# Save weekly data
weekly_data.to_csv("cleaned_datasets/weekly_economic_data.csv", index=False)

print("\nCleaned data saved successfully.")