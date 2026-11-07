
"""Connects the Streamlit pages to Sim's recommendation engine."""

import json
from pathlib import Path


CROP_ID = {
    "Corn": "corn",
    "Soybeans": "soybean",
    "Oats": "oats",
    "Winter wheat": "winter_wheat",
}

ID_LABEL = {v: k for k, v in CROP_ID.items()}

PRI_KEY = {
    "soil": "soil_protection",
    "water": "water_suitability",
    "resilience": "climate_resilience",
}

SOIL_FIELDS = [
    "texture",
    "ph",
    "organic_matter_pct",
    "drainage_class",
    "available_water_capacity",
]

def load_usda_soil_profile():
    """Load mapped USDA soil estimates for the Ames demonstration area."""
    project_root = Path(__file__).resolve().parents[2]
    profile_path = (
        project_root / "data" / "processed" / "ames_soil_profile.json"
    )

    try:
        with profile_path.open(encoding="utf-8") as file:
            profile = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    soil = profile.get("soil")

    if not isinstance(soil, dict):
        return None

    # Preserve missing values as None. Never substitute zero.
    return {
        field: soil.get(field)
        for field in SOIL_FIELDS
    }

def load_usda_soil_metadata():
    """Load the full USDA soil profile, including source and limitations."""
    project_root = Path(__file__).resolve().parents[2]
    profile_path = (
        project_root / "data" / "processed" / "ames_soil_profile.json"
    )

    try:
        with profile_path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def build_inputs(p):
    farm = {}

    rot = p.get("current_rotation")
    if rot and len(rot) == 3 and all(c in CROP_ID for c in rot):
        farm["current_rotation"] = tuple(CROP_ID[c] for c in rot)

    if p.get("prior_crop") in CROP_ID:
        farm["prior_crop"] = CROP_ID[p["prior_crop"]]

    if p.get("irrigation_available") in (True, False):
        farm["irrigation_available"] = bool(
            p["irrigation_available"]
        )

    # Pass mapped USDA estimates separately from farmer-entered answers.
    usda_soil = load_usda_soil_profile()
    if usda_soil is not None:
        farm["soil"] = usda_soil

    pri = {
        PRI_KEY[k]: int(v)
        for k, v in p["weights"].items()
    }

    return farm, pri


def run(p):
    """Returns (result, error_message). Exactly one of them is None."""
    farm, pri = build_inputs(p)

    if sum(pri.values()) == 0:
        return None, (
            "All three priorities are 0. "
            "Raise at least one slider in Farm Profile."
        )

    if (
        pri["water_suitability"] > 0
        and pri["soil_protection"] == 0
        and pri["climate_resilience"] == 0
    ):
        return None, (
            "Water suitability isn't scored yet. "
            "Raise soil protection or climate resilience too."
        )

    try:
        from src.recommendations.climate_inputs import (
            load_climate_scenarios,
        )
        from src.recommendations.scoring import recommend_rotations

    except ImportError as e:
        return None, (
            f"Sim's engine was not found ({e}). "
            "Merge Sim's branch first, and run Streamlit "
            "from the ROOTED folder."
        )

    try:
        return (
            recommend_rotations(
                farm,
                load_climate_scenarios(),
                pri,
            ),
            None,
        )
    except (ValueError, TypeError) as e:
        return None, f"Please check your inputs: {e}"
