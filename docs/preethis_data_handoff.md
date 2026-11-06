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
- USDA NRCS Soil Data Access:
  https://sdmdataaccess.sc.egov.usda.gov/
  - Soil map unit: Clarion loam, Bemis moraine, 2 to 6 percent slopes
  - Map unit key (MUKEY): 2765537
  - Dominant component: Clarion (85%)
  - Component key (COKEY): 28635382
  - Soil values retrieved from USDA survey records.
  - These are representative mapped soil estimates,
    not measurements collected from a specific farm.

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
  USDA-derived soil profile for the Ames demonstration location.

  Dominant soil component: Clarion (85% of map unit).

  Surface horizon (Ap, 0-23 cm):
  - Texture: Loam
  - Soil pH: 6.2
  - Organic matter: 3.5%
  - Available water capacity: 0.21 cm/cm

  Component drainage class: Well drained.

  Available water capacity describes soil water storage
  capacity, not current soil moisture or soil wetness.

  Values represent mapped soil survey estimates rather
  than direct measurements from an individual farm.

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
- Soil properties are now populated using USDA survey estimates.
- Preserve the existing soil JSON field names for integration.
- Available water capacity is stored as 0.21 cm/cm for
  the 0-23 cm surface horizon, not the full soil profile.
- Available water capacity must not be labeled as current
  soil moisture or soil wetness.
- Do not treat missing soil values as zero.
- Soil-dependent scoring should use only properties supported
  by documented scoring rules; otherwise report limitations.

## Limitations

1. Ames coordinates represent a demonstration location,
   not a surveyed farm boundary.
2. May–September summaries do not describe the full
   fall/winter/spring crop rotation cycle.
3. The typical scenario is selected by precipitation,
   not by all climate variables simultaneously.
4. Historical scenarios are not forecasts.
5. Soil properties are USDA mapped survey estimates for the
   dominant Clarion component, not field-measured values.
6. Recommendations should clearly identify missing inputs.

## Soil Integration Status

- USDA soil properties retrieved and added to the soil JSON.
- The original soil field names have been preserved.
- Soil data is available on feature/climate-data.
- Sim should verify that the recommendation engine loads
  the updated soil profile and handles the values correctly.
- Dilpreet should display soil properties with their units
  and source limitations.
- Any missing or farmer-provided soil inputs must still be
  handled safely without substituting zero.
