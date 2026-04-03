"""
Sprint 1: Weather Data Pipeline
================================
Downloads historical hourly weather data from Open-Meteo API
for Fremont, CA (latitude: 37.5485, longitude: -121.9886).

Signals collected:
  - shortwave_radiation       : Global Horizontal Irradiance (GHI), W/m²
  - temperature_2m            : Air temperature at 2m, °C
  - cloudcover                : Total cloud cover, %
  - direct_normal_irradiance  : DNI, W/m²
  - diffuse_radiation         : DHI, W/m²

Output: stage1_solar_grid/data/raw/weather_fremont.csv
"""

import requests
import pandas as pd
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
LAT        = 37.5485
LON        = -121.9886
START_DATE = "2022-01-01"
END_DATE   = "2023-12-31"   # 2 years of history for model training
LOCATION   = "Fremont_CA"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "weather_fremont.csv"

# ── API Call ───────────────────────────────────────────────────────────────────
def fetch_weather(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude"       : lat,
        "longitude"      : lon,
        "start_date"     : start,
        "end_date"       : end,
        "hourly"         : [
            "shortwave_radiation",
            "direct_normal_irradiance",
            "diffuse_radiation",
            "temperature_2m",
            "cloudcover",
            "relative_humidity_2m",
            "windspeed_10m",
        ],
        "timezone"       : "America/Los_Angeles",
    }

    print(f"Fetching weather data: {start} to {end} ...")
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


# ── Parse to DataFrame ─────────────────────────────────────────────────────────
def parse_to_dataframe(data):
    hourly = data["hourly"]
    df = pd.DataFrame(hourly)

    # Rename columns to cleaner names
    df = df.rename(columns={
        "time"                       : "timestamp",
        "shortwave_radiation"        : "ghi_wm2",
        "direct_normal_irradiance"   : "dni_wm2",
        "diffuse_radiation"          : "dhi_wm2",
        "temperature_2m"             : "temp_c",
        "cloudcover"                 : "cloud_pct",
        "relative_humidity_2m"       : "humidity_pct",
        "windspeed_10m"              : "wind_ms",
    })

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp").sort_index()

    print(f"Rows: {len(df)}")
    print(f"Date range: {df.index[0]} → {df.index[-1]}")
    print(f"Missing values:\n{df.isnull().sum()}")

    return df


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    raw = fetch_weather(LAT, LON, START_DATE, END_DATE)
    df  = parse_to_dataframe(raw)

    df.to_csv(OUTPUT_PATH)
    print(f"\nSaved to: {OUTPUT_PATH}")
    print(df.head())
