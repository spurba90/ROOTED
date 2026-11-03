from src.recommendations.crop_rules import validate_rotation


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



def recommend_rotations(farm, scenarios, priorities):
    """
    Main entry point for ROOTED's recommendation engine.
    """
    if not isinstance(farm, dict):
        raise TypeError("farm must be a dictionary")

    if not isinstance(scenarios, dict):
        raise TypeError("scenarios must be a dictionary")

    if not isinstance(priorities, dict):
        raise TypeError("priorities must be a dictionary")

    return {
        "baseline": None,
        "recommendations": [],
        "scenario_results": {},
        "limitations": [
            "Recommendation scoring has not been implemented.",
            "Farm-specific feasibility has not been evaluated.",
            "Climate variables and units require validation."
        ]
    }

