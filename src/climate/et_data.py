# preethi et data
from pathlib import Path

import pandas as pd
import requests

# ames, iowa location
LATITUDE = 42.03
LONGITUDE = -93.62
START_DATE = "20050101"
END_DATE = "20251231"

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

params = {
    "parameters": "EVPTRNS",
    "community": "AG",
    "longitude": LONGITUDE,
    "latitude": LATITUDE,
    "start": START_DATE,
    "end": END_DATE,
    "format": "JSON",
}

response = requests.get(URL, params=params, timeout=120) # daily et energy-flux data
response.raise_for_status()
data = response.json()

metadata = data["parameters"]["EVPTRNS"]
print("Parameter:", metadata["longname"])
print("Unit:", metadata["units"])

if metadata["units"] != "MJ/m^2/day":
    raise ValueError("Unexpected ET units")

# convert daily obs into df
daily_values = data["properties"]["parameter"]["EVPTRNS"]

df = pd.DataFrame(list(daily_values.items()),columns=["date", "EVPTRNS"])
df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
df["EVPTRNS"] = pd.to_numeric(df["EVPTRNS"], errors="coerce")

# replace missing values
df["EVPTRNS"] = df["EVPTRNS"].replace(-999, float("nan"))

# unique dates
if df["date"].duplicated().any():
    raise ValueError("Duplicate dates found")

expected_dates = pd.date_range(start=pd.to_datetime(START_DATE, format="%Y%m%d"), end=pd.to_datetime(END_DATE, format="%Y%m%d"), freq="D")
missing_dates = expected_dates.difference(df["date"])

if len(missing_dates) > 0:
    raise ValueError(f"Missing {len(missing_dates)} dates")

# missing msmts
missing_values = df["EVPTRNS"].isna().sum()
print("Missing ET values:", missing_values)

if missing_values > 0:
    raise ValueError("Missing ET measurements found")

# Save cleaned daily ET observations
project_root = Path(__file__).resolve().parents[2]

output_file = (project_root / "data" / "processed" / "ames_daily_et_2005_2025.csv")
output_file.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_file, index=False, date_format="%Y%m%d")

print("\nFirst five rows:")
print(df.head())
print("\nTotal records:", len(df))
print("First date:", df["date"].min().date())
print("Last date:", df["date"].max().date())
print("Saved to:", output_file)