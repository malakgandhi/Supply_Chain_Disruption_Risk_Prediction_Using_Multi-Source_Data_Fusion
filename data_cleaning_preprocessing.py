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

gscpi.dropna(how='all')

gscpi = gscpi[['Date', 'GSCPI']]

# Convert data types of the attributes
gscpi['Date'] = pd.to_datetime(gscpi['Date'], errors="coerce")
gscpi['GSCPI'] = pd.to_numeric(gscpi['gscpi'], errors="coerce")

gscpi.dropna(subset=['Date'])

