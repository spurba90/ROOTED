import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from streamlit.testing.v1 import AppTest
from src.data_loader import load_farm_profile, load_scenarios
from src.recommendations import recommend_rotations


def _run(**over):
    farm = {**load_farm_profile()[0], **over}
    return recommend_rotations(farm, load_scenarios()[0], farm["weights"])


def test_contract_keys():
    r = _run()["rotations"][0]
    for k in ("rotation_id", "crops_by_year", "cover_crop", "score_components", "scenario_scores", "explanation", "limitations"):
        assert k in r


def test_scenarios_change_ranking():
    ranks = [{x["rotation_id"]: x["scenario_ranks"][s] for x in _run()["rotations"]} for s in ("typical", "dry")]
    assert ranks[0] != ranks[1]


def test_priorities_change_scores():
    a = _run(weights={"soil": 10, "water": 0, "resilience": 0})["rotations"][0]["total"]
    b = _run(weights={"soil": 0, "water": 10, "resilience": 0})["rotations"][0]["total"]
    assert a != b


def test_constraints_exclude():
    res = _run(allowed=["Corn", "Soybeans"])
    assert all("Oats" not in r["crops_by_year"] and "Alfalfa" not in r["crops_by_year"] for r in res["rotations"])
    assert res["excluded"]


def test_all_pages_render():
    at = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=30)
    for page in ["Dashboard", "Farm Profile", "Farm Memory", "Rotation Advisor", "Climate Replay"]:
        at.session_state["page"] = page
        at.run()
        assert not at.exception, (page, at.exception)
