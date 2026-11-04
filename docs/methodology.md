# ROOTED — Recommendation Engine Methodology

## 1. Overview

ROOTED — The Farm That Remembers — is a decision-support application designed to help farmers explore alternative crop rotations using historical environmental data, agricultural constraints, and farmer priorities.

The initial demonstration area is Ames, Story County, Iowa.

The recommendation engine is designed to:

1. Load and validate a crop database.
2. Generate candidate three-entry cash-crop rotations.
3. Validate the structure of each candidate.
4. Represent optional cover-crop practices.
5. Evaluate farm-specific feasibility when sufficient information is available.
6. Compare feasible alternatives using historical climate scenarios and documented indicators.
7. Explain the recommendations and their limitations.

**Current implementation status:** Steps 1–4 have been implemented at the structural level. The main recommendation interface has also been established. Farm-specific feasibility evaluation, scoring, and scenario comparisons remain under development.

---

## 2. Crop Database

ROOTED stores its initial crop library in:

`data/crops.csv`

The database contains five crops:

| Crop | Crop Family | Classification |
|---|---|---|
| Corn | Poaceae | Cash crop |
| Soybeans | Fabaceae | Cash crop |
| Oats | Poaceae | Cash crop |
| Winter wheat | Poaceae | Cash crop |
| Cereal rye | Poaceae | Cover crop |

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

The purpose of these checks is to prevent malformed crop records from entering the recommendation engine.

The crop database contains general descriptive information. It does not establish whether a crop is suitable for a particular farm.

---

## 3. Three-Year Rotation Generation

### 3.1 Candidate Generation

ROOTED generates three-entry cash-crop sequences using the function:

`generate_rotations(crops)`

The function is implemented in:

`src/recommendations/rotation_generator.py`

It first identifies all crops classified as cash crops.

It then generates every possible ordered sequence of three cash-crop identifiers using the Cartesian product.

For the current library:

- Number of cash crops: 4
- Number of positions: 3
- Repeated crops: Allowed

The total number of candidate sequences is:

**4³ = 64**

Examples include:

- Corn → Soybeans → Corn
- Corn → Oats → Soybeans
- Soybeans → Corn → Winter Wheat
- Corn → Corn → Corn

These examples demonstrate the generator's behavior. They are not agricultural recommendations.

### 3.2 Why Repeated Crops Are Allowed

The generator does not automatically exclude repeated crops.

For example:

`("corn", "corn", "corn")`

is a structurally valid candidate.

This does not mean continuous corn is recommended.

Instead, ROOTED separates the generation of possible sequences from the evaluation of their agricultural suitability.

Excluding crops or sequences requires documented rules rather than unsupported assumptions.

### 3.3 Interpretation of Three-Year Sequences

The current implementation uses three ordered crop entries as a simplified representation of a three-year rotation.

However, a three-entry sequence is not automatically a verified three-calendar-year planting schedule.

Some crops, including winter wheat, grow across calendar years.

A future scheduling component must account for actual planting dates, harvest dates, and field occupancy before determining whether a proposed sequence is feasible.

---

## 4. Crop and Cover-Crop Validation

ROOTED distinguishes structural validation from agricultural feasibility evaluation.

### 4.1 Cash-Crop Rotation Validation

The function:

`validate_rotation(rotation, crops)`

is implemented in:

`src/recommendations/crop_rules.py`

A structurally valid rotation must:

- Contain exactly three cash-crop entries.
- Use crop identifiers registered in the crop database.
- Exclude cover crops from cash-crop positions.

Repeated crops are permitted.

A sequence that passes these checks is considered **structurally valid**, not necessarily agriculturally feasible.

### 4.2 Cover-Crop Classification

Optional cover crops are stored separately from cash crops.

The function:

`validate_cover_crop(cover_crop_id, crops)`

verifies that a crop identifier is registered as a cover crop.

It does not determine whether that crop can be successfully established or managed on a particular farm.

### 4.3 Agricultural Feasibility Requirements

Before ROOTED presents a crop rotation as agriculturally feasible, the system must consider:

- Local planting and harvest windows.
- Crop suitability for local soil and climate conditions.
- Field drainage and irrigation availability.
- Required equipment.
- Farmer preferences and restrictions.
- Market access.
- Compatibility between consecutive crops.

These checks require farm-specific information and supporting agricultural evidence.

Until those inputs are available, ROOTED must not classify a generated candidate as a confirmed feasible rotation.

---

## 5. Optional Cover-Crop Practices

### 5.1 Cover-Crop Representation

ROOTED represents cover crops as optional management practices rather than additional cash-crop rotation entries.

The current cover crop is cereal rye.

The function:

`create_cover_crop_practice(cover_crop_id, after_year, crops)`

is implemented in:

`src/recommendations/rotation_generator.py`

A proposed practice contains:

| Field | Description |
|---|---|
| `cover_crop_id` | Identifier of the proposed cover crop |
| `after_year` | Position of the preceding cash-crop entry |
| `before_year` | Position of the following cash-crop entry |
| `feasibility_status` | Current feasibility evaluation status |

For a three-entry sequence, the initial implementation permits proposed cover-crop positions between entries 1–2 and 2–3.

These positions represent potential management opportunities, not verified planting windows.

### 5.2 Feasibility Status

New cover-crop practices are assigned:

`not_evaluated`

This means the practice has been represented but its agricultural feasibility has not been established.

### 5.3 Cover-Crop Feasibility Requirements

Before ROOTED recommends a cover crop between two cash crops, the system must evaluate:

- Harvest timing of the preceding cash crop.
- Available establishment window.
- Cover-crop termination requirements.
- Planting window of the following cash crop.
- Available equipment and management options.
- Relevant local environmental and field conditions.

These requirements are particularly important for cereal rye because its growing period can extend from fall into spring.

A proposed cover-crop practice must not be presented as feasible until the relevant timing and management constraints have been evaluated.

---

## 6. NASA Climate Data and Unit Handling

### 6.1 Environmental Data Source

ROOTED receives environmental information from the NASA POWER processing pipeline.

The climate-data team has collected daily temperature and precipitation data for 2005–2025 for the Ames, Iowa demonstration area.

Initial processed outputs include May–September growing-season summaries.

Additional seasonal summaries are under consideration because crops such as winter wheat and cereal rye grow outside the main summer period.

### 6.2 Climate Scenario Integration

ROOTED is designed to receive historical climate scenarios through the agreed recommendation-engine interface.

The planned scenario categories are:

- Dry
- Typical
- Wet

These scenarios will be supplied by the climate-data component.

The recommendation engine will not independently invent climate observations or substitute synthetic environmental measurements for missing data.

Scenario definitions, aggregation periods, and input units must be documented before numerical comparisons are implemented.

### 6.3 Evapotranspiration-Related Energy Flux

The climate-data team has identified an ET-related variable reported in:

**MJ/m²/day**

This is an energy-flux unit rather than a water-depth unit.

Precipitation measurements may be expressed in millimeters.

ROOTED must not directly subtract an energy-flux measurement from precipitation to estimate water balance.

Before calculating any precipitation-minus-evapotranspiration indicator, the team must:

1. Confirm the exact NASA POWER parameter.
2. Verify its physical definition.
3. Determine whether conversion to water-depth units is scientifically appropriate.
4. Document the conversion method and assumptions.
5. Ensure that measurements refer to compatible time periods.

Until those conditions are satisfied, the ET-related variable will remain a separate environmental indicator.

### 6.4 Climate Data Limitations

NASA POWER provides gridded environmental estimates rather than direct observations from an individual farm.

These data can support historical environmental comparisons but cannot independently establish field-level crop suitability, future yield, or actual soil-water availability.

ROOTED must preserve the original variable definitions, units, and time periods when processing environmental inputs.

---

## 7. Recommendation Engine Interface

The team has agreed to use the following main function:

```python
def recommend_rotations(farm, scenarios, priorities):
    ...
```

This function is located in:

`src/recommendations/scoring.py`

### 7.1 Inputs

**`farm`**

A dictionary intended to contain the farm profile, including the existing rotation and relevant management constraints.

**`scenarios`**

A dictionary intended to contain processed environmental scenarios supplied by the climate-data component.

**`priorities`**

A dictionary intended to contain farmer preferences used when comparing rotations.

The exact input fields and schemas must be finalized during team integration.

### 7.2 Outputs

The current interface returns a dictionary containing:

| Key | Purpose |
|---|---|
| `baseline` | Evaluation of the farmer's existing rotation |
| `recommendations` | Candidate recommendations |
| `scenario_results` | Comparison results under environmental scenarios |
| `limitations` | Important limitations or missing evaluation steps |

### 7.3 Current Implementation

The function currently validates that its three inputs are dictionaries.

It returns an empty recommendation structure and explicitly reports that scoring, farm-specific feasibility, and climate-variable validation remain incomplete.

This is intentional.

The interface establishes how the application's components will communicate without presenting unimplemented evaluations as completed results.

---

## 8. Planned Rotation Evaluation

ROOTED's next development phase will introduce indicators for comparing candidate rotations.

Potential indicators include:

- Number of distinct crop species.
- Number of distinct crop families.
- Repetition of crop species.
- Potential seasonal soil-cover opportunities.
- Compatibility with documented farm constraints.
- Historical climate exposure under validated scenarios.

### 8.1 Crop Diversity

Crop-species diversity and crop-family diversity will be considered separately.

For example, corn, oats, and winter wheat are different crop species but all belong to the Poaceae family.

Therefore, counting distinct crop species alone does not fully describe crop-family diversity.

These indicators describe rotation composition.

They do not directly measure soil-health improvement.

### 8.2 Soil Protection

ROOTED may consider seasonal soil cover as a potential soil-protection indicator.

However, the presence of a cover crop in a proposed sequence does not establish that it can be planted successfully or that a measurable soil-health benefit will occur.

Any future soil-protection scoring must distinguish between:

- Observable or computable characteristics.
- Evidence-supported qualitative considerations.
- Outcomes that cannot be established from the available data.

### 8.3 Farmer Priorities

Farmer priorities may eventually influence how feasible rotations are compared.

However, priority weights and scoring methods must be explicitly defined and documented.

The engine must not invent preference weights when they have not been provided.

### 8.4 Baseline Comparison

ROOTED is designed to compare alternative rotations against the farmer's existing rotation.

A baseline evaluation requires an actual farm profile and a documented evaluation method.

Until those inputs are available, ROOTED must not invent a baseline rotation or assign unsupported baseline scores.

---

## 9. Testing and Validation

ROOTED uses `pytest` to validate the recommendation engine's implemented functionality.

The automated tests cover:

- Crop database loading.
- Missing and duplicate crop data.
- Invalid crop classifications and seasons.
- Cash-crop rotation validation.
- Cover-crop classification.
- Optional cover-crop practice representation.
- Three-entry rotation generation.
- Exclusion of cover crops from cash-crop sequences.
- Allowance of repeated cash crops.

The generator has also been checked to produce 64 candidate sequences from the current four cash crops.

These tests verify software behavior and structural consistency.

They do not validate agricultural feasibility or the accuracy of future recommendation scores.

---
### Drought-Resilience Ranking

For historical dry-scenario comparison, ROOTED uses a simple ordinal
drought-resilience ranking for the four demonstration cash crops.

The ranking is based on qualitative extension evidence describing crop
responses to moisture stress. The values are relative rank positions,
not measured drought-tolerance coefficients, yield-loss estimates, or
predicted agronomic outcomes.

Current ranking:

1. Corn
2. Soybean
3. Oats
4. Winter wheat

Higher values indicate greater relative drought resilience within the
limited demonstration crop set.

The dry-scenario ranking is used only as a transparent decision-support
heuristic. It does not replace field-specific agronomic assessment.

Wet scenarios are not currently assigned crop-specific excess-moisture
scores because seasonal precipitation totals do not establish flooding,
waterlogging, soil saturation, or drainage conditions.

## 10. Current Limitations

The recommendation engine currently supports crop-data validation, structural rotation validation, candidate generation, and optional cover-crop representation.

It does not yet evaluate:

- Field-level crop suitability.
- Exact planting and harvest schedules.
- Equipment or market feasibility.
- Crop-specific climate stress.
- Measured soil-health improvements.
- Crop yields.
- Farm profitability.
- Validated numerical rotation scores.
- Scenario-based regret.

These capabilities require additional data, agricultural evidence, and documented evaluation methods.

**ROOTED is intended to support farmer decision-making, not replace local agronomic expertise or field-specific assessment.**

---

## 11. Supporting Documentation

Agricultural references, NASA data sources, crop classifications, and outstanding evidence gaps are documented in:

`docs/data_sources.md`

This methodology document describes the recommendation engine's implemented behavior and planned evaluation framework.

Future updates should distinguish completed functionality from proposed features and document the evidence supporting any new feasibility rules or numerical indicators.