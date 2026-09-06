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