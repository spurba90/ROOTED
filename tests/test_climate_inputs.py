import csv

import pytest

from src.recommendations.climate_inputs import (
    load_climate_scenarios,
    validate_climate_scenarios,
)


def write_test_scenarios(path):
    fieldnames = [
        "scenario_id",
        "representative_year",
        "season_start_month",
        "season_end_month",
        "avg_temp_c",
        "total_precip_mm",
        "temp_anomaly_c",
        "precip_anomaly_mm",
        "precip_anomaly_pct",
        "avg_daily_et_mj_m2_day",
        "total_et_energy_mj_m2",
    ]

    rows = [
        {
            "scenario_id": "dry",
            "representative_year": 2001,
            "season_start_month": 5,
            "season_end_month": 9,
            "avg_temp_c": 20.0,
            "total_precip_mm": 300.0,
            "temp_anomaly_c": 0.0,
            "precip_anomaly_mm": -100.0,
            "precip_anomaly_pct": -20.0,
            "avg_daily_et_mj_m2_day": 3.0,
            "total_et_energy_mj_m2": 450.0,
        },
        {
            "scenario_id": "typical",
            "representative_year": 2002,
            "season_start_month": 5,
            "season_end_month": 9,
            "avg_temp_c": 20.0,
            "total_precip_mm": 500.0,
            "temp_anomaly_c": 0.0,
            "precip_anomaly_mm": 0.0,
            "precip_anomaly_pct": 0.0,
            "avg_daily_et_mj_m2_day": 4.0,
            "total_et_energy_mj_m2": 600.0,
        },
        {
            "scenario_id": "wet",
            "representative_year": 2003,
            "season_start_month": 5,
            "season_end_month": 9,
            "avg_temp_c": 20.0,
            "total_precip_mm": 700.0,
            "temp_anomaly_c": 0.0,
            "precip_anomaly_mm": 100.0,
            "precip_anomaly_pct": 20.0,
            "avg_daily_et_mj_m2_day": 5.0,
            "total_et_energy_mj_m2": 750.0,
        },
    ]

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_load_and_validate_climate_scenarios(tmp_path):
    test_file = tmp_path / "scenarios.csv"
    write_test_scenarios(test_file)

    scenarios = load_climate_scenarios(test_file)

    assert set(scenarios) == {"dry", "typical", "wet"}
    assert scenarios["dry"]["representative_year"] == 2001
    assert scenarios["wet"]["total_precip_mm"] == 700.0

    assert validate_climate_scenarios(scenarios) is True


def test_climate_scenarios_require_all_three(tmp_path):
    test_file = tmp_path / "scenarios.csv"
    write_test_scenarios(test_file)

    scenarios = load_climate_scenarios(test_file)
    del scenarios["wet"]

    with pytest.raises(
        ValueError,
        match="dry, typical, and wet",
    ):
        validate_climate_scenarios(scenarios)


def test_climate_scenarios_reject_wrong_precip_order(tmp_path):
    test_file = tmp_path / "scenarios.csv"
    write_test_scenarios(test_file)

    scenarios = load_climate_scenarios(test_file)
    scenarios["dry"]["total_precip_mm"] = 800.0

    with pytest.raises(
        ValueError,
        match="dry to typical to wet",
    ):
        validate_climate_scenarios(scenarios)