from pathlib import Path

import pandas as pd
import requests


url = (
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/"
    "arcgis/rest/services/Daily_Ports_Data/FeatureServer/0/query"
)

year_ranges = [
    (2020,2021),
    (2022,2023),
    (2024,2025)
]

# City names represented by the existing 2020-2023 PortWatch files.
# Sydney and Vancouver each have multiple PortWatch IDs, but filtering by name
# includes the corresponding rows for each city.
port_names = [
    "Mumbai-Jawaharlal Nehru (Nhava Sheva)",
    "Dubai",
    "Jebel Ali",
    "Sydney",
    "Cape Town",
    "Osaka",
    "Singapore",
    "Rio De Janeiro",
    "Hong Kong",
    "Shanghai",
    "Vancouver",
    "København",
    "Istanbul",
    "Los Angeles-Long Beach",
    "Seattle",
    "Miami",
    "New York-New Jersey"
]

port_name_filter = ",".join(f"'{name}'" for name in port_names)
output_folder = Path("datasets/port_data")


def request_json(params):
    """Request one page from the PortWatch ArcGIS service."""
    try:
        response = requests.get(url, params=params, timeout=60)
        result = response.json()
    except requests.RequestException as error:
        raise RuntimeError(f"PortWatch request failed: {error}") from error
    except ValueError as error:
        raise RuntimeError(
            f"PortWatch returned a non-JSON response:\n{response.text[:1000]}"
        ) from error

    if response.status_code >= 400 or "error" in result:
        error_details = result.get("error", {})
        raise RuntimeError(
            "PortWatch query failed.\n"
            f"HTTP status: {response.status_code}\n"
            f"Message: {error_details.get('message', 'No message returned')}\n"
            f"Details: {error_details.get('details', [])}\n"
            f"Query: {params.get('where')}"
        )

    return result


def download_period(start_year, end_year):
    """Download and save all records for one year range."""
    where_clause = (
        f"portname IN ({port_name_filter}) "
        f"AND year >= {start_year} AND year <= {end_year}"
    )

    params = {
        "where": where_clause,
        "outFields": (
            "year,month,day,portid,portname,"
            "portcalls,import,export"
        ),
        "orderByFields": "year,month,day,portname",
        "returnGeometry": "false",
        "resultRecordCount": 1000,
        "f": "json",
    }

    records = []
    offset = 0

    while True:
        params["resultOffset"] = offset
        print(
            f"Requesting {start_year}-{end_year}, "
            f"starting at row {offset}"
        )

        page = request_json(params)
        features = page.get("features", [])

        records.extend(feature["attributes"] for feature in features)
        print(f"Downloaded {len(records)} rows for {start_year}-{end_year}")

        if not page.get("exceededTransferLimit", False) or not features:
            break

        offset += len(features)

    if not records:
        print(f"No records found for {start_year}-{end_year}.")
        return

    data = pd.DataFrame(records)

    data["date"] = pd.to_datetime(
        data[["year", "month", "day"]],
        errors="coerce",
    )

    data = data.dropna(subset=["date"])
    data = data.drop_duplicates(subset=["date", "portid"])
    data = data.sort_values(
        ["date", "portname", "portid"]
    ).reset_index(drop=True)

    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"port_data_{start_year}_{end_year}.csv"
    data.to_csv(output_path, index=False)

    found_names = sorted(data["portname"].dropna().unique())
    found_ids = sorted(data["portid"].dropna().unique())

    print(f"Saved {data.shape} to {output_path}")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")
    print(f"Port names found: {found_names}")
    print(f"Port IDs found: {found_ids}")


if __name__ == "__main__":
    for start_year, end_year in year_ranges:
        download_period(start_year, end_year)