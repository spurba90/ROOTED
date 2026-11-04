from src.recommendations.crop_rules import validate_rotation
from src.recommendations.crop_data import (
    load_crops,
    load_crop_climate_traits,
)
from src.recommendations.rotation_generator import generate_rotations

from src.recommendations.rotation_generator import (
    generate_rotations,
    create_cover_crop_practice,
)

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

    return {
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
    crop_diversity = indicators["unique_crop_count"] / 3

    repeat_avoidance = 1 - (
        indicators["adjacent_repeat_count"] / 2
    )

    return {
        "crop_diversity": crop_diversity,
        "repeat_avoidance": repeat_avoidance,
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
    }

    missing = required_components - set(baseline_components)

    if missing:
        raise ValueError(
            f"Missing baseline components: {sorted(missing)}"
        )

    values = [
        baseline_components["crop_diversity"],
        baseline_components["repeat_avoidance"],
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
            "No weighted scoring components are available"
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

    return {
        "score": score,
        "components": component_values,
        "effective_weights": effective_weights,
        "unavailable_components": unavailable_components,
    }



def calculate_dry_resilience_index(rotation, climate_traits):
    """
    Calculate a normalized relative drought-resilience index
    for a three-crop rotation.

    The index is based on ordinal crop ranks from the documented
    climate-trait table. It is a model heuristic, not a measured
    yield response or drought-tolerance coefficient.
    """
    ranks = []

    for crop_id in rotation:
        if crop_id not in climate_traits:
            raise ValueError(
                f"Missing climate traits for crop: {crop_id}"
            )

        ranks.append(
            climate_traits[crop_id]["dry_resilience_rank"]
        )

    all_ranks = [
        traits["dry_resilience_rank"]
        for traits in climate_traits.values()
    ]

    min_rank = min(all_ranks)
    max_rank = max(all_ranks)

    if min_rank == max_rank:
        raise ValueError(
            "Climate trait ranks must contain more than one rank"
        )

    normalized_ranks = [
        (rank - min_rank) / (max_rank - min_rank)
        for rank in ranks
    ]

    return sum(normalized_ranks) / len(normalized_ranks)



def calculate_scenario_climate_component(
    rotation,
    climate_traits,
    scenario_id,
):
    """
    Calculate the climate component available for a historical scenario.

    Dry scenarios use the documented relative drought-resilience index.
    Typical and wet scenarios currently return no crop-specific climate
    score because validated crop-specific rules are not yet available.
    """
    if scenario_id == "dry":
        return {
            "value": calculate_dry_resilience_index(
                rotation,
                climate_traits,
            ),
            "status": "available",
            "basis": "relative_drought_resilience",
        }

    if scenario_id in {"typical", "wet"}:
        return {
            "value": None,
            "status": "not_scored",
            "basis": None,
        }

    raise ValueError(
        f"Unknown climate scenario: {scenario_id}"
    )




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
    }


def score_rotation_for_scenario(
    rotation,
    crops,
    climate_traits,
    priorities,
    scenario_id,
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
        climate_traits,
        scenario_id,
    )

    weighted_result = calculate_weighted_rotation_score(
        structural_soil_proxy,
        climate_component,
        priorities,
    )

    return {
        "rotation": tuple(rotation),
        "scenario_id": scenario_id,
        "indicators": indicators,
        "baseline_components": baseline_components,
        "structural_soil_proxy": structural_soil_proxy,
        "climate_component": climate_component,
        "score": weighted_result["score"],
        "effective_weights": weighted_result["effective_weights"],
        "unavailable_components": weighted_result[
            "unavailable_components"
        ],
    }


def rank_rotations_for_scenario(
    rotations,
    crops,
    climate_traits,
    priorities,
    scenario_id,
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
            climate_traits,
            priorities,
            scenario_id,
        )

        results.append(result)

    return sorted(
        results,
        key=lambda item: (
            -item["score"],
            item["rotation"],
        ),
    )

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
    adjacent_repeat_count = indicators["adjacent_repeat_count"]

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

    if adjacent_repeat_count == 0:
        explanations.append(
            "Avoids planting the same cash crop in consecutive years."
        )
    else:
        explanations.append(
            f"Contains {adjacent_repeat_count} adjacent repeated-crop "
            f"transition(s)."
        )

    if (
        climate_component["status"] == "available"
        and climate_component["basis"]
        == "relative_drought_resilience"
    ):
        explanations.append(
            "Dry-scenario ranking includes the documented relative "
            "drought-resilience trait component."
        )
    else:
        explanations.append(
            "No crop-specific climate component is applied for this scenario."
        )

    if "water_suitability" in result["unavailable_components"]:
        explanations.append(
            "Water suitability is not currently included in the score."
        )

    return explanations

def build_cover_crop_options(crops):
    """
    Build optional cover-crop practices for recommendation cards.

    These options are structurally valid but remain unevaluated for
    farm-specific feasibility.
    """
    return [
        create_cover_crop_practice(
            "cereal_rye",
            after_year,
            crops,
        )
        for after_year in (1, 2)
    ]

def build_baseline_result(
    farm,
    crops,
    climate_traits,
    priorities,
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

    for scenario_id in ("dry", "typical", "wet"):
        scenario_scores[scenario_id] = score_rotation_for_scenario(
            current_rotation,
            crops,
            climate_traits,
            priorities,
            scenario_id,
        )

    return {
        "rotation": tuple(current_rotation),
        "scenario_scores": scenario_scores,
    }

def recommend_rotations(farm, scenarios, priorities):
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

    required_scenarios = {"dry", "typical", "wet"}

    if set(scenarios) != required_scenarios:
        raise ValueError(
            "scenarios must contain dry, typical, and wet"
        )

    crops = load_crops()
    climate_traits = load_crop_climate_traits()

    baseline = build_baseline_result(
        farm,
        crops,
        climate_traits,
        priorities,
    )

    rotations = generate_rotations(crops)

    soil_factors = prepare_soil_factors(farm)

    cover_crop_options = build_cover_crop_options(crops)

    scenario_results = {}

    for scenario_id in ("dry", "typical", "wet"):
        scenario_results[scenario_id] = rank_rotations_for_scenario(
            rotations,
            crops,
            climate_traits,
            priorities,
            scenario_id,
        )

    dry_rankings = scenario_results["dry"]

    recommendations = []

    for result in dry_rankings[:3]:
        recommendations.append({
            "rotation": result["rotation"],
            "score": result["score"],
            "scenario_id": "dry",
            "structural_soil_proxy": result[
                "structural_soil_proxy"
            ],
            "climate_component": result[
                "climate_component"
            ],
            "effective_weights": result[
                "effective_weights"
            ],
            "unavailable_components": result[
                "unavailable_components"
            ],
            "why": build_rotation_explanations(result),
            "cover_crop_options": cover_crop_options,
        })

    return {
    "baseline": baseline,
    "recommendations": recommendations,
    "scenario_results": scenario_results,
    "soil_factors": soil_factors,
    "limitations": [
        "Soil measurements may be unavailable and are not imputed.",
        "Water suitability is not currently scored.",
        "Dry-scenario climate scoring uses relative drought-resilience traits.",
        "Typical and wet scenarios do not currently use crop-specific climate scores.",
        "Scores are decision-support heuristics, not yield or soil-health predictions.",
    ],
}