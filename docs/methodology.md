# ROOTED — Recommendation Engine Methodology

## 1. Overview

ROOTED — The Farm That Remembers — is a decision-support application designed to help farmers explore alternative crop rotations using historical environmental data, agricultural constraints, and farmer priorities.

The initial demonstration area is Ames, Story County, Iowa.

The recommendation engine:

1. Loads and validates a crop database.
2. Generates candidate three-entry cash-crop rotations.
3. Validates the structure of each candidate.
4. Represents optional cover-crop practices that fit the crop calendar.
5. Scores each candidate on transparent rotation-structure indicators.
6. Scores each candidate's exposure to historically dry months using NASA POWER daily rainfall.
7. Combines the scores using farmer-selected priorities.
8. Ranks candidates separately for each historical scenario and explains the results and their limitations.

**Current implementation status:** Steps 1–8 are implemented and covered by automated tests. Water suitability, soil-based scoring, and farm-specific feasibility evaluation are not implemented.

All scores are relative model heuristics on a 0–1 scale. They are not yield, profit, or soil-health predictions, and they are comparable only within the same scenario.

---

## 2. Crop Database

ROOTED stores its initial crop library in:

`data/crops.csv`

The database contains five crops:

| Crop | Crop Family | Classification | Planting season |
|---|---|---|---|
| Corn | Poaceae | Cash crop | Spring |
| Soybeans | Fabaceae | Cash crop | Spring |
| Oats | Poaceae | Cash crop | Spring |
| Winter wheat | Poaceae | Cash crop | Fall |
| Cereal rye | Poaceae | Cover crop | Fall |

Each crop record contains:

- `crop_id`
- `crop_name`
- `crop_family`
- `crop_type`
- `planting_season`
- `harvest_season`

### 2.1 Crop Data Validation

The `load_crops()` function in `src/recommendations/crop_data.py` loads the crop database and checks for invalid records.

Validation includes:

- Required CSV columns.
- Missing crop values.
- Duplicate crop identifiers.
- Valid crop classifications.
- Valid seasonal categories.
- Unexpected CSV fields.

The crop database contains general descriptive information. It does not establish whether a crop is suitable for a particular farm.

### 2.2 Crop Drought-Sensitive Months

Each cash crop is assigned one drought-sensitive calendar month in:

`data/crop_critical_windows.csv`

| Crop | Month | Growth stage | Basis |
|---|---|---|---|
| Corn | July | Late vegetative through blister (incl. silking and pollination) | Stage cited (Iowa State Extension); July is a typical-calendar assumption |
| Soybean | August | Early pod set through mid seed fill | Stage cited (Iowa State Extension); August is a typical-calendar assumption |
| Oats | June | Heading and grain fill | Assumption; citation needed |
| Winter wheat | June | Heading and grain fill | Assumption; Iowa-specific citation needed |

These months are timing assumptions for a typical Iowa season, not field observations. Sources are listed in `docs/data_sources.md`. The loader `load_crop_critical_windows()` rejects missing, duplicate, or out-of-range values and never fills them in.

---

## 3. Three-Year Rotation Generation

### 3.1 Candidate Generation

ROOTED generates three-entry cash-crop sequences using:

`generate_rotations(crops)`

in `src/recommendations/rotation_generator.py`.

It identifies all crops classified as cash crops and generates every ordered sequence of three cash-crop identifiers.

- Number of cash crops: 4
- Number of positions: 3
- Repeated crops: allowed

The total number of candidate sequences is **4³ = 64**.

### 3.2 Why Repeated Crops Are Allowed

The generator does not exclude repeated crops. For example, `("corn", "corn", "corn")` is a structurally valid candidate.

This does not mean continuous corn is recommended. ROOTED separates generating possible sequences from evaluating them. Repeated crops are scored lower by the structural indicators (Section 8.1) and are left off recommendation cards (Section 8.5), but they remain in the full ranking for transparency.

### 3.3 Interpretation of Three-Year Sequences

Each three-entry sequence is treated as a **repeating cycle**: after year 3, the rotation starts again at year 1. The transition from year 3 back to year 1 is therefore counted when checking for repeated crops and same-family transitions.

Because of this, sequences that are the same cycle started in a different year (for example, corn → soybean → oats and soybean → oats → corn) are treated as the same rotation cycle. The 64 sequences correspond to **24 distinct cycles** (`unique_cycles()` and `canonical_cycle()` in `rotation_generator.py`).

A three-entry sequence is not automatically a verified planting schedule. Some crops, including winter wheat, grow across calendar years, and exact planting dates and field occupancy are not modeled.

---

## 4. Crop and Cover-Crop Validation

ROOTED distinguishes structural validation from agricultural feasibility evaluation.

### 4.1 Cash-Crop Rotation Validation

`validate_rotation(rotation, crops)` in `src/recommendations/crop_rules.py` checks that a rotation:

- Contains exactly three cash-crop entries.
- Uses crop identifiers registered in the crop database.
- Excludes cover crops from cash-crop positions.

A sequence that passes these checks is **structurally valid**, not necessarily agriculturally feasible.

### 4.2 Cover-Crop Classification

`validate_cover_crop(cover_crop_id, crops)` verifies that a crop identifier is registered as a cover crop. It does not determine whether that crop can be established or managed on a particular farm.

### 4.3 Agricultural Feasibility Requirements

Before ROOTED could present a rotation as agriculturally feasible, the system would need to consider:

- Local planting and harvest windows.
- Crop suitability for local soil and climate conditions.
- Field drainage and irrigation availability.
- Required equipment.
- Farmer preferences and restrictions.
- Market access.
- Compatibility between consecutive crops.

These checks require farm-specific information that is not currently available. ROOTED therefore does not classify any candidate as a confirmed feasible rotation.

---

## 5. Optional Cover-Crop Practices

### 5.1 Cover-Crop Representation

ROOTED represents cover crops as optional management practices, not as cash-crop rotation entries. The current cover crop is cereal rye.

`create_cover_crop_practice(cover_crop_id, after_year, crops)` in `rotation_generator.py` creates a proposed practice:

| Field | Description |
|---|---|
| `cover_crop_id` | Identifier of the proposed cover crop |
| `after_year` | Position of the preceding cash-crop entry |
| `before_year` | Position of the following cash-crop entry |
| `feasibility_status` | Always `not_evaluated` |
| `caution` | Optional management caution (see 5.2) |

### 5.2 Calendar Check

`build_cover_crop_options(rotation, crops)` in `scoring.py` builds cover-crop options for each recommended rotation:

- A cereal-rye slot is **skipped** when the next cash crop is planted in the fall (winter wheat), because the cover crop would need the same fall planting window.
- A slot **before corn** carries a caution: Iowa State Extension recommends terminating cereal rye at least 10 days before planting corn to reduce the risk of seedling disease and yield loss.

A rotation can therefore have zero, one, or two cover-crop options.

### 5.3 Feasibility Status

Every cover-crop option keeps `feasibility_status = "not_evaluated"`. The calendar check removes slots that clearly conflict; it does not establish that the remaining slots will work on a particular farm. Establishment timing, termination, equipment, and field conditions are not evaluated.

---

## 6. NASA Climate Data

### 6.1 Environmental Data Source

ROOTED uses NASA POWER Daily API data for the Ames, Iowa demonstration point (42.03, −93.62), 2005–2025, collected and processed by the climate-data team.

NASA POWER provides gridded estimates (approximately 50 km resolution), not observations from an individual farm.

### 6.2 Historical Scenarios

The climate-data team supplies three representative growing seasons in `data/processed/ames_climate_scenarios.csv`, chosen by May–September total precipitation:

| Scenario | Year | Selection rule |
|---|---|---|
| Dry | 2022 | Closest to the 25th percentile |
| Typical | 2009 | Closest to the median |
| Wet | 2025 | Closest to the 75th percentile |

`load_climate_scenarios()` and `validate_climate_scenarios()` in `climate_inputs.py` check that exactly these three scenarios are present, that all required fields are filled, that the years are distinct, and that precipitation increases from dry to typical to wet.

The recommendation engine adds one stress-test scenario computed from the same NASA POWER daily file:

| Scenario | Year | Selection rule |
|---|---|---|
| July–August dry (`jul_aug_dry`) | 2013 | Lowest combined July + August precipitation on record (50.9 mm) |

The stress year is not probability-weighted. It is included because corn and soybean are most water-sensitive in July and August, and a May–September total can hide a dry mid-summer.

Scenarios are historical replays, not forecasts.

### 6.3 Monthly Rainfall Percentiles

`src/recommendations/climate_timing.py` reads the climate team's raw daily file (`data/raw/nasa_power_ames_iowa_2005_2025.csv`) without modifying it:

1. Daily precipitation (PRECTOTCORR, mm/day) is totalled for each May–September month.
2. Each month is ranked against the same month in all 21 years (rank 1 = driest; tied values share the average rank). The percentile is rank ÷ 21, so the driest month on record is 1/21 ≈ 0.05 and the wettest is 1.0.
3. A month is classed as **dry** when its percentile is ≤ 0.25 — the driest quarter of the record, matching the 25th-percentile rule used for the dry scenario.

Missing values (−999 or blank) stop the calculation; nothing is filled in.

Results for the scenario years:

| Scenario | Year | Dry months |
|---|---|---|
| Dry | 2022 | None (May and September were below median but not in the driest quarter) |
| Typical | 2009 | None |
| Wet | 2025 | May, September |
| July–August dry | 2013 | July, August |

### 6.4 Evapotranspiration-Related Energy Flux

The climate-data team's files include EVPTRNS (evapotranspiration energy flux, MJ/m²/day). This is a modeled estimate reported as an energy flux, not a water depth, and not a reference (potential) evapotranspiration.

ET is **not used in scoring**. ROOTED does not subtract it from precipitation or use it as a measure of crop water demand.

### 6.5 Climate Data Limitations

- Monthly totals do not show rainfall timing within a month, intensity, or heat stress.
- Each scenario is a single historical year and carries that year's particular conditions (for example, 2009 was unusually cool).
- Gridded data cannot establish field-level crop suitability, future yield, or actual soil-water availability.

---

## 7. Recommendation Engine Interface

The main function is:

```python
def recommend_rotations(farm, scenarios, priorities, monthly_totals=None):
    ...
```

in `src/recommendations/scoring.py`.

### 7.1 Inputs

**`farm`** — A dictionary that may contain `current_rotation` (a three-crop tuple) and a `soil` dictionary.

**`scenarios`** — The climate team's dry / typical / wet scenarios, as loaded by `load_climate_scenarios()`.

**`priorities`** — Non-negative values for all three of `soil_protection`, `water_suitability`, and `climate_resilience`. Every key is required (use 0 for priorities the farmer does not want to weight); unknown or missing names are rejected.

**`monthly_totals`** — Optional. When omitted, monthly precipitation totals are computed from the NASA POWER daily file.

### 7.2 Outputs

| Key | Contents |
|---|---|
| `baseline` | The farmer's current rotation scored under every scenario, or `None` if no current rotation is supplied |
| `recommendations` | Three recommendation cards per scenario: `{"dry": [...], "typical": [...], "wet": [...], "jul_aug_dry": [...]}` |
| `scenario_results` | All 64 sequences ranked for each scenario |
| `scenario_context` | For each scenario: year, precipitation, anomalies (where available), dry months, monthly percentiles, and data source |
| `soil_factors` | Supplied soil values, missing fields, `soil_data_status` (`none` / `partial` / `complete`), and `used_in_score = False` |
| `limitations` | Plain-language limitations of the results |

Each recommendation card includes the rotation, scenario, representative year, score, rank, `tied_with`, component values, effective weights, unscored components, `score_basis`, `dropped_priority_share`, explanation text (`why`), and cover-crop options.

---

## 8. Rotation Evaluation

### 8.1 Structural Soil-Protection Proxy

Three components describe rotation structure. All count the three transitions of the repeating cycle (year 1→2, 2→3, and 3→1).

| Component | Formula | Meaning |
|---|---|---|
| Crop diversity | (unique crops − 1) / 2 | 0 = one crop, 1 = three different crops |
| Repeat avoidance | 1 − (same crop in consecutive years) / 3 | 1 = never the same crop two years running |
| Family alternation | 1 − (same family in consecutive years) / 3 | Grass (Poaceae) vs legume (Fabaceae) |

The proxy is the equal-weight mean of the three components. Equal weighting is a stated assumption; no evidence was found supporting a different weighting.

Corn, oats, and winter wheat are different species but the same family (Poaceae), so an all-grass rotation scores lower on family alternation than a rotation that includes soybean.

The proxy describes rotation composition. It is not a measurement or prediction of soil health.

### 8.2 Climate Component (Critical-Window Dry Exposure)

For each scenario, a crop-year is **exposed** if the crop's drought-sensitive month (Section 2.2) was a dry month (Section 6.3) in that scenario's representative year.

**Climate score = 1 − (exposed rotation years) / 3**

- 1.0 means no crop in the rotation had its sensitive month in the driest quarter of 2005–2025 in that year.
- Wet months are not penalized. Monthly totals cannot show ponding or waterlogging, and the engine does not evaluate those conditions using the mapped soil drainage estimate.

With the current data, no crop is exposed in 2022, 2009, or 2025, so the climate score is the same for every rotation in those scenarios and their rankings are decided by rotation structure. In 2013, corn (July) and soybean (August) are exposed and the small grains are not, so the ranking changes.

### 8.3 Farmer Priorities

Priority values are normalized to sum to 1. Negative, non-numeric, all-zero, unknown, and missing priorities are rejected.

Water suitability is not scored. Its weight is removed and the remaining weights are renormalized over the components that are scored. This is equivalent to assuming the unscored component would match the scored ones, so the removed share is reported on every result as `dropped_priority_share` and in the explanation text. If only water suitability has a non-zero priority, the engine returns an error explaining that another priority must be set above zero.

### 8.4 Baseline Comparison

If the farmer supplies a current rotation, it is scored under every scenario with the same method. If not, no baseline is created; ROOTED does not invent one.

### 8.5 Ranking and Recommendation Cards

- All 64 sequences are scored and ranked for each scenario, highest score first.
- Ranks are dense: rotations with the same score (to 6 decimal places) share a rank.
- `tied_with` counts the other distinct rotation cycles at the same score. Sequences that are the same cycle always share a score and are not counted as separate ties.
- Recommendation cards skip rotations that repeat a crop in consecutive years (including year 3 to year 1) and show one card per cycle.
- Three cards are returned per scenario. No single best-overall rotation is claimed, because scores are not comparable across scenarios.

### 8.6 Explanations

Explanation text describes model mechanics only: number of crops, repeated crops in the cycle, crop-family transitions, which crops were exposed in which year, ties, and unscored priority weight. An automated test checks that explanations never contain outcome claims such as "soil health", "improve", "optimal", or "yield".

---

## 9. Testing and Validation

ROOTED uses `pytest` (configured in `pytest.ini`). The automated tests cover:

- Crop database loading and validation.
- Rotation and cover-crop validation.
- Generation of 64 sequences and 24 distinct cycles.
- Structural indicators, including year-3-to-year-1 transitions and crop families.
- Loading and validating the climate team's scenario file.
- Monthly precipitation totals and percentiles from the NASA POWER daily file, including known 2013 values and the 2013 stress year.
- Critical-window loading and climate exposure for each real scenario year.
- Priority normalization, name validation, unscored-weight reporting, and water-only error handling.
- Ranking, dense ranks, tie counts, and card screening.
- Calendar-aware cover-crop options and the rye-before-corn caution.
- Explanation wording, including the absence of outcome claims.
- Soil-data status, including the retrieved USDA mapped Ames soil profile and its field-level limitations.

Climate and scenario tests use the real project files. Error-handling tests break a temporary copy of a real file; the originals are never changed. A small number of arithmetic and validation tests use hand-typed input values to check calculations; these values are not presented as Ames data.

These tests verify software behavior and consistency with the documented method. They do not validate agricultural feasibility or the agronomic accuracy of the scores.

---

## 10. Current Limitations

- Scores are relative heuristics, not yield, profit, or soil-health predictions.
- Scores are comparable only within a scenario.
- Climate scoring uses monthly rainfall only: no heat stress, soil moisture, or rainfall timing within a month.
- Crop sensitive months are typical Iowa timing assumptions; oats and winter wheat timing still need Iowa-specific citations.
- Each scenario is a single historical year; 2013 is a stress test.
- NASA POWER data are gridded estimates (~50 km), not field measurements.
- Wet-weather effects (ponding, waterlogging) are not evaluated.
- Water suitability is not scored.
- USDA mapped soil data are available for the demo location as representative estimates. They are displayed for context but are not used in scoring.
- Cover-crop options are checked only against the crop calendar; farm-specific feasibility is not evaluated.
- Economics, markets, equipment, pests, disease, and nitrogen effects are not modeled.

**ROOTED is intended to support farmer decision-making, not replace local agronomic expertise or field-specific assessment.**

---

## 11. Supporting Documentation

Agricultural references, NASA data sources, crop classifications, and outstanding evidence gaps are documented in:

`docs/data_sources.md`

Future updates should distinguish completed functionality from proposed features and document the evidence supporting any new feasibility rules or numerical indicators.
