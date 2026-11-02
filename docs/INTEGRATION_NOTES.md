# ROOTED integration notes (draft)

This UI is a prototype for Ames, Story County, Iowa. It currently uses synthetic
climate values and illustrative rotation sequences. Do not use them for farm
decisions or present them as NASA observations.

## Draft recommendation-engine call

The UI currently prepares a draft payload with this shape:

```python
payload = {
    "farm": {
        "location": {"city": "Ames", "county": "Story County", "state": "Iowa"},
        "field_acres": 40.0,
        "soil": {"type": "Silt loam", "notes": ""},
        "crop_history": ["Corn", "Soybeans", "Corn"],
        "current_rotation": "corn -> soybeans",
        "allowed_crops": ["Corn", "Soybeans", "Oats"],
        "irrigation": "No irrigation",
        "equipment_constraints": ["Standard row-crop equipment"],
    },
    "scenarios": None,  # Replace with Preethi's agreed climate schema
    "priorities": ["Improve soil health", "Reduce climate risk"],
}
```

This is a discussion draft, not a finalized contract. Sim, Preethi, and Dilpreet
should agree on exact names, required/optional fields, units, date formats, and
missing-data behavior before wiring the modules.

## Suggested engine return shape

```python
{
    "baseline_rotation": {...},
    "recommended_rotations": [
        {
            "rotation_id": "...",
            "crops_by_year": ["...", "...", "..."],
            "score": 0.0,
            "explanation": ["..."],
            "tradeoffs": ["..."],
            "scenario_results": {
                "dry": {...},
                "typical": {...},
                "wet": {...}
            }
        }
    ],
    "warnings": ["..."],
    "missing_data": ["..."],
    "assumptions": ["..."]
}
```

Agree whether scores are normalized (for example 0–100), how higher/lower scores
should be interpreted, and how scenario names map to historical periods.

## Run locally

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Before real-data wiring

- Confirm Preethi's climate variables, units, seasonal windows, source, and date coverage.
- Confirm Sim's input/output schema, crop-rule assumptions, scoring scale, and warnings.
- Keep raw source values and metadata; don't silently fill missing values.
- Add tests for payload construction and rendering of missing-data warnings.
