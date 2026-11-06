# preethi - USDA soil profile for the ROOTED Ames demonstration.
# Values come from USDA NRCS Soil Data Access.
# These are mapped soil survey estimates, not field measurements.

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ames_soil_profile.json"


def build_soil_profile():
    """Build a representative soil profile from retrieved USDA survey data."""

    return {
        "farm_id": "iowa_demo_01",
        "location": {
            "name": "Ames, Iowa",
            "latitude": 42.03,
            "longitude": -93.62
        },
        "soil": {
            "texture": "Loam",
            "ph": 6.2,
            "organic_matter_pct": 3.5,
            "drainage_class": "Well drained",
            "available_water_capacity": 0.21
        },
        "source": {
            "name": "USDA NRCS Soil Data Access",
            "url": "https://sdmdataaccess.sc.egov.usda.gov/",
            "status": "retrieved",
            "map_unit_key": "2765537",
            "map_unit_name": (
                "Clarion loam, Bemis moraine, 2 to 6 percent slopes"
            ),
            "component_key": "28635382",
            "component_name": "Clarion",
            "component_percentage": 85,
            "surface_horizon": "Ap",
            "surface_depth_cm": [0, 23],
            "awc_unit": "cm/cm"
        },
        "limitations": [
            "Demo coordinates identify a USDA mapped soil unit, not a verified individual farm field.",
            "Values represent the dominant Clarion component, estimated at 85 percent of the map unit.",
            "Texture, pH, organic matter, and available water capacity are representative values for the 0-23 cm surface horizon.",
            "Drainage class describes the mapped soil component, not a measured field drainage rate.",
            "Available water capacity is not current soil moisture or soil wetness.",
            "USDA soil survey estimates should be verified against field observations before making farm management decisions."
        ]
    }


if __name__ == "__main__":
    profile = build_soil_profile()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=2)

    print(json.dumps(profile, indent=2))
    print("\nSaved to:", OUTPUT_FILE)