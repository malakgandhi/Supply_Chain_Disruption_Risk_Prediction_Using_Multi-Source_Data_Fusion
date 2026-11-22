# Supply Chain Disruption Risk Analysis

This project combines global supply-chain indicators, port activity, and weather data to build a weekly dataset and examine disruption risk. The current preprocessing script assigns disruption labels from documented event windows and creates a next-month target. The modeling script is intended to compare Logistic Regression and XGBoost and save held-out predictions for the dashboard.

## Project contents

```text
.
├── datasets/
│   ├── commodity.csv
│   ├── freight.csv
│   ├── global_weather.csv
│   ├── gscpi_data.csv
│   └── port_data/
│       ├── port_data_2020_2021.csv
│       ├── port_data_2022_2023.csv
│       └── port_data_2024_2025.csv
├── cleaned_data/
│   ├── weekly_economic_data.csv
│   ├── weekly_target_review.csv
│   └── weekly_disruption_forecast.csv
├── static/style.css
├── templates/index.html
├── data_cleaning_preprocessing.py
├── threshold_checker.py
├── model_analysis.py
├── portwatch_download.py
├── weather_api_data_downloader.py
├── forecast_dashboard.py
└── forecast_server.py
```

## Datasets and sources

| File | Contents | Source / notes |
|---|---|---|
| `datasets/gscpi_data.csv` | Monthly Global Supply Chain Pressure Index (`date`, `GSCPI`) | Federal Reserve Bank of New York, [Global Supply Chain Pressure Index](https://www.newyorkfed.org/research/policy/gscpi#/overview). |
| `datasets/commodity.csv` | Monthly global all-commodities price index (`date`, `commodity_index`) | IMF series `PALLFNFINDEXM`, distributed by FRED: [Global Price Index of All Commodities](https://fred.stlouisfed.org/series/PALLFNFINDEXM). |
| `datasets/freight.csv` | Monthly water freight transportation price index (`date`, `freight_prices`) | U.S. Bureau of Labor Statistics series `WPU3013`, distributed by FRED: [Water Transportation of Freight](https://fred.stlouisfed.org/series/WPU3013). This is a U.S. producer price index, not a global container spot-rate series. |
| `datasets/port_data/port_data_2020_2021.csv` | Daily port calls, imports, and exports for selected ports | IMF PortWatch Daily Ports Data ArcGIS service. |
| `datasets/port_data/port_data_2022_2023.csv` | Same PortWatch fields for 2022–2023 | IMF PortWatch Daily Ports Data ArcGIS service. |
| `datasets/port_data/port_data_2024_2025.csv` | Same PortWatch fields for 2024–2025 | IMF PortWatch Daily Ports Data ArcGIS service. |
| `datasets/global_weather.csv` | Daily precipitation, weather code, wind gusts, and wind speed at selected port locations | Open-Meteo Historical Weather API. The downloader requests 2020-01-01 through 2025-12-31. |

The two FRED-based economic index files contain longer histories than the project period. The current scripts align them with the 2020–2025 analysis period. Cite the provider and series identifier when presenting results.

## Scripts

- `portwatch_download.py` downloads the configured port names for the three two-year periods and writes the CSV files under `datasets/port_data/`.
- `weather_api_data_downloader.py` retrieves daily weather observations for the configured locations and writes `datasets/global_weather.csv`.
- `data_cleaning_preprocessing.py` cleans the economic series, aggregates economic, PortWatch, and weather features to weeks, applies the event-window labels, and writes `cleaned_data/weekly_economic_data.csv`.
- `threshold_checker.py` is a separate diagnostic for GSCPI threshold breaches and event labels.
- `model_analysis.py` is intended to split observations chronologically, compare Logistic Regression and XGBoost, and write `cleaned_data/weekly_disruption_forecast.csv`.
- `forecast_dashboard.py` serves the saved predictions using `templates/index.html` and `static/style.css`.
- `forecast_server.py` is an alternate basic static-file server and is not required for the template-based forecast dashboard.

The disruption windows are entered directly in `data_cleaning_preprocessing.py`. Check the dates and citations for those event windows before using them as ground-truth labels. These labels reflect the chosen event definitions and should not be described as direct observations from the GSCPI series.

## Setup

Use Python 3.10 or newer. From PowerShell in the project folder, create and activate a virtual environment and install the packages:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pandas requests scikit-learn xgboost
```

If Python is not available as `python`, replace it with the path to your Python executable.

## Run order

The CSV files are already present in the project. Re-run the downloaders only when you want to refresh the source data; each downloader writes to its configured output path and replaces that output file.

```powershell
python portwatch_download.py
python weather_api_data_downloader.py
python data_cleaning_preprocessing.py
python model_analysis.py
python forecast_dashboard.py
```

Open `http://127.0.0.1:8000` after starting `forecast_dashboard.py`. Stop the local server with Ctrl+C.

### Current run note

At the time this README was prepared, `model_analysis.py` does not parse: Python reports an unexpected indent at line 24. Correct that indentation before running the modeling step. The existing forecast CSV and weekly outputs are saved artifacts; their presence does not mean the current scripts have been rerun successfully after the latest changes.

## Output interpretation

`weekly_economic_data.csv` is the model input and target table. `weekly_disruption_forecast.csv` contains held-out historical predictions, with `forecast_week`, `actual_disruption`, and `predicted_risk`. The dashboard explicitly presents these as historical test predictions, not as a live forecast.

The weekly series uses week-start dates. PortWatch and weather values are aggregated from daily records. Read the preprocessing code to confirm the exact aggregation, lag, and target timing used for a given output version.

## Limitations

- PortWatch coverage is limited to the ports configured in `portwatch_download.py`.
- Weather observations represent selected points near ports; they are not comprehensive local weather measurements for each whole port region.
- The freight series is a U.S. water transportation producer price index, so describe its geographic scope accurately.
- Event-window labels are manually specified and should be independently sourced and reviewed.
- Time-ordered evaluation is appropriate for forecasting, but metrics can be unstable when the positive disruption class is rare. Interpret them alongside class counts and simple baselines.
