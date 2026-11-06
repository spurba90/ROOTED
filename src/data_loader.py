"""Loads farm/climate data. Prefers Preethi's real files in data/processed/, falls back to data/mock/."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC, MOCK = ROOT / "data" / "processed", ROOT / "data" / "mock"
GROWING = "ames_growing_seasons_2005_2025.csv"
ET = "ames_seasonal_et_2005_2025.csv"
ANOM = "ames_climate_anomalies_2005_2025.csv"
SOIL = "ames_soil_profile.json"


def load_farm_profile():
    """Sample farm inputs (data/mock) with location and farm_id taken from Preethi's soil profile if present."""
    d = json.loads((MOCK / "farm_profile.json").read_text(encoding="utf-8"))
    sp = PROC / SOIL
    if sp.exists():
        s = json.loads(sp.read_text(encoding="utf-8"))
        loc = s.get("location") or {}
        d["farm_id"] = s.get("farm_id", d["farm_id"])
        d["location"] = loc.get("name", d["location"])
        d["lat"] = loc.get("latitude", d["lat"])
        d["lon"] = loc.get("longitude", d["lon"])
    return d, True


def load_climate_annual():
    """Returns (DataFrame with one row per year, is_sample)."""
    if (PROC / GROWING).exists():
        df = pd.read_csv(PROC / GROWING)
        for name in (ET, ANOM):
            if (PROC / name).exists():
                extra = pd.read_csv(PROC / name)
                extra = extra[["year"] + [c for c in extra.columns if c not in df.columns]]
                df = df.merge(extra, on="year", how="left")
        return df, False
    return pd.read_csv(MOCK / "climate_annual.csv"), True


def load_provenance():
    for d in (PROC, MOCK):
        if (d / "provenance.json").exists():
            return pd.DataFrame(json.loads((d / "provenance.json").read_text(encoding="utf-8")))
    return pd.DataFrame()
