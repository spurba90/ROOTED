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

ROOTED must not assume cereal rye is appropriate between every pair of cash crops.

**Source:**

- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf

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
| USDA NRCS | Cereal Rye Cover Crop Fact Sheet | Cover-crop benefits, risks, and management considerations |

These are authoritative institutional sources. However, some references currently point to general resource pages rather than individual crop-specific publications.

Before finalizing the scientific documentation, ROOTED should verify each crop-specific claim against an identifiable publication or database record and record its publication date where available.

---

## 2. Crop Growing Seasons

ROOTED currently represents planting and harvest periods using broad seasonal categories.

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

Winter wheat and cereal rye require particular attention because their growing periods extend across calendar years.

For example, winter wheat planted in fall may occupy a field until the following summer.

Consequently, a three-entry crop sequence cannot automatically be interpreted as a verified three-calendar-year planting schedule.

ROOTED must evaluate crop timing separately before classifying a sequence as agriculturally feasible.

**Sources:**

- Iowa State University — Integrated Crop Management:  
  https://crops.extension.iastate.edu/
- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf

---

## 3. Crop Rotation Considerations

### 3.1 Rotation Feasibility Framework

ROOTED distinguishes between:

1. **Candidate generation:** Producing possible cash-crop sequences.
2. **Structural validation:** Checking whether a sequence follows the application's data rules.
3. **Agricultural feasibility:** Determining whether a sequence can realistically be implemented on a particular farm.
4. **Rotation evaluation:** Comparing feasible alternatives using documented indicators and farmer priorities.

A generated crop sequence is not automatically a feasible or recommended rotation.

### 3.2 Structural Rules

ROOTED currently enforces the following structural rules:

- A three-entry rotation must contain exactly three cash-crop identifiers.
- Every crop must exist in the validated crop database.
- Cover crops cannot occupy cash-crop positions.
- Repeated cash crops are permitted during candidate generation.
- Optional cover-crop practices are represented separately from cash-crop sequences.

The structural validation logic is implemented in:

`src/recommendations/crop_rules.py`

The candidate-generation logic is implemented in:

`src/recommendations/rotation_generator.py`

With four cash crops and three positions, ROOTED generates:

**4 × 4 × 4 = 64 candidate sequences**

These sequences are not confirmed agricultural recommendations.

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

### 3.4 Agronomic Considerations

ROOTED may eventually compare rotations using indicators related to:

- Crop diversity.
- Crop-family diversity.
- Seasonal soil cover.
- Potential cover-crop opportunities.
- Climate-related exposure.
- Farmer management constraints.

However, these characteristics must not automatically be interpreted as measured improvements in soil health, crop yield, or profitability.

For example, corn, oats, and winter wheat are three different crops, but all belong to the Poaceae family.

A rotation containing those crops has crop-species diversity without equivalent crop-family diversity.

ROOTED will not assign numerical agronomic benefits without supporting evidence and a documented methodology.

### 3.5 Current Feasibility Limitations

ROOTED uses Ames, Story County, Iowa, as its demonstration area.

The climate-data team has collected historical NASA POWER data for the area.

However, the characteristics of an individual demonstration farm have not yet been finalized.

ROOTED can currently generate and structurally validate candidate crop sequences.

It cannot yet confirm their agricultural feasibility without additional farm-specific information and crop-calendar constraints.

---

## 4. Cover Crop Practices

### 4.1 Initial Cover-Crop Option

ROOTED currently includes cereal rye as an optional cover-crop practice.

Cereal rye may provide winter soil cover, help reduce erosion, and take up residual soil nutrients.

However, its suitability depends on establishment timing, termination timing, the following cash crop, and farm management practices.

### 4.2 Optional Practice Representation

ROOTED represents cover crops separately from its three-entry cash-crop sequences.

A proposed practice contains the following fields:

| Field | Description |
|---|---|
| `cover_crop_id` | Identifier of the optional cover crop |
| `after_year` | Position of the preceding cash-crop entry |
| `before_year` | Position of the following cash-crop entry |
| `feasibility_status` | Whether agricultural feasibility has been evaluated |

For a three-entry cash-crop sequence, the initial implementation supports potential practice positions between entries 1–2 and 2–3.

The `after_year` and `before_year` fields describe positions in the crop sequence, not verified calendar-year planting dates.

### 4.3 Feasibility Status

The current implementation uses:

`not_evaluated`

This indicates that a potential practice has been represented but its agricultural feasibility has not been established.

The function responsible for creating these records is:

`create_cover_crop_practice()`

It is implemented in:

`src/recommendations/rotation_generator.py`

The function validates the cover-crop identifier and its position within the sequence.

It does not determine whether the cover crop can actually be established or managed.

### 4.4 Requirements for Agricultural Feasibility

Before ROOTED recommends cereal rye between two cash crops, the system must evaluate:

- Harvest timing of the preceding cash crop.
- Available cover-crop establishment window.
- Cover-crop termination requirements.
- Planting window of the following cash crop.
- Available equipment and management options.
- Relevant soil and environmental conditions.

Until these requirements can be evaluated, optional cover-crop practices must not be presented as confirmed feasible recommendations.

**Source:**

- USDA NRCS — Cereal Rye Cover Crop Fact Sheet:  
  https://www.nrcs.usda.gov/sites/default/files/2024-03/Cereal%20Rye%20Cover%20Crop%20Fact%20Sheet_0.pdf

---

## 5. NASA Environmental Data

### 5.1 NASA POWER

ROOTED uses historical climate information from NASA POWER for the Ames, Story County, Iowa demonstration area.

According to the climate-data team's progress report, the initial dataset includes daily temperature and precipitation data for 2005–2025.

The team has also prepared May–September growing-season summaries.

Additional seasonal summaries are being considered to account for crops growing outside the summer period, including winter wheat and cereal rye.

Dry, typical, and wet historical climate scenarios are under development.

**Source:**

- NASA POWER — Prediction Of Worldwide Energy Resources:  
  https://power.larc.nasa.gov/

### 5.2 Environmental Variables

The climate-data pipeline is expected to provide environmental information relevant to evaluating historical growing conditions.

| Variable | Intended Use | Important Limitation |
|---|---|---|
| Temperature | Characterize historical thermal conditions | Does not independently establish crop suitability |
| Precipitation | Characterize historical rainfall | Does not equal plant-available soil water |
| ET-related energy flux | Characterize an energy-related environmental variable | Must not be treated as water depth without a justified conversion |
| Seasonal climate summaries | Compare historical environmental conditions | Must cover periods relevant to the crops being evaluated |

The exact parameter names, units, temporal aggregation methods, and missing-data conventions must be confirmed with the climate-data team before integration.

### 5.3 Evapotranspiration-Related Data and Unit Handling

The climate-data team has identified an ET-related energy-flux variable reported in:

**MJ/m²/day**

This represents energy per unit area per day rather than water depth.

Precipitation, by contrast, may be expressed in millimeters.

ROOTED must not directly subtract an energy-flux value from precipitation to calculate a water-balance indicator.

The exact NASA POWER parameter and its physical interpretation must be confirmed before any conversion.

A precipitation-minus-evapotranspiration indicator may only be calculated after verifying the variable definition and using a documented method to express the relevant quantities in compatible units.

Until then, the ET-related energy flux must remain a separate environmental variable.

### 5.4 Spatial and Temporal Limitations

NASA POWER provides gridded meteorological estimates rather than direct measurements taken at an individual demonstration farm.

These estimates are useful for understanding historical regional environmental conditions but should not be presented as precise field-level observations.

Historical climate summaries also do not independently predict future crop yields or establish the suitability of individual rotations.

ROOTED will use the environmental data as supporting context for its evaluation framework, subject to the availability of validated inputs.

---

## 6. Limitations and Data Gaps

ROOTED's initial crop library and recommendation engine have several important limitations.

### 6.1 Farm-Specific Information

Although Ames, Iowa, has been selected as the demonstration area, the characteristics of an individual farm have not yet been finalized.

The engine still requires information about:

- Existing crop rotation.
- Soil characteristics and drainage.
- Irrigation availability.
- Equipment and management capabilities.
- Crop preferences and restrictions.
- Market access.

### 6.2 Crop Timing

The crop database currently uses broad seasonal categories rather than exact planting and harvest dates.

Therefore, generated three-entry sequences are not verified planting schedules.

This is particularly important for winter wheat and optional cereal rye practices.

### 6.3 Agricultural Feasibility

The current engine validates crop classifications and rotation structure.

It does not yet establish field-level agricultural feasibility.

Farm-specific and crop-calendar constraints must be evaluated before a candidate can be presented as a feasible alternative.

### 6.4 Environmental Data

NASA POWER data provides gridded historical environmental estimates rather than direct field measurements.

Climate scenario generation and validation of the ET-related variable are still in progress.

The recommendation engine must preserve variable definitions and units and must not combine incompatible measurements.

### 6.5 Soil Health and Agricultural Outcomes

Crop diversity and cover-crop inclusion do not automatically establish improvements in soil health.

ROOTED does not currently predict:

- Crop yield.
- Farm profitability.
- Measured soil-health improvement.
- Field-level water stress.
- Exact future climate conditions.

Any future scoring system must distinguish between measurable indicators, qualitative considerations, and outcomes that cannot be established from the available data.

### 6.6 Research and Citation Gaps

Some agricultural references currently point to institutional databases or resource homepages rather than individual publications.

Before final submission, the team should:

- Verify crop-specific claims against identifiable sources.
- Record publication dates where available.
- Confirm that agricultural guidance applies to the demonstration area.
- Document the exact NASA POWER parameters used.
- Record data units and processing methods.
- Clearly identify any remaining assumptions.

---

## 7. Implementation References

The following files contain the current crop-library and recommendation-engine foundation.

| File | Purpose |
|---|---|
| `data/crops.csv` | Initial crop library |
| `src/recommendations/crop_data.py` | Crop database loading and validation |
| `src/recommendations/crop_rules.py` | Structural crop and cover-crop validation |
| `src/recommendations/rotation_generator.py` | Candidate rotation generation and optional practice representation |
| `src/recommendations/scoring.py` | Agreed recommendation-function interface; scoring pending |
| `tests/test_recommendations.py` | Automated tests for crop and rotation logic |
| `docs/methodology.md` | Recommendation-engine methodology and feasibility requirements |

The current implementation generates **64 structurally valid candidate cash-crop sequences** from four cash crops.

It also supports representing optional cereal rye practices without asserting agricultural feasibility.

The agreed recommendation-engine interface is:

`recommend_rotations(farm, scenarios, priorities)`

The interface has been established, but farm-specific feasibility evaluation, scenario-based comparisons, and recommendation scoring remain future development tasks.

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

---
