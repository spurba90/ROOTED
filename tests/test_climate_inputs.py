import copy

import pytest

from src.recommendations.climate_inputs import (
    load_climate_scenarios,
    validate_climate_scenarios,
)

# These tests use the climate team's real scenario file:
#   data/processed/ames_climate_scenarios.csv
# Error-handling tests change an in-memory copy; the file is never changed.


def test_load_and_validate_real_climate_scenarios():
    scenarios = load_climate_scenarios()

    assert set(scenarios) == {"dry", "typical", "wet"}
    assert scenarios["dry"]["representative_year"] == 2022
    assert scenarios["typical"]["representative_year"] == 2009
    assert scenarios["wet"]["representative_year"] == 2025
    assert scenarios["wet"]["total_precip_mm"] == pytest.approx(621.77)

    assert validate_climate_scenarios(scenarios) is True


def test_climate_scenarios_require_all_three():
    scenarios = copy.deepcopy(load_climate_scenarios())
    del scenarios["wet"]

    with pytest.raises(ValueError, match="dry, typical, and wet"):
        validate_climate_scenarios(scenarios)


def test_climate_scenarios_reject_wrong_precip_order():
    scenarios = copy.deepcopy(load_climate_scenarios())
    scenarios["dry"]["total_precip_mm"] = scenarios["wet"]["total_precip_mm"] + 1

    with pytest.raises(ValueError, match="dry to typical to wet"):
        validate_climate_scenarios(scenarios)