from src.recommendations.crop_rules import validate_rotation

from src.recommendations.crop_data import (
    load_crops,
    load_crop_critical_windows,
)
from src.recommendations.climate_inputs import validate_climate_scenarios
from src.recommendations.climate_timing import (
    load_monthly_precip_totals,
    calculate_monthly_percentiles,
    build_jul_aug_stress_scenario,
    build_climate_profiles,
)

from src.recommendations.regret import calculate_scenario_regret

from src.recommendations.rotation_generator import (
    generate_rotations,
    create_cover_crop_practice,
    canonical_cycle,
    rotation_id,
)

# dry / typical / wet come from the climate team's scenario file.
# jul_aug_dry is built by the engine from the NASA daily file.
SCENARIO_IDS = ("dry", "typical", "wet", "jul_aug_dry")


# The three priorities a farmer can set. Every one must be supplied
# (use 0 for "don't care") so a misspelled name can't silently vanish.
PRIORITY_NAMES = {"soil_protection", "water_suitability", "climate_resilience"}

def calculate_rotation_indicators(rotation, crops, cover_crop_practice=None):
    """
    Calculate transparent structural indicators for a three-year rotation.

    These indicators describe the rotation but do not claim measured
    soil-health improvements.
    """
    validate_rotation(rotation, crops)

    crop_lookup = {
        crop["crop_id"]: crop
        for crop in crops
    }

    crop_families = [
        crop_lookup[crop_id]["crop_family"]
        for crop_id in rotation
    ]

    adjacent_repeat_count = sum(
        rotation[index] == rotation[index + 1]
        for index in range(len(rotation) - 1)
    )

    same_family_transition_count = sum(
        crop_families[index] == crop_families[index + 1]
        for index in range(len(crop_families) - 1)
    )

    transitions = [
        (index, (index + 1) % len(rotation))
        for index in range(len(rotation))
    ]

    cyclic_repeat_count = sum(
        rotation[a] == rotation[b]
        for a, b in transitions
    )

    cyclic_same_family_count = sum(
        crop_families[a] == crop_families[b]
        for a, b in transitions
    )

    return {
        "cyclic_repeat_count": cyclic_repeat_count,
        "cyclic_same_family_count": cyclic_same_family_count,
        "unique_crop_count": len(set(rotation)),
        "unique_family_count": len(set(crop_families)),
        "adjacent_repeat_count": adjacent_repeat_count,
        "same_family_transition_count": same_family_transition_count,
        "cover_crop_present": cover_crop_practice is not None,
    }


def calculate_baseline_components(indicators):
    """
    Convert rotation indicators into normalized baseline components.

    These values describe rotation structure on a 0–1 scale.
    They are model mechanics, not measured agronomic outcomes.

    Parameters
    ----------
    indicators : dict
        Output from calculate_rotation_indicators().

    Returns
    -------
    dict
        Normalized structural components.
    """
    crop_diversity = (indicators["unique_crop_count"] - 1) / 2

    repeat_avoidance = 1 - (
        indicators["cyclic_repeat_count"] / 3
    )

    family_alternation = 1 - (
        indicators["cyclic_same_family_count"] / 3
    )

    return {
        "crop_diversity": crop_diversity,
        "repeat_avoidance": repeat_avoidance,
        "family_alternation": family_alternation,
    }



def calculate_structural_soil_proxy(baseline_components):
    """
    Combine normalized rotation-structure components into a
    soil-protection proxy.

    This is a model heuristic based on rotation structure.
    It is not a measurement or prediction of soil health.
    """
    required_components = {
        "crop_diversity",
        "repeat_avoidance",
        "family_alternation",
    }

    missing = required_components - set(baseline_components)

    if missing:
        raise ValueError(
            f"Missing baseline components: {sorted(missing)}"
        )

    values = [
        baseline_components["crop_diversity"],
        baseline_components["repeat_avoidance"],
        baseline_components["family_alternation"],
    ]

    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                "Baseline components must be numeric"
            )

        if not 0 <= value <= 1:
            raise ValueError(
                "Baseline components must be between 0 and 1"
            )

    return sum(values) / len(values)



def calculate_weighted_rotation_score(
    structural_soil_proxy,
    climate_component,
    priorities,
):
    """
    Combine available recommendation components using farmer priorities.

    Missing or unscored components are excluded rather than treated
    as zero. Remaining priority weights are renormalized across the
    components that are actually available.

    Returns
    -------
    dict
        Final normalized score, effective weights, component values,
        and unavailable components.
    """
    if isinstance(structural_soil_proxy, bool) or not isinstance(
        structural_soil_proxy, (int, float)
    ):
        raise TypeError(
            "structural_soil_proxy must be numeric"
        )

    if not 0 <= structural_soil_proxy <= 1:
        raise ValueError(
            "structural_soil_proxy must be between 0 and 1"
        )

    if not isinstance(climate_component, dict):
        raise TypeError(
            "climate_component must be a dictionary"
        )

    normalized_priorities = normalize_priority_weights(priorities)

    component_values = {
        "soil_protection": structural_soil_proxy,
        "water_suitability": None,
        "climate_resilience": (
            climate_component.get("value")
            if climate_component.get("status") == "available"
            else None
        ),
    }

    available_components = {
        name: value
        for name, value in component_values.items()
        if value is not None
        and normalized_priorities.get(name, 0) > 0
    }

    if not available_components:
        raise ValueError(
            "No weighted scoring components are available: every "
            "priority above zero is for a component that is not scored "
            "yet (water suitability is not scored). Set soil protection "
            "or climate resilience above zero."
        )

    available_weight_total = sum(
        normalized_priorities[name]
        for name in available_components
    )

    effective_weights = {
        name: normalized_priorities[name] / available_weight_total
        for name in available_components
    }

    score = sum(
        component_values[name] * effective_weights[name]
        for name in available_components
    )

    unavailable_components = [
        name
        for name, value in component_values.items()
        if value is None
    ]

    dropped_priority_share = sum(
        normalized_priorities[name]
        for name in unavailable_components
    )

    return {
        "score": score,
        "components": component_values,
        "effective_weights": effective_weights,
        "unavailable_components": unavailable_components,
        "dropped_priority_share": dropped_priority_share,
    }


def calculate_scenario_climate_component(
    rotation,
    crop_windows,
    climate_profile,
):
    """
    Score how many rotation years would have their crop's
    drought-sensitive month fall in a historically dry month
    of this scenario's representative year.

    1.0 = no crop's sensitive month was in the driest quarter of
    the record for that month. Lower = more exposed. Wet months are
    not penalized; excess water is not evaluated.
    """
    exposed_crops = []

    for crop_id in rotation:
        if crop_id not in crop_windows:
            raise ValueError(
                f"Missing critical window for crop: {crop_id}"
            )

        month = crop_windows[crop_id]["critical_month"]

        if month not in climate_profile["month_percentiles"]:
            raise ValueError(
                f"Critical month {month} for {crop_id} is outside "
                f"the scenario season"
            )

        if month in climate_profile["dry_months"]:
            exposed_crops.append(crop_id)

    return {
        "value": 1 - len(exposed_crops) / len(rotation),
        "status": "available",
        "basis": "critical_window_dry_exposure",
        "exposed_year_count": len(exposed_crops),
        "exposed_crops": exposed_crops,
        "representative_year": climate_profile["representative_year"],
        "dry_months": climate_profile["dry_months"],
    }


def normalize_priority_weights(priorities):
    """
    Normalize farmer-selected priority values so they sum to 1.

    The function does not assign priorities for the farmer.
    It only converts supplied non-negative values into relative weights.

    Parameters
    ----------
    priorities : dict
        Farmer-selected priority values.

    Returns
    -------
    dict
        Priority weights that sum to 1.
    """
    if not isinstance(priorities, dict):
        raise TypeError("priorities must be a dictionary")

    if not priorities:
        raise ValueError("priorities cannot be empty")

    for name, value in priorities.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"Priority '{name}' must be numeric"
            )

        if value < 0:
            raise ValueError(
                f"Priority '{name}' cannot be negative"
            )
    unknown = set(priorities) - PRIORITY_NAMES
    missing = PRIORITY_NAMES - set(priorities)

    if unknown:
        raise ValueError(
            f"Unknown priority name(s): {sorted(unknown)}. "
            f"Expected: {sorted(PRIORITY_NAMES)}"
        )

    if missing:
        raise ValueError(
            f"Missing priority value(s): {sorted(missing)}. "
            f"Use 0 for priorities the farmer does not want to weight."
        )

    total = sum(priorities.values())

    if total == 0:
        raise ValueError(
            "At least one priority must be greater than zero"
        )

    return {
        name: value / total
        for name, value in priorities.items()
    }


def prepare_soil_factors(farm):
    """
    Prepare soil inputs for recommendation scoring without inventing
    missing values.

    Parameters
    ----------
    farm : dict
        Farm profile that may contain a nested "soil" dictionary.

    Returns
    -------
    dict
        Soil values, availability information, and missing fields.
    """
    if not isinstance(farm, dict):
        raise TypeError("farm must be a dictionary")

    soil = farm.get("soil")

    soil_fields = [
        "texture",
        "ph",
        "organic_matter_pct",
        "drainage_class",
        "available_water_capacity",
    ]

    if soil is None:
        return {
            "values": {
                field: None
                for field in soil_fields
            },
            "available_fields": [],
            "missing_fields": soil_fields,
            "soil_data_available": False,
            "soil_data_status": "none",
            "used_in_score": False,
        }

    if not isinstance(soil, dict):
        raise TypeError("farm['soil'] must be a dictionary")

    values = {
        field: soil.get(field)
        for field in soil_fields
    }

    available_fields = [
        field
        for field, value in values.items()
        if value is not None
    ]

    missing_fields = [
        field
        for field, value in values.items()
        if value is None
    ]

    return {
        "values": values,
        "available_fields": available_fields,
        "missing_fields": missing_fields,
        "soil_data_available": bool(available_fields),
        "soil_data_status": (
            "none" if not available_fields
            else "complete" if not missing_fields
            else "partial"
        ),
        "used_in_score": False,
    }


def score_rotation_for_scenario(
    rotation,
    crops,
    crop_windows,
    priorities,
    climate_profile,
    cover_crop_practice=None,
):
    """
    Score one rotation for one historical climate scenario.

    The score uses only currently available model components.
    Missing components are not treated as zero.
    """
    indicators = calculate_rotation_indicators(
        rotation,
        crops,
        cover_crop_practice,
    )

    baseline_components = calculate_baseline_components(
        indicators
    )

    structural_soil_proxy = calculate_structural_soil_proxy(
        baseline_components
    )

    climate_component = calculate_scenario_climate_component(
        rotation,
        crop_windows,
        climate_profile,
    )

    weighted_result = calculate_weighted_rotation_score(
        structural_soil_proxy,
        climate_component,
        priorities,
    )

    return {
        "rotation": tuple(rotation),
        "rotation_id": rotation_id(rotation),
        "scenario_id": climate_profile["scenario_id"],
        "indicators": indicators,
        "baseline_components": baseline_components,
        "structural_soil_proxy": structural_soil_proxy,
        "climate_component": climate_component,
        "score": weighted_result["score"],
        "effective_weights": weighted_result["effective_weights"],
        "unavailable_components": weighted_result[
            "unavailable_components"
        ],
        "score_basis": sorted(weighted_result["effective_weights"]),
        "dropped_priority_share": weighted_result["dropped_priority_share"],
        "comparable_across_scenarios": False,
    }


def rank_rotations_for_scenario(
    rotations,
    crops,
    crop_windows,
    priorities,
    climate_profile,
):
    """
    Score and rank candidate rotations for one climate scenario.

    Higher scores rank first. Rotation IDs are used as a deterministic
    tie-breaker when scores are equal.
    """
    results = []

    for rotation in rotations:
        result = score_rotation_for_scenario(
            rotation,
            crops,
            crop_windows,
            priorities,
            climate_profile,
        )

        results.append(result)

    ranked = sorted(
        results,
        key=lambda item: (
            -item["score"],
            item["rotation"],
        ),
    )

    cycles_per_score = {}

    for item in ranked:
        score_key = round(item["score"], 6)
        cycles_per_score.setdefault(score_key, set()).add(
            canonical_cycle(item["rotation"])
        )

    rank = 0
    previous_score = None

    for item in ranked:
        score_key = round(item["score"], 6)

        if score_key != previous_score:
            rank += 1
            previous_score = score_key

        item["rank"] = rank
        item["tied_with"] = len(cycles_per_score[score_key]) - 1
        item["cycle_id"] = canonical_cycle(item["rotation"])
        item["cycle_key"] = rotation_id(item["cycle_id"])

    return ranked


def select_recommendation_cards(ranked_results, limit=3, prior_crop=None):
    """
    Choose recommendation cards from a ranked list.

    Skips rotations that repeat a crop in consecutive years
    (including year 3 to year 1) and keeps one card per cycle.
    The full ranking is still returned separately.
    """
    cards = []
    seen_cycles = set()

    for result in ranked_results:
        if result["indicators"]["cyclic_repeat_count"] > 0:
            continue


        if prior_crop is not None and result["rotation"][0] == prior_crop:
            continue

        if result["cycle_id"] in seen_cycles:
            continue

        seen_cycles.add(result["cycle_id"])
        cards.append(result)

        if len(cards) == limit:
            break

    return cards

def build_rotation_explanations(result):
    """
    Build transparent explanation text from calculated rotation results.

    Explanations describe model mechanics only and do not claim
    measured agronomic outcomes.
    """
    explanations = []

    indicators = result["indicators"]
    climate_component = result["climate_component"]

    unique_crop_count = indicators["unique_crop_count"]
    cyclic_repeat_count = indicators["cyclic_repeat_count"]
    cyclic_same_family_count = indicators["cyclic_same_family_count"]

    if unique_crop_count == 3:
        explanations.append(
            "Uses three different cash crops across the three-year rotation."
        )
    elif unique_crop_count == 2:
        explanations.append(
            "Uses two different cash crops across the three-year rotation."
        )
    else:
        explanations.append(
            "Uses the same cash crop across the three-year rotation."
        )

    if cyclic_repeat_count == 0:
        explanations.append(
            "Does not plant the same cash crop in consecutive years, "
            "including when the rotation restarts (year 3 to year 1)."
        )
    else:
        explanations.append(
            f"Plants the same cash crop in consecutive years "
            f"{cyclic_repeat_count} time(s) per cycle when the rotation "
            f"is repeated (year 3 to year 1 included)."
        )

    if cyclic_same_family_count == 0:
        explanations.append(
            "Changes crop family every year (grass and legume alternate)."
        )
    elif indicators["unique_family_count"] == 1:
        explanations.append(
            "All crops are in the same plant family; the rotation "
            "includes no legume."
        )
    else:
        explanations.append(
            f"Includes more than one crop family; {cyclic_same_family_count} "
            f"of 3 year-to-year transitions stay within the same family."
        )

    if climate_component["status"] == "available":
        year = climate_component["representative_year"]
        exposed = climate_component["exposed_crops"]

        if exposed:
            names = ", ".join(sorted(set(exposed)))
            explanations.append(
                f"In {year}, rainfall in the drought-sensitive month of "
                f"{names} was in the driest quarter of 2005-2025 "
                f"({len(exposed)} of 3 rotation years exposed)."
            )
        else:
            explanations.append(
                f"In {year}, no crop in this rotation had its "
                f"drought-sensitive month in the driest quarter of "
                f"2005-2025."
            )
    else:
        explanations.append(
            "No crop-specific climate component is applied for this scenario."
        )

    tied_with = result.get("tied_with", 0)

    if tied_with:
        explanations.append(
            f"Tied with {tied_with} other rotation(s) at this score; "
            f"the order among tied rotations is not meaningful."
        )

    dropped_share = result.get("dropped_priority_share", 0)

    if dropped_share > 0:
        explanations.append(
            f"{round(dropped_share * 100)}% of the farmer's priority weight "
            f"is on water suitability, which is not scored yet, so it is "
            f"left out of this score."
        )
    elif "water_suitability" in result["unavailable_components"]:
        explanations.append(
            "Water suitability is not currently included in the score."
        )

    return explanations

def build_cover_crop_options(rotation, crops):
    """
    Build optional cereal-rye cover-crop practices that fit this
    rotation's crop calendar.

    A slot is skipped when the next cash crop is planted in the fall
    (winter wheat), because the cover crop would need the same fall
    planting window. Options remain unevaluated for farm-specific
    feasibility.
    """
    crop_lookup = {
        crop["crop_id"]: crop
        for crop in crops
    }

    options = []

    for after_year in (1, 2):
        next_crop = rotation[after_year]  # crop planted in year after_year + 1

        if crop_lookup[next_crop]["planting_season"] == "fall":
            continue

        practice = create_cover_crop_practice(
            "cereal_rye",
            after_year,
            crops,
        )

        if next_crop == "corn":
            practice["caution"] = (
                "Iowa State Extension recommends terminating cereal rye "
                "at least 10 days before planting corn to reduce the risk "
                "of seedling disease and yield loss."
            )

        options.append(practice)

    return options

def build_recommendation_card(result, crops, prior_crop=None):
    """
    Package one ranked result as a recommendation card for the UI.
    """
    return {
        "rotation": result["rotation"],
        "rotation_id": result["rotation_id"],
        "cycle_key": result["cycle_key"],
        "crops_by_year": [
            {"year": year, "crop_id": crop_id}
            for year, crop_id in enumerate(result["rotation"], start=1)
        ],
        "scenario_id": result["scenario_id"],
        "representative_year": result["climate_component"][
            "representative_year"
        ],
        "score": result["score"],
        "rank": result["rank"],
        "tied_with": result["tied_with"],
        "structural_soil_proxy": result["structural_soil_proxy"],
        "climate_component": result["climate_component"],
        "effective_weights": result["effective_weights"],
        "unavailable_components": result["unavailable_components"],
        "score_basis": result["score_basis"],
        "dropped_priority_share": result["dropped_priority_share"],
        "why": build_rotation_explanations(result) + (
            [
                f"Year 1 ({result['rotation'][0]}) differs from the "
                f"prior crop ({prior_crop})."
            ]
            if prior_crop is not None
            else []
        ),
        "follows_prior_crop": prior_crop,
        "cover_crop_options": build_cover_crop_options(
            result["rotation"],
            crops,
        ),
    }

def build_climate_replay(scenario_results, current_rotation=None):
    """
    Show how each rotation cycle ranks in every historical scenario.

    One row per distinct cycle (24 for four cash crops). Ranks are
    compared across scenarios, not scores, because scores are only
    comparable within a scenario. Rows are ordered by their rank in
    the typical scenario.
    """
    current_cycle = (
        canonical_cycle(current_rotation)
        if current_rotation is not None
        else None
    )

    rows = {}

    for scenario_id, ranked in scenario_results.items():
        for item in ranked:
            row = rows.setdefault(item["cycle_key"], {
                "cycle_key": item["cycle_key"],
                "cycle": item["cycle_id"],
                "repeats_crop": item["indicators"]["cyclic_repeat_count"] > 0,
                "is_current_rotation": item["cycle_id"] == current_cycle,
                "ranks": {},
                "tied_with": {},
                "exposed_crops": {},
            })

            if scenario_id in row["ranks"]:
                continue  # same cycle, different start year: same result

            row["ranks"][scenario_id] = item["rank"]
            row["tied_with"][scenario_id] = item["tied_with"]
            row["exposed_crops"][scenario_id] = sorted(
                set(item["climate_component"]["exposed_crops"])
            )

    regret = calculate_scenario_regret(scenario_results)

    for row in rows.values():
        ranks = list(row["ranks"].values())
        row["best_rank"] = min(ranks)
        row["worst_rank"] = max(ranks)
        row["rank_spread"] = row["worst_rank"] - row["best_rank"]

        row["regret"] = regret[row["cycle_key"]]
        row["max_regret_scenario"] = max(
            row["regret"],
            key=lambda scenario_id: row["regret"][scenario_id],
        )
        row["max_regret"] = row["regret"][row["max_regret_scenario"]]


    return sorted(
        rows.values(),
        key=lambda row: (row["ranks"].get("typical", 0), row["cycle_key"]),
    )

def build_baseline_result(
    farm,
    crops,
    crop_windows,
    priorities,
    climate_profiles,
):
    """
    Score the farmer's current rotation when one is provided.

    If no current rotation is supplied, no baseline is created.
    """
    current_rotation = farm.get("current_rotation")

    if current_rotation is None:
        return None

    validate_rotation(current_rotation, crops)

    scenario_scores = {}

    for scenario_id, climate_profile in climate_profiles.items():
        scenario_scores[scenario_id] = score_rotation_for_scenario(
            current_rotation,
            crops,
            crop_windows,
            priorities,
            climate_profile,
        )

    return {
        "rotation": tuple(current_rotation),
        "rotation_id": rotation_id(current_rotation),
        "scenario_scores": scenario_scores,
    }

def recommend_rotations(farm, scenarios, priorities, monthly_totals=None):
    """
    Main entry point for ROOTED's recommendation engine.

    Generates candidate rotations, ranks them under each supplied
    historical climate scenario, and returns structured results for
    the UI.
    """
    if not isinstance(farm, dict):
        raise TypeError("farm must be a dictionary")

    if not isinstance(scenarios, dict):
        raise TypeError("scenarios must be a dictionary")

    if not isinstance(priorities, dict):
        raise TypeError("priorities must be a dictionary")

    validate_climate_scenarios(scenarios)

    if monthly_totals is None:
        monthly_totals = load_monthly_precip_totals()

    monthly_percentiles = calculate_monthly_percentiles(monthly_totals)

    all_scenarios = dict(scenarios)
    all_scenarios["jul_aug_dry"] = build_jul_aug_stress_scenario(
        monthly_totals
    )

    climate_profiles = build_climate_profiles(
        all_scenarios,
        monthly_percentiles,
    )

    crops = load_crops()
    crop_windows = load_crop_critical_windows()


    prior_crop = farm.get("prior_crop")

    cash_crop_ids = {
        crop["crop_id"]
        for crop in crops
        if crop["crop_type"] == "cash"
    }

    if prior_crop is not None and prior_crop not in cash_crop_ids:
        raise ValueError(
            f"Unknown or non-cash prior crop: {prior_crop}"
        )
    irrigation_available = farm.get("irrigation_available")

    if irrigation_available is not None and not isinstance(
        irrigation_available, bool
    ):
        raise TypeError(
            "farm['irrigation_available'] must be True, False, or left out"
        )

    irrigation = {
        "irrigation_available": irrigation_available,
        "used_in_score": False,
        "note": (
            "Irrigation is reported but not used in scoring. Climate "
            "scores are based on rainfall only, so they may overstate "
            "dry-month exposure on irrigated fields."
            if irrigation_available
            else "Irrigation is not used in scoring."
        ),
    }


    baseline = build_baseline_result(
        farm,
        crops,
        crop_windows,
        priorities,
        climate_profiles,
    )

    rotations = generate_rotations(crops)

    soil_factors = prepare_soil_factors(farm)

    scenario_results = {}

    for scenario_id in SCENARIO_IDS:
        scenario_results[scenario_id] = rank_rotations_for_scenario(
            rotations,
            crops,
            crop_windows,
            priorities,
            climate_profiles[scenario_id],
        )

    scenario_context = {
        scenario_id: {
            "representative_year": scenario["representative_year"],
            "total_precip_mm": scenario["total_precip_mm"],
            "precip_anomaly_pct": scenario.get("precip_anomaly_pct"),
            "temp_anomaly_c": scenario.get("temp_anomaly_c"),
            "jul_aug_precip_mm": scenario.get("jul_aug_precip_mm"),
            "source": (
                "engine stress test from NASA POWER daily data"
                if scenario_id == "jul_aug_dry"
                else "climate team scenario file"
            ),
            "dry_months": climate_profiles[scenario_id]["dry_months"],
            "month_percentiles": climate_profiles[scenario_id][
                "month_percentiles"
            ],
        }
        for scenario_id, scenario in all_scenarios.items()
    }

    recommendations = {
        scenario_id: [
            build_recommendation_card(result, crops, prior_crop)
            for result in select_recommendation_cards(
                scenario_results[scenario_id],
                prior_crop=prior_crop,
            )
        ]
        for scenario_id in SCENARIO_IDS
    }

    climate_replay = build_climate_replay(
        scenario_results,
        farm.get("current_rotation"),
    )

    return {
    "baseline": baseline,
    "prior_crop": prior_crop,
    "recommendations": recommendations,
    "scenario_results": scenario_results,
    "scenario_context": scenario_context,
    "climate_replay": climate_replay,
    "soil_factors": soil_factors,
    "irrigation": irrigation,
    "limitations": [
        "Soil measurements may be unavailable and are not imputed.",
        "Water suitability is not currently scored.",
        "Climate scoring checks whether each crop's drought-sensitive month was in the driest quarter of 2005-2025 in each scenario year. It uses monthly rainfall only (no heat, soil moisture, or timing within the month).",
        "Crop sensitive months are typical Iowa timing assumptions, not field observations.",
        "Wet conditions (ponding, waterlogging) are not evaluated.",
        "Cover-crop options are only checked against the crop calendar (no rye slot before fall-planted winter wheat); farm-specific feasibility is not evaluated.",
        "Scores are decision-support heuristics, not yield or soil-health predictions.",
        "Scores are comparable only within the same scenario.",
        "If a prior crop is given, each card starts with a different crop; earlier field history is not considered.",
        "Climate replay compares ranks, not scores, across scenarios; a rank counts distinct score levels, so the same rank number can cover a different number of rotations in different scenarios.",
        "Regret is the gap between a rotation's score and the best score in the same scenario, in heuristic score units; it is not lost yield or income.",
        "Irrigation availability is reported but not used in scoring; climate scores reflect rainfall only.",
        "Recommendation cards are listed separately for each historical scenario; no single best-overall rotation is claimed.",
    ],
}