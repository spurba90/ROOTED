# preethi - dowloading historical climate data from nasa power

# test request !!! 
import pandas as pd
import requests

# location we agreed on: ames, iowa (from story county)
LATITUDE = 42.03
LONGITUDE = -93.62

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point" # daily api endpoint

# one month of historical climate data
parameters = {
    "parameters": "T2M,PRECTOTCORR",
    "community": "AG",
    "longitude": LONGITUDE,
    "latitude": LATITUDE,
    "start": "20050101",
    "end": "20251231",
    "format": "JSON",
}

response = requests.get(BASE_URL, params=parameters, timeout=60)
response.raise_for_status() # sending the request to NASA

data = response.json()

climate_data = data["properties"]["parameter"] # climate vars

df = pd.DataFrame(climate_data)
df.index.name = "date"
df = df.reset_index()

print(df.head())
print("\nDataset shape:", df.shape)

# output
'''
       date   T2M  PRECTOTCORR
0  20240101 -3.37         0.00
1  20240102 -1.54         0.00
2  20240103 -2.23         0.00
3  20240104 -3.26         0.00
4  20240105 -1.65         0.02

Dataset shape: (31, 3) '''


from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
output_file = PROJECT_ROOT / "data" / "raw" / "nasa_power_ames_iowa_2005_2025.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)
print(f"\nSaved NASA data to: {output_file}")


print("\nTotal daily records:", len(df)) # daily observations nasa returned
print("\nMissing values by column:")
print(df.isna().sum())
print("\nFirst date:", df["date"].iloc[0]) # first iloc
print("Last date:", df["date"].iloc[-1]) # last iloc

'''
Total daily records: 7670

Missing values by column:
date           0
T2M            0
PRECTOTCORR    0
dtype: int64

First date: 20050101
Last date: 20251231 '''