## Demo Location

- Ames, Iowa
- Latitude: 42.03
- Longitude: -93.62
- Historical period years: 2005–2025
- Primary growing season: May–September

## Data Sources Used

- NASA POWER Daily API: https://power.larc.nasa.gov/
- NASA parameters definitions:
  - T2M: The mean daily air temperature (in °C)
  - PRECTOTCORR: The corrected daily precipitation (mm/day)
  - EVPTRNS: Evapotranspiration energy flux (MJ/m²/day)
- USDA NRCS Web Soil Survey:
  https://websoilsurvey.nrcs.usda.gov/app/
  Note: Soil measurements have not yet been retrieved.

## Files for Integration

### Climate

- data/raw/nasa_power_ames_iowa_2005_2025.csv
  Daily temperature and precipitation observations.

- data/processed/ames_growing_seasons_2005_2025.csv
  Annual May–September mean temperature and total precipitation.

- data/processed/ames_climate_anomalies_2005_2025.csv
  Temperature and precipitation differences relative to the
  2005–2025 growing-season baseline.

### Evapotranspiration

- data/processed/ames_daily_et_2005_2025.csv
  Daily EVPTRNS energy-flux observations.

- data/processed/ames_seasonal_et_2005_2025.csv
  May–September average daily ET energy flux and seasonal
  energy-flux total.

### Scenarios

- data/processed/ames_climate_scenarios.csv
  Three representative historical growing seasons:
  dry, typical, and wet.

### Soil

- data/processed/ames_soil_profile.json
  Structured Iowa demo farm profile.
  Soil measurements are currently null and unverified.

## Scenario Selection

Scenarios are selected using historical growing-season
precipitation percentiles:

- Dry: Historical season nearest the 25th percentile
- Typical: Historical season nearest the 50th percentile
- Wet: Historical season nearest the 75th percentile

Selected years:

- Dry: 2022
- Typical: 2009
- Wet: 2025

These are historical examples, not future climate forecasts.

## Integration Notes

- Join annual climate, anomaly, and ET data by year.
- Scenario IDs are: dry, typical, wet.
- Seasonal precipitation is measured in mm.
- Temperature and temperature anomalies are measured in °C.
- Precipitation anomalies are also available as percentages.
- ET values are energy-flux metrics, not water-depth estimates.
- Do not directly subtract ET energy from precipitation in mm.
- Do not treat missing soil values as zero.
- Soil-dependent scoring should wait for verified or
  farmer-provided soil measurements.

## Limitations

1. Ames coordinates represent a demonstration location,
   not a surveyed farm boundary.
2. May–September summaries do not describe the full
   fall/winter/spring crop rotation cycle.
3. The typical scenario is selected by precipitation,
   not by all climate variables simultaneously.
4. Historical scenarios are not forecasts.
5. Soil attributes have not yet been verified.
6. Recommendations should clearly identify missing inputs.

## Pending Integration Decision

Sim needs to confirm whether soil properties are:

- Retrieved from a verified soil data source, or
- Provided by the farmer through the application.

Until then, soil-dependent recommendation logic should
handle missing values safely.
