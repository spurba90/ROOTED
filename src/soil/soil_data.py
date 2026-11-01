# preethi - for preparing the farm's soil information.
# iowa demonstration farm soil profile
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = (PROJECT_ROOT / "data" / "processed" / "ames_soil_profile.json")

def build_soil_profile():
    """Create a demo farm profile without inventing soil values."""
    return {
        "farm_id": "iowa_demo_01",
        "location": {
            "name": "Ames, Iowa",
            "latitude": 42.03,
            "longitude": -93.62
        },
        "soil": {
            "texture": None,
            "ph": None,
            "organic_matter_pct": None,
            "drainage_class": None,
            "available_water_capacity": None
        },
        "source": {
            "name": "USDA NRCS Web Soil Survey",
            "url": "https://websoilsurvey.nrcs.usda.gov/app/",
            "status": "not_yet_retrieved"
        },
        "limitations": [
            "Demo coordinates do not identify a surveyed farm field.",
            "Soil properties have not been verified for this location.",
            "Missing soil values must not be treated as zero.",
            "Soil-dependent recommendations require verified or farmer-provided inputs."
        ]
    }

if __name__ == "__main__":
    profile = build_soil_profile()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as file:
        json.dump(profile, file, indent=2)
    print(json.dumps(profile, indent=2))
    print("\nSaved to:", OUTPUT_FILE)