import requests
import pandas as pd

locations = [
    ("Mumbai", 18.949824, 72.949991),
    ("Jebel Ali", 24.991210, 55.026913),  # Existing UAE weather point
    ("Dubai", 25.263000, 55.297000),      # Approx. Port Rashid area
    ("Sydney", -33.848858, 151.195510),
    ("Cape Town", -33.989456, 18.426968),
    ("Osaka", 34.622143, 135.454540),
    ("Singapore", 1.300527, 103.862564),
    ("Rio De Janeiro", -22.952549, -43.215027),
    ("Hong Kong", 22.319859, 114.198555),
    ("Shanghai", 31.247803, 121.500000),
    ("Vancouver", 49.244286, -123.133575),
    ("Copenhagen", 55.641476, 12.596349),
    ("Istanbul", 41.019330, 29.015692),
    ("Los Angeles", 33.736000, -118.263000),
    ("Seattle", 47.602000, -122.338000),
    ("Miami", 25.778000, -80.179000),
    ("New York-New Jersey", 40.684000, -74.140000),
]

params = {
    "latitude": ",".join(str(lat) for _,lat,_ in locations),
    "longitude": ",".join(str(lon) for _,_,lon in locations),
    "start_date": "2020-01-01",
    "end_date": "2025-12-31",
    "daily": ("precipitation_sum,weather_code,wind_gusts_10m_max,wind_speed_10m_max"),
    "timezone":"GMT",
    "wind_speed_unit":"kmh",
    "precipitation_unit":"mm"
}

response = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=60)
response.raise_for_status()

result = response.json()
results = result if type(result) == list else [result]

frames = []
for location, weather in zip(locations, results):
    name, latitude, longitude = location
    daily = pd.DataFrame(weather['daily'])
    daily['location_name'] = name
    daily['latitude'] = latitude
    daily['longitude'] = longitude
    frames.append(daily)

weather_ports = pd.concat(frames, ignore_index=True)

weather_ports.to_csv("datasets/global_weather.csv", index=False)