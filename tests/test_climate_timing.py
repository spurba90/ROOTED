import csv
import shutil

import pytest

from src.recommendations.crop_data import load_crop_critical_windows
from src.recommendations.climate_inputs import load_climate_scenarios
from src.recommendations.climate_timing import (
    load_monthly_precip_totals,
    calculate_monthly_percentiles,
    build_jul_aug_stress_scenario,
    build_climate_profiles,
)

# These tests use the real project files:
#   data/raw/nasa_power_ames_iowa_2005_2025.csv   (NASA POWER daily, Ames)
#   data/processed/ames_climate_scenarios.csv     (climate team scenarios)
#   data/crop_critical_windows.csv
# Error-handling tests break a temporary copy of a real file; the
# originals are never changed.

RAW_DAILY_FILE = "data/raw/nasa_power_ames_iowa_2005_2025.csv"
CRITICAL_WINDOWS_FILE = "data/crop_critical_windows.csv"


def test_monthly_totals_cover_21_years_of_may_to_september():
    totals = load_monthly_precip_totals()

    assert len(totals) == 21 * 5
    assert {year for year, _ in totals} == set(range(2005, 2026))
    assert (2013, 1) not in totals  # outside May-September


def test_monthly_totals_match_known_2013_values():
    totals = load_monthly_precip_totals()

    assert totals[(2013, 7)] == pytest.approx(30.6, abs=0.01)
    assert totals[(2013, 8)] == pytest.approx(20.26, abs=0.01)


def test_monthly_totals_reject_missing_value(tmp_path):
    broken_copy = tmp_path / "daily.csv"

    with open(RAW_DAILY_FILE, newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))

    for row in rows:
        if row["date"] == "20130715":
            row["PRECTOTCORR"] = "-999"

    with broken_copy.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="Missing precipitation value"):
        load_monthly_precip_totals(broken_copy)


def test_monthly_percentiles_rank_within_month():
    percentiles = calculate_monthly_percentiles(load_monthly_precip_totals())

    assert percentiles[2013][7] == pytest.approx(1 / 21)  # driest July
    assert percentiles[2025][7] == pytest.approx(1.0)     # wettest July


def test_stress_scenario_is_driest_jul_aug_on_record():
    stress = build_jul_aug_stress_scenario(load_monthly_precip_totals())

    assert stress["representative_year"] == 2013
    assert stress["jul_aug_precip_mm"] == pytest.approx(50.86, abs=0.01)


def test_climate_profiles_for_real_scenarios():
    totals = load_monthly_precip_totals()
    scenarios = load_climate_scenarios()
    scenarios["jul_aug_dry"] = build_jul_aug_stress_scenario(totals)

    profiles = build_climate_profiles(
        scenarios,
        calculate_monthly_percentiles(totals),
    )

    assert profiles["dry"]["dry_months"] == []
    assert profiles["typical"]["dry_months"] == []
    assert profiles["wet"]["dry_months"] == [5, 9]
    assert profiles["jul_aug_dry"]["dry_months"] == [7, 8]


def test_climate_profiles_reject_missing_year():
    percentiles = calculate_monthly_percentiles(load_monthly_precip_totals())
    del percentiles[2022]

    with pytest.raises(ValueError, match="No monthly precipitation data"):
        build_climate_profiles(load_climate_scenarios(), percentiles)


def test_load_crop_critical_windows():
    windows = load_crop_critical_windows()

    assert set(windows) == {"corn", "soybean", "oats", "winter_wheat"}
    assert windows["corn"]["critical_month"] == 7
    assert windows["soybean"]["critical_month"] == 8


def test_critical_windows_reject_duplicate_crop(tmp_path):
    broken_copy = tmp_path / "windows.csv"

    with open(CRITICAL_WINDOWS_FILE, newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))

    rows.append(dict(rows[0]))  # repeat the corn row

    with broken_copy.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="Duplicate critical-window"):
        load_crop_critical_windows(broken_copy)


def test_critical_windows_reject_missing_month(tmp_path):
    broken_copy = tmp_path / "windows.csv"

    with open(CRITICAL_WINDOWS_FILE, newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))

    rows[0]["critical_month"] = ""

    with broken_copy.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="Missing critical month"):
        load_crop_critical_windows(broken_copy)