import pandas as pd

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

# Clean the date columns
storm_data = pd.to_datetime(storm_data["BEGIN_DATE_TIME"], errors="coerce")

# Handling missing values
storm_data["INJURIES_DIRECT"] = storm_data["INJURIES_DIRECT"].fillna(0)
storm_data["DEATHS_DIRECT"] = storm_data["DEATHS_DIRECT"].fillna(0)

'''
Keep latitude and longitude data as unknown to prevent misclassification onto incorrect coordinates.
'''

# Create a severe disaster weather map
severe_events = [
    "Hurricane",
    "Tropical Storm",
    "Flood",
    "Flash Flood",
    "Storm Surge/Tide",
    "High Wind",
    "Thunderstorm Wind",
    "Tornado",
    "Blizzard",
    "Winter Storm"
]

storm_data["SEVERE_EVENT"] = storm_data["EVENT_TYPE"].isin(severe_events).astype(int)

# Convert date to week
storm_data['week'] = storm_data["BEGIN_DATE_TIME"].dt.to_period("W-MON").apply(lambda x: x.stat_time)

# Create weekly weather data
weekly_weather = storm_data.groupby('Week').agg(
    Storm_Count = ("EVENT_ID", "count"),
    Severe_Storm_Count = ("SEVERE_EVENT", "count"),
    Total_Injuries = ("INJURIES_DIRECT", "sum"),
    Total_Deaths = ("DEATHS_DIRECT", "sum")
).reset_index()

# Create weather event flag
weakly_weather["Weather_Event_Flag"] = (weekly_weather["Storm_Count"] > 0).astype(int)

# Final cleaning
weekly_weather = weekly_weather.sort_values("Week")

print("\nMissing Values:", weekly_weather.isnull().sum())
print("\nFinal Shape:", weekly_weather.shape)
print("\nFirst 10 rows:\n", weekly_weather.head(10))
