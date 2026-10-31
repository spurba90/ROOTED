# preethi - intended for creating dry, typical, and wet historical climate scenarios.
# ames, iowa (may-sept, 2005–2025)
import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parents[2]
processed = root / "data" / "processed"
climate_file = processed / "ames_climate_anomalies_2005_2025.csv"
et_file = processed / "ames_seasonal_et_2005_2025.csv"
output_file = processed / "ames_climate_scenarios.csv"
climate = pd.read_csv(climate_file)
et = pd.read_csv(et_file)

# match the climate/ET msmtd by yr
df = climate.merge(et[["year", "avg_daily_et_mj_m2_day", "total_et_energy_mj_m2"]], on="year", how="inner", validate="one_to_one")

if len(df) != 21 or df["year"].nunique() != 21:
    raise ValueError("Expected 21 historical seasons")
if df.isna().any().any():
    raise ValueError("Missing values found in scenario data")

scenario_quantiles = {"dry": 0.25, "typical": 0.50, "wet": 0.75}
scenarios = []
for scenario_name, quantile in scenario_quantiles.items():
    target_precip = df["total_precip_mm"].quantile(quantile)  # target precipitation

    # this is the year closest to that target
    representative = (df.assign(distance_from_target=
                                (df["total_precip_mm"] - target_precip).abs()).sort_values(["distance_from_target", "year"]).iloc[0])

    scenarios.append({
        "scenario_id": scenario_name,
        "representative_year": int(representative["year"]),
        "season_start_month": 5,
        "season_end_month": 9,
        "avg_temp_c": representative["avg_temp_c"],
        "total_precip_mm": representative["total_precip_mm"],
        "temp_anomaly_c": representative["temp_anomaly_c"],
        "precip_anomaly_mm": representative["precip_anomaly_mm"],
        "precip_anomaly_pct": representative["precip_anomaly_pct"],
        "avg_daily_et_mj_m2_day":
            representative["avg_daily_et_mj_m2_day"],
        "total_et_energy_mj_m2":
            representative["total_et_energy_mj_m2"]
    })

scenario_df = pd.DataFrame(scenarios)
if scenario_df["representative_year"].nunique() != 3:
    raise ValueError("Duplicate representative years selected")

if not scenario_df["total_precip_mm"].is_monotonic_increasing:
    raise ValueError("Scenarios are not ordered dry to wet")

# for sim's engine
scenario_df.to_csv(output_file, index=False)
print("ROOTED historical climate scenarios:")
print(scenario_df.to_string(index=False))
print("\nSaved to:", output_file)