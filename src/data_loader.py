"""Loads farm/climate data. Real files in data/processed/ override data/mock/ automatically.
Expected names: farm_profile.json, climate_annual.csv, climate_scenarios.csv, provenance.json"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIRS = [ROOT / "data" / "processed", ROOT / "data" / "mock"]


def _find(name):
    for d in DIRS:
        if (d / name).exists():
            return d / name
    raise FileNotFoundError(f"{name} not found in data/processed or data/mock")


def is_sample(path):
    return path.parent.name == "mock"


def load_farm_profile():
    p = _find("farm_profile.json")
    return json.loads(p.read_text(encoding="utf-8")), is_sample(p)


def load_climate_annual():
    p = _find("climate_annual.csv")
    df = pd.read_csv(p)
    df["p_minus_et_mm"] = df["precip_mm"] - df["ref_et_mm"]
    return df, is_sample(p)


def load_scenarios():
    p = _find("climate_scenarios.csv")
    df = pd.read_csv(p)
    df["scenario"] = df["scenario"].str.lower()
    df["p_minus_et_mm"] = df["precip_mm"] - df["ref_et_mm"]
    return df, is_sample(p)


def load_provenance():
    p = _find("provenance.json")
    return pd.DataFrame(json.loads(p.read_text(encoding="utf-8")))
