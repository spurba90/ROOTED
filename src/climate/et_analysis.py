from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
input_file = (project_root / "data" / "processed" / "ames_daily_et_2005_2025.csv")
output_file = (project_root / "data" / "processed" / "ames_seasonal_et_2005_2025.csv")
df = pd.read_csv(input_file) # cleaned daily ET data

df["date"] = pd.to_datetime(df["date"].astype(str),format="%Y%m%d")
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

growing_season = df[df["month"].between(5, 9)].copy()

# grouping data by yr/calculating seasonal metrics
seasonal_et = (growing_season.groupby("year")
    .agg(
        avg_daily_et_mj_m2_day=("EVPTRNS", "mean"),
        total_et_energy_mj_m2=("EVPTRNS", "sum"),
        days_observed=("EVPTRNS", "count")
    ).reset_index()
)

# complete may-sept seasons??
if not (seasonal_et["days_observed"] == 153).all():
    raise ValueError("One or more growing seasons are incomplete")

# rounding outputs
seasonal_et[["avg_daily_et_mj_m2_day", "total_et_energy_mj_m2"]] = seasonal_et[["avg_daily_et_mj_m2_day", "total_et_energy_mj_m2"]].round(2)

output_file.parent.mkdir(parents=True, exist_ok=True)
seasonal_et.to_csv(output_file, index=False)

print("Seasonal ET summary:")
print(seasonal_et.head())

print("\nNumber of seasons:", len(seasonal_et))
print("First year:", seasonal_et["year"].min())
print("Last year:", seasonal_et["year"].max())

print("\nSeasonal ET energy range:")
print(
    seasonal_et["total_et_energy_mj_m2"].min(),
    "to",
    seasonal_et["total_et_energy_mj_m2"].max(),
    "MJ/m²"
)

print("\nSaved to:", output_file)
