# preethi - cleaning and analyzing climate data
# 21 years of daily climate observations and make a summary per peak growing season (i think may 1-sept 30 is good)
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
input_file = (PROJECT_ROOT / "data" / "raw" / "nasa_power_ames_iowa_2005_2025.csv")
df = pd.read_csv(input_file)

df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d") # making it yyyymmdd 

# checking if there are any numeric missing data values
climate_columns = ["T2M", "PRECTOTCORR"]

for column in climate_columns:
    df[column] = df[column].replace(-999, float("nan"))

print("Missing climate values:")
print(df[climate_columns].isna().sum())

# stop if any climate values are missing
if df[climate_columns].isna().any().any():
    raise ValueError(
        "Missing NASA climate values found. "
        "Review the dataset before analysis."
    )


df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

# may thru sept
growing_season = df[df["month"].between(5, 9)].copy()

# calculate one summary row for each year
seasonal_summary = (
    growing_season.groupby("year")
    .agg(
        avg_temp_c=("T2M", "mean"),
        total_precip_mm=("PRECTOTCORR", "sum"),
        days_observed=("date", "count"),
    )
    .reset_index()
)

# round climate measurements for readability
seasonal_summary["avg_temp_c"] = (seasonal_summary["avg_temp_c"].round(2))
seasonal_summary["total_precip_mm"] = (seasonal_summary["total_precip_mm"].round(2))

output_file = (PROJECT_ROOT / "data" / "processed" / "ames_growing_seasons_2005_2025.csv")
output_file.parent.mkdir(parents=True, exist_ok=True)
seasonal_summary.to_csv(output_file, index=False)
print("\nGrowing-season summaries:")
print(seasonal_summary)
print("\nNumber of seasons:", len(seasonal_summary))
print("\nSaved to:", output_file)