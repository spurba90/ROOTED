import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from src.ui import engine_bridge


def test_water_only_is_blocked():
    _, err = engine_bridge.run({"weights": {"soil": 0, "water": 5, "resilience": 0}})
    assert err and "Water" in err


def test_all_zero_is_blocked():
    _, err = engine_bridge.run({"weights": {"soil": 0, "water": 0, "resilience": 0}})
    assert err


def test_inputs_map_to_engine_ids():
    farm, pri = engine_bridge.build_inputs({"current_rotation": ["Corn", "Soybeans", "Oats"], "prior_crop": "Winter wheat",
                                            "irrigation_available": True, "weights": {"soil": 5, "water": 3, "resilience": 2}})
    assert farm["current_rotation"] == ("corn", "soybean", "oats") and farm["prior_crop"] == "winter_wheat"
    assert pri == {"soil_protection": 5, "water_suitability": 3, "climate_resilience": 2}


def test_unknown_prior_crop_is_omitted():
    farm, _ = engine_bridge.build_inputs({"prior_crop": "Unknown / other", "weights": {"soil": 1, "water": 0, "resilience": 0}})
    assert "prior_crop" not in farm


def test_all_pages_render():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    for page in ["Dashboard", "Farm Profile", "Farm Memory", "Rotation Advisor", "Climate Replay"]:
        at.session_state["page"] = page
        at.run()
        assert not at.exception, (page, at.exception)
