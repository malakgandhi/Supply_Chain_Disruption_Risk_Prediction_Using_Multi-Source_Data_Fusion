import pandas as pd
import os

# Load the 4 files

files = [
    "datasets/storm_events/storm_2020.csv",
    "datasets/storm_events/storm_2021.csv",
    "datasets/storm_events/storm_2022.csv",
    "datasets/storm_events/storm_2023.csv"
]

data = []

for file in files:
    df = pd.read_csv(file, low_memory=False)
    data = df.append(df)

# Combine all the years
storm_data = pd.concat(data, ignore_index=True)
print("Original Shape:", storm_data.shape)

# Keep required columns
cols = [
    "EVENT_ID",
    "BEGIN_DATE_TIME",
    "EVENT_TYPE",
    "STATE",
    "CZ_NAME",
    "BEGIN_LAT",
    "BEGIN_LON",
    "INJURIES_DIRECT",
    "DEATHS_DIRECT"
]

storm_data = storm_data[cols]

# Remove duplicates
print("Number of duplicate Rows:",storm_data.duplicated().sum())

storm_data = storm_data.drop_duplicates()
storm_data = storm_data.drop_duplicates(subset="EVENT_ID")