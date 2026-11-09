# ROOTED — Data Sources and Agricultural References

---

## 1. Crop Selection and Classification

ROOTED uses an initial library of five crops: four cash crops and one optional cover crop.

The crop library supports the generation of candidate three-year crop rotations for the Ames, Iowa demonstration area.

These crops are included for exploration and comparison. Their inclusion does not establish suitability for an individual farm.

### 1.1 Corn and Soybeans

Corn and soybeans are included because they are major agricultural crops in Iowa, according to the USDA National Agricultural Statistics Service (NASS).

Both are classified as cash crops in ROOTED's initial database.

- **Corn (*Zea mays*):** Poaceae (grass family).
- **Soybeans (*Glycine max*):** Fabaceae (legume family).

Corn and soybeans are generally planted in spring and harvested in fall in Iowa.

Their inclusion allows ROOTED to represent common crop sequences and explore alternatives.

**Sources:**

- USDA NASS — Iowa Agricultural Overview:  
  https://www.nass.usda.gov/Quick_Stats/Ag_Overview/stateOverview.php?state=Iowa
- USDA PLANTS Database:  
  https://plants.usda.gov/
- Iowa State University — Integrated Crop Management:  
  https://crops.extension.iastate.edu/

### 1.2 Oats and Winter Wheat

Oats and winter wheat are included as additional candidate cash crops to explore rotation diversity and different seasonal growing patterns.

- **Oats (*Avena sativa*):** Poaceae (grass family).
- **Winter wheat (*Triticum aestivum*):** Poaceae (grass family).

Oats are generally spring-planted and harvested during summer.

Winter wheat is generally planted in fall and harvested the following summer, meaning its growing period spans two calendar years.

These crops introduce growing-season patterns that differ from corn and soybeans.

However, ROOTED does not assume that either crop is suitable or economically viable for every farm in central Iowa.

Before recommending them, the system would need to evaluate local growing conditions, planting and harvest timing, equipment availability, and market access.

**Sources:**

- Iowa State University — Integrated Crop Management:  
  https://crops.extension.iastate.edu/
- USDA PLANTS Database:  
  https://plants.usda.gov/
- USDA NASS — Iowa Agricultural Overview:  
  https://www.nass.usda.gov/Quick_Stats/Ag_Overview/stateOverview.php?state=Iowa

### 1.3 Cereal Rye (Optional Cover Crop)

Cereal rye (*Secale cereale*) belongs to the Poaceae (grass) family.

ROOTED includes cereal rye as an optional cover crop rather than a fifth cash crop.

Cereal rye can provide winter soil cover and may help:

- Reduce soil erosion.
- Take up residual soil nutrients, including nitrogen.
- Contribute plant biomass.
- Reduce the amount of time soil remains uncovered.

However, its successful use depends on establishment timing, termination timing, the following cash crop, and available management practices.

ROOTED does not assume cereal rye is appropriate between every pair of cash crops (see Section 4).

**Sources:**

- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf
- Farm Progress — "Cereal rye cover crop could negatively affect corn" (reports Iowa State University guidance on terminating rye before corn):  
  https://www.farmprogress.com/crops/cereal-rye-cover-crop-could-negatively-affect-corn

### 1.4 Initial Crop Reference Table

The following table summarizes ROOTED's initial crop library.

| Crop | Scientific Name | Family | Type | Planting Season | Harvest / Termination |
|---|---|---|---|---|---|
| Corn | *Zea mays* | Poaceae | Cash | Spring | Fall |
| Soybeans | *Glycine max* | Fabaceae | Cash | Spring | Fall |
| Oats | *Avena sativa* | Poaceae | Cash | Spring | Summer |
| Winter wheat | *Triticum aestivum* | Poaceae | Cash | Fall | Following summer |
| Cereal rye | *Secale cereale* | Poaceae | Cover | Fall | Following spring (termination) |

**Important:** These are general seasonal classifications, not exact planting or harvest windows for a specific farm.

The table corresponds to the crop records stored in `data/crops.csv`.

### 1.5 Supporting Agricultural References

| Organization | Resource | Primary Use |
|---|---|---|
| USDA NASS | Iowa Agricultural Overview | Iowa crop production and crop-selection context |
| USDA PLANTS | PLANTS Database | Botanical names and crop families |
| Iowa State University Extension | Integrated Crop Management | Crop production and growing-season considerations |
| Iowa State University Extension | "Influence of drought on corn and soybean" | Drought-sensitive growth stages of corn and soybean |
| USDA NRCS | Cereal Rye Cover Crop Fact Sheet | Cover-crop benefits, risks, and management considerations |
| Farm Progress (reporting Iowa State guidance) | "Cereal rye cover crop could negatively affect corn" | Terminating cereal rye before corn |
| NASA POWER | Daily API | Historical precipitation for Ames, 2005–2025 |

Some of these references point to general resource pages rather than individual crop-specific publications. Before final submission, each crop-specific claim should be checked against an identifiable publication or database record, with its publication date where available.

---

## 2. Crop Growing Seasons

ROOTED represents planting and harvest periods using broad seasonal categories.

These descriptions help organize candidate crop sequences but are not sufficient to establish agricultural feasibility.

| Crop | General Planting Season | General Harvest / Termination | Notes |
|---|---|---|---|
| Corn | Spring | Fall | Timing varies with local conditions, crop variety, and management. |
| Soybeans | Spring | Fall | Timing varies with local conditions, crop variety, and management. |
| Oats | Spring | Summer | Earlier harvest may create additional management opportunities. |
| Winter wheat | Fall | Following summer | Growing period spans two calendar years. |
| Cereal rye | Fall | Following spring | Optional cover crop requiring termination management. |

### 2.1 Seasonal Limitations

Actual planting and harvest windows depend on:

- Local weather and soil conditions.
- Crop varieties and maturity characteristics.
- Field accessibility.
- Available equipment.
- Farm management decisions.
- Timing of preceding and following crops.

Winter wheat and cereal rye require particular attention because their growing periods extend across calendar years. For example, winter wheat planted in fall may occupy a field until the following summer.

Consequently, a three-entry crop sequence is not a verified three-calendar-year planting schedule.

The engine uses the planting-season category in one place: no cereal-rye cover-crop slot is offered directly before winter wheat, because both would need the same fall planting window (Section 4.3). Exact dates are not modeled.

**Sources:**

- Iowa State University — Integrated Crop Management:  
  https://crops.extension.iastate.edu/
- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf

### 2.2 Drought-Sensitive Months

For climate scoring, each cash crop is assigned one drought-sensitive calendar month, stored in `data/crop_critical_windows.csv`.

| Crop | Month | Growth stage | Evidence status |
|---|---|---|---|
| Corn | July | Late vegetative through blister, including silking and pollination | Growth stage cited (Iowa State Extension, "Influence of drought on corn and soybean"). July is a typical-calendar assumption. |
| Soybean | August | Early pod set through mid seed fill | Growth stage cited (same source). August is a typical-calendar assumption. |
| Oats | June | Heading and grain fill | **Assumption — citation needed.** Candidate source: USDA NASS Iowa Crop Progress reports (oat heading dates). |
| Winter wheat | June | Heading and grain fill | **Assumption — Iowa-specific citation needed.** |

These are typical-season timing assumptions, not field observations. Actual timing varies with planting date, variety, and weather.

**Source:**

- Iowa State University Extension — "Influence of drought on corn and soybean" (Integrated Crop Management, July 2017):  
  https://crops.extension.iastate.edu/cropnews/2017/07/influence-drought-corn-and-soybean

---

## 3. Crop Rotation Considerations

### 3.1 Rotation Feasibility Framework

ROOTED distinguishes between:

1. **Candidate generation:** Producing possible cash-crop sequences.
2. **Structural validation:** Checking whether a sequence follows the application's data rules.
3. **Rotation evaluation:** Comparing candidates using documented indicators and farmer priorities.
4. **Agricultural feasibility:** Determining whether a sequence can realistically be implemented on a particular farm.

Steps 1–3 are implemented. Step 4 is not: a generated or highly ranked sequence is not a confirmed feasible rotation.

### 3.2 Structural Rules

ROOTED enforces the following structural rules:

- A three-entry rotation must contain exactly three cash-crop identifiers.
- Every crop must exist in the validated crop database.
- Cover crops cannot occupy cash-crop positions.
- Repeated cash crops are permitted during candidate generation.
- Optional cover-crop practices are represented separately from cash-crop sequences.

The structural validation logic is implemented in `src/recommendations/crop_rules.py`. Candidate generation is implemented in `src/recommendations/rotation_generator.py`.

With four cash crops and three positions, ROOTED generates **4 × 4 × 4 = 64 candidate sequences**.

Each sequence is treated as a repeating three-year cycle, so the transition from year 3 back to year 1 is counted. Sequences that are the same cycle started in a different year are grouped, giving **24 distinct cycles**.

Repeated crops stay in the full ranking but are left off recommendation cards.

### 3.3 Farm-Specific Constraints

The following factors require additional information before agricultural feasibility can be established:

- Local planting and harvest windows.
- Soil characteristics and drainage.
- Crop suitability for local climate conditions.
- Availability of necessary equipment.
- Irrigation availability.
- Farmer crop preferences and restrictions.
- Market access and intended crop use.
- Cover-crop establishment and termination timing.
- Compatibility between consecutive crops.

These factors should be evaluated using actual farm information and appropriately sourced agricultural guidance.

### 3.4 Rotation Indicators Used in Scoring

ROOTED compares rotations using three structural indicators and one climate indicator. Full formulas are in `docs/methodology.md`, Section 8.

| Indicator | What it counts | Evidence status |
|---|---|---|
| Crop diversity | Number of different cash crops | Descriptive count |
| Repeat avoidance | Same crop in consecutive years (including year 3 → year 1) | Descriptive count |
| Family alternation | Same plant family in consecutive years (grass vs legume) | Descriptive count; families from USDA PLANTS |
| Critical-window dry exposure | Crop-years whose drought-sensitive month was in the driest quarter of 2005–2025 in the scenario year | Uses NASA POWER rainfall (Section 5) and the timing assumptions in Section 2.2 |

The structural indicators are combined with equal weights. Equal weighting is a stated modeling assumption, not an evidence-based weighting.

These indicators describe rotation composition and historical rainfall timing. They are not measured improvements in soil health, crop yield, or profitability.

For example, corn, oats, and winter wheat are three different crops, but all belong to the Poaceae family. A rotation containing only those crops has crop-species diversity without crop-family diversity, and it scores lower on family alternation than a rotation that includes soybean.

### 3.5 Current Feasibility Limitations

ROOTED uses Ames, Story County, Iowa, as its demonstration area. The demonstration coordinates (42.03, −93.62) do not identify a surveyed farm field, and individual farm characteristics have not been finalized.

ROOTED can generate, structurally validate, score, and rank candidate crop sequences. It cannot confirm their agricultural feasibility without farm-specific information and exact crop-calendar constraints.

---

## 4. Cover Crop Practices

### 4.1 Initial Cover-Crop Option

ROOTED includes cereal rye as an optional cover-crop practice.

Cereal rye may provide winter soil cover, help reduce erosion, and take up residual soil nutrients. Its suitability depends on establishment timing, termination timing, the following cash crop, and farm management practices.

### 4.2 Optional Practice Representation

ROOTED represents cover crops separately from its three-entry cash-crop sequences.

A proposed practice contains:

| Field | Description |
|---|---|
| `cover_crop_id` | Identifier of the optional cover crop |
| `after_year` | Position of the preceding cash-crop entry |
| `before_year` | Position of the following cash-crop entry |
| `feasibility_status` | Always `not_evaluated` |
| `caution` | Management caution, when one applies |

The `after_year` and `before_year` fields describe positions in the crop sequence, not verified calendar-year planting dates.

`create_cover_crop_practice()` in `src/recommendations/rotation_generator.py` validates the cover-crop identifier and position. It does not determine whether the cover crop can be established or managed.

### 4.3 Calendar Check and Caution

`build_cover_crop_options(rotation, crops)` in `src/recommendations/scoring.py` builds the cover-crop options shown on each recommendation card:

| Rule | Basis |
|---|---|
| No cereal-rye slot directly before winter wheat | Both are fall-planted (`data/crops.csv`), so they would compete for the same planting window |
| A slot directly before corn carries a caution to terminate rye at least 10 days before planting corn | Iowa State University guidance on seedling-disease and yield risk, as reported by Farm Progress (link in Section 1.3) |

A rotation can have zero, one, or two cover-crop options.

### 4.4 Feasibility Status

Every option keeps `feasibility_status = "not_evaluated"`. The calendar check removes clearly conflicting slots; it does not establish that remaining slots will work on a particular farm.

Before ROOTED could recommend cereal rye between two cash crops, the system would need to evaluate:

- Harvest timing of the preceding cash crop.
- Available cover-crop establishment window.
- Cover-crop termination requirements.
- Planting window of the following cash crop.
- Available equipment and management options.
- Relevant soil and environmental conditions.

**Sources:**

- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf
- Farm Progress — "Cereal rye cover crop could negatively affect corn":  
  https://www.farmprogress.com/crops/cereal-rye-cover-crop-could-negatively-affect-corn

---

## 5. NASA Environmental Data

### 5.1 NASA POWER

ROOTED uses historical daily data from the NASA POWER Daily API for the Ames, Story County, Iowa demonstration point (42.03, −93.62), 2005–2025. The data were retrieved and processed by the climate-data team.

**Files used by the recommendation engine:**

| File | Prepared by | Used for |
|---|---|---|
| `data/raw/nasa_power_ames_iowa_2005_2025.csv` | Climate-data team | Engine reads daily precipitation (PRECTOTCORR) to compute monthly totals, monthly percentiles, and the July–August stress year. The file is read, never modified. |
| `data/processed/ames_climate_scenarios.csv` | Climate-data team | Dry, typical, and wet representative seasons |

**Scenarios:**

| Scenario | Year | Selection rule | Prepared by |
|---|---|---|---|
| Dry | 2022 | May–Sep precipitation closest to the 25th percentile | Climate-data team |
| Typical | 2009 | Closest to the median | Climate-data team |
| Wet | 2025 | Closest to the 75th percentile | Climate-data team |
| July–August dry | 2013 | Lowest combined July + August precipitation on record (50.9 mm) | Recommendation engine, from the raw daily file |

Scenarios are historical replays, not forecasts. 2013 is a stress test, not a probability-weighted scenario.

**Source:**

- NASA POWER — Prediction Of Worldwide Energy Resources:  
  https://power.larc.nasa.gov/

### 5.2 Environmental Variables

| Variable | NASA POWER parameter | Use in ROOTED | Important limitation |
|---|---|---|---|
| Precipitation | PRECTOTCORR (mm/day) | Monthly May–September totals; each month ranked against the same month in all 21 years; a month in the driest quarter (percentile ≤ 0.25) counts as dry | Rainfall does not equal plant-available soil water; monthly totals hide timing within the month |
| Temperature | T2M (°C) | Displayed as scenario context (season average and anomaly) | Not used in scoring; heat stress is not evaluated |
| Evapotranspiration energy flux | EVPTRNS (MJ/m²/day) | Displayed as scenario context only | Modeled estimate reported as energy, not water depth; not reference ET; not used in scoring |

Missing values (−999 or blank) stop the calculation in the engine; they are never filled in.

### 5.3 Evapotranspiration-Related Data and Unit Handling

EVPTRNS is reported in **MJ/m²/day**, an energy flux rather than a water depth. It is a modeled estimate of actual evapotranspiration, not a reference (potential) evapotranspiration, and therefore does not measure crop water demand.

ROOTED does not subtract it from precipitation and does not use it in scoring. A precipitation-minus-ET indicator would require a verified reference-ET source and a documented unit conversion.

### 5.4 Spatial and Temporal Limitations

NASA POWER provides gridded estimates (approximately 50 km resolution) rather than direct measurements at an individual farm.

These estimates support comparisons of historical regional conditions but should not be presented as field-level observations.

Each scenario is a single historical year and carries that year's specific conditions; for example, the typical year (2009) had an unusually cool summer.

Historical climate summaries do not predict future crop yields or establish the suitability of individual rotations.

---

## 6. Limitations and Data Gaps

### 6.1 Farm-Specific Information

The characteristics of an individual farm have not been finalized. The engine accepts a current rotation but still lacks:

- Soil characteristics and drainage.
- Irrigation availability.
- Equipment and management capabilities.
- Crop preferences and restrictions.
- Market access.

### 6.2 Soil Data

`data/processed/ames_soil_profile.json` contains a retrieved USDA NRCS Soil Data Access profile for the Ames demonstration location. It includes representative mapped values for texture, pH, organic matter, drainage class, and available water capacity. These are estimates for the dominant Clarion soil component and surface horizon, not verified measurements from an individual farm field.

The engine reports soil status as `none`, `partial`, or `complete`, never fills in missing values, and does not use soil in scoring.

### 6.3 Crop Timing

The crop database uses broad seasonal categories rather than exact planting and harvest dates, and drought-sensitive months are typical-season assumptions (Section 2.2). Generated sequences are not verified planting schedules.

### 6.4 Agricultural Feasibility

The engine validates rotation structure, scores rotations, and checks cover-crop slots against the planting-season categories. It does not establish field-level agricultural feasibility.

### 6.5 Environmental Data

- NASA POWER data are gridded estimates, not field measurements.
- Climate scoring uses monthly rainfall only; heat stress, soil moisture, and rainfall timing within a month are not evaluated.
- Wet-weather effects (ponding, waterlogging) are not evaluated.
- Water suitability is not scored.

### 6.6 Soil Health and Agricultural Outcomes

Crop diversity and cover-crop inclusion do not establish improvements in soil health.

ROOTED does not predict:

- Crop yield.
- Farm profitability.
- Measured soil-health improvement.
- Field-level water stress.
- Future climate conditions.

### 6.7 Research and Citation Gaps

Outstanding items before final submission:

- Cite Iowa-specific heading and grain-fill timing for oats (candidate: USDA NASS Iowa Crop Progress reports).
- Cite Iowa-specific heading and grain-fill timing for winter wheat.
- Replace general resource-page links with specific publications where possible, and record publication dates.
- Retrieve and verify soil properties for an agricultural point near the demonstration area, if soil is to be shown.

---

## 7. Implementation References

| File | Purpose |
|---|---|
| `data/crops.csv` | Crop library |
| `data/crop_critical_windows.csv` | Drought-sensitive month for each cash crop, with stage and source |
| `data/raw/nasa_power_ames_iowa_2005_2025.csv` | NASA POWER daily data (climate-data team) |
| `data/processed/ames_climate_scenarios.csv` | Dry, typical, wet scenarios (climate-data team) |
| `data/processed/ames_soil_profile.json` | Retrieved USDA mapped soil profile for the Ames demonstration location; representative estimates, not field measurements |
| `src/recommendations/crop_data.py` | Loads and validates crops and critical windows |
| `src/recommendations/crop_rules.py` | Structural crop and cover-crop validation |
| `src/recommendations/rotation_generator.py` | Candidate generation, cycle grouping, cover-crop practice records |
| `src/recommendations/climate_inputs.py` | Loads and validates the climate team's scenario file |
| `src/recommendations/climate_timing.py` | Monthly rainfall totals, percentiles, stress year, and dry-month profiles |
| `src/recommendations/scoring.py` | Scoring, ranking, recommendation cards, explanations, and `recommend_rotations()` |
| `tests/test_recommendations.py` | Tests for crop, rotation, scoring, ranking, card, and explanation logic |
| `tests/test_climate_inputs.py` | Tests for the scenario file, using the real file |
| `tests/test_climate_timing.py` | Tests for monthly rainfall and critical windows, using the real NASA file |
| `pytest.ini` | Test configuration |
| `docs/methodology.md` | Full description of the method |

The recommendation-engine interface is:

`recommend_rotations(farm, scenarios, priorities, monthly_totals=None)`

It returns the farmer's baseline, three recommendation cards per scenario, full rankings for all 64 sequences, scenario context, soil status, and a list of limitations.

---

## 8. Primary References

**[1] USDA National Agricultural Statistics Service (NASS)**  
Iowa Agricultural Overview  
https://www.nass.usda.gov/Quick_Stats/Ag_Overview/stateOverview.php?state=Iowa

**[2] USDA Natural Resources Conservation Service (NRCS)**  
Cereal Rye Cover Crop Fact Sheet  
https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf

**[3] USDA PLANTS Database**  
Plant classification and botanical information  
https://plants.usda.gov/

**[4] Iowa State University Extension and Outreach**  
Integrated Crop Management  
https://crops.extension.iastate.edu/

**[5] NASA POWER**  
Prediction Of Worldwide Energy Resources  
https://power.larc.nasa.gov/

**[6] Iowa State University Extension and Outreach**  
"Influence of drought on corn and soybean," Integrated Crop Management, July 2017  
https://crops.extension.iastate.edu/cropnews/2017/07/influence-drought-corn-and-soybean

**[7] Farm Progress**  
"Cereal rye cover crop could negatively affect corn" (reports Iowa State University guidance)  
https://www.farmprogress.com/crops/cereal-rye-cover-crop-could-negatively-affect-corn

---
