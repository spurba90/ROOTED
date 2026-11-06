# preethi - finding anomalies
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
input_file = (project_root / "data" / "processed" / "ames_growing_seasons_2005_2025.csv")
output_file = (project_root / "data" / "processed" / "ames_climate_anomalies_2005_2025.csv")
df = pd.read_csv(input_file)

# the expected columns
required_columns = {
    "year",
    "avg_temp_c",
    "total_precip_mm",
    "days_observed"
}

if not required_columns.issubset(df.columns):
    raise ValueError("Missing required climate columns")


expected_years = set(range(2005, 2026))

if set(df["year"]) != expected_years or len(df) != 21:
    raise ValueError("Unexpected year coverage")

if not (df["days_observed"] == 153).all():
    raise ValueError("Incomplete growing seasons found")

if df[["avg_temp_c", "total_precip_mm"]].isna().any().any():
    raise ValueError("Missing climate values found")

# 2005–2025 baseline averages
baseline_temp = df["avg_temp_c"].mean()
baseline_precip = df["total_precip_mm"].mean()

# each year's difference from baseline
df["temp_anomaly_c"] = df["avg_temp_c"] - baseline_temp
df["precip_anomaly_mm"] = df["total_precip_mm"] - baseline_precip

# precipitation's percentage difference
df["precip_anomaly_pct"] = (df["precip_anomaly_mm"] / baseline_precip) * 100

# rounding results
df[
    ["temp_anomaly_c", "precip_anomaly_mm", "precip_anomaly_pct"]
] = df[
    ["temp_anomaly_c", "precip_anomaly_mm", "precip_anomaly_pct"]
].round(2)


output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("Historical baseline (2005–2025):")
print(f"Average temperature: {baseline_temp:.2f} °C")
print(f"Average precipitation: {baseline_precip:.2f} mm")

print("\nFirst five seasonal anomalies:")
print(df.head().to_string(index=False))

print("\nWarmest anomaly:")
print(df.loc[df["temp_anomaly_c"].idxmax(),
             ["year", "temp_anomaly_c"]])

print("\nDriest anomaly:")
print(df.loc[df["precip_anomaly_mm"].idxmin(),
             ["year", "precip_anomaly_mm"]])

print("\nSaved to:", output_file)

''' OUTPUT:
Historical baseline (2005-2025):
Average temperature: 21.03 °C
Average precipitation: 521.27 mm

First five seasonal anomalies:
 year  avg_temp_c  total_precip_mm  days_observed  temp_anomaly_c  precip_anomaly_mm  precip_anomaly_pct
 2005       21.93           454.57            153            0.90             -66.70              -12.80
 2006       21.29           440.14            153            0.26             -81.13              -15.56
 2007       21.23           595.74            153            0.20              74.47               14.29
 2008       19.27           703.55            153           -1.76             182.28               34.97
 2009       19.18           471.19            153           -1.85             -50.08               -9.61

Warmest anomaly:
year              2012.00
temp_anomaly_c       1.88
Name: 7, dtype: float64

Driest anomaly:
year                 2012.00
precip_anomaly_mm    -254.42
Name: 7, dtype: float64

Saved to: /Users/preethisridhar/Desktop/ROOTED/data/processed/ames_climate_anomalies_2005_2025.csv'''