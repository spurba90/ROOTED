import copy
import csv

import pytest


from src.recommendations.crop_data import (
    load_crops,
    load_crop_critical_windows,
)
from src.recommendations.climate_inputs import load_climate_scenarios
from src.recommendations.climate_timing import (
    load_monthly_precip_totals,
    calculate_monthly_percentiles,
    build_jul_aug_stress_scenario,
    build_climate_profiles,
)

from src.recommendations.crop_rules import validate_rotation, validate_cover_crop
from src.recommendations.rotation_generator import (
    create_cover_crop_practice,
    generate_rotations,
    canonical_cycle,
    unique_cycles,
    rotation_id,
)

from src.recommendations.scoring import (
    calculate_rotation_indicators,
    calculate_baseline_components,
    normalize_priority_weights,
    prepare_soil_factors,
    calculate_scenario_climate_component,
    calculate_structural_soil_proxy,
    calculate_weighted_rotation_score,
    score_rotation_for_scenario,
    rank_rotations_for_scenario,
    build_rotation_explanations,
    build_cover_crop_options,
    build_baseline_result,
    recommend_rotations,
    select_recommendation_cards,
)

def test_duplicate_crop_ids(tmp_path):
    test_file = tmp_path / "test_crops.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "crop_name",
            "crop_family",
            "crop_type",
            "planting_season",
            "harvest_season",
        ])

        writer.writerow([
            "corn", "Corn", "Poaceae", "cash", "spring", "fall"
        ])

        writer.writerow([
            "corn", "Corn", "Poaceae", "cash", "spring", "fall"
        ])


    with pytest.raises(ValueError, match="Duplicate crop IDs"):
        load_crops(test_file)



def test_missing_crop_value(tmp_path):
    test_file = tmp_path / "missing_crop_data.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "crop_name",
            "crop_family",
            "crop_type",
            "planting_season",
            "harvest_season",
        ])

        writer.writerow([
            "oats", "Oats", "", "cash", "spring", "summer"
        ])

    with pytest.raises(ValueError, match="Missing value"):
        load_crops(test_file)


@pytest.mark.parametrize(
    "column, invalid_value",
    [
        ("crop_type", "cas"),
        ("planting_season", "sprng"),
        ("harvest_season", "autumn"),
    ],
)
def test_invalid_crop_categories(tmp_path, column, invalid_value):
    crop = {
        "crop_id": "corn",
        "crop_name": "Corn",
        "crop_family": "Poaceae",
        "crop_type": "cash",
        "planting_season": "spring",
        "harvest_season": "fall",
    }

    crop[column] = invalid_value

    test_file = tmp_path / "invalid_crop.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=crop.keys())
        writer.writeheader()
        writer.writerow(crop)

    with pytest.raises(ValueError, match="Invalid"):
        load_crops(test_file)


def test_extra_csv_columns(tmp_path):
    test_file = tmp_path / "extra_columns.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "crop_name",
            "crop_family",
            "crop_type",
            "planting_season",
            "harvest_season",
        ])

        writer.writerow([
            "corn", "Corn", "Poaceae",
            "cash", "spring", "fall", "extra_value"
        ])

    with pytest.raises(ValueError, match="Extra columns"):
        load_crops(test_file)



def test_crop_whitespace(tmp_path):
    test_file = tmp_path / "whitespace_crops.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "crop_name",
            "crop_family",
            "crop_type",
            "planting_season",
            "harvest_season",
        ])

        writer.writerow([
            " corn ", " Corn ", " Poaceae ",
            " cash ", " spring ", " fall "
        ])

    crops = load_crops(test_file)

    assert crops[0]["crop_id"] == "corn"
    assert crops[0]["crop_name"] == "Corn"
    assert crops[0]["crop_type"] == "cash"
    assert crops[0]["planting_season"] == "spring"

def test_valid_rotation():
    crops = load_crops()

    assert validate_rotation(
        ("corn", "soybean", "oats"), crops
    ) is True


def test_rotation_with_wrong_length():
    crops = load_crops()

    with pytest.raises(ValueError, match="exactly three"):
        validate_rotation(("corn", "soybean"), crops)


def test_rotation_with_unknown_crop():
    crops = load_crops()

    with pytest.raises(ValueError, match="Unknown or non-cash crop"):
        validate_rotation(("corn", "soybean", "unknown"), crops)


def test_rotation_with_cover_crop():
    crops = load_crops()

    with pytest.raises(ValueError, match="Unknown or non-cash crop"):
        validate_rotation(
            ("corn", "cereal_rye", "soybean"), crops
        )


def test_valid_cover_crop():
    crops = load_crops()

    assert validate_cover_crop("cereal_rye", crops) is True


def test_cash_crop_cannot_be_cover_crop():
    crops = load_crops()

    with pytest.raises(ValueError, match="Unknown or non-cover crop"):
        validate_cover_crop("corn", crops)


def test_unknown_cover_crop():
    crops = load_crops()

    with pytest.raises(ValueError, match="Unknown or non-cover crop"):
        validate_cover_crop("unknown", crops)


def test_create_cover_crop_practice():
    crops = load_crops()

    practice = create_cover_crop_practice("cereal_rye", 1, crops)

    assert practice["cover_crop_id"] == "cereal_rye"
    assert practice["after_year"] == 1
    assert practice["before_year"] == 2
    assert practice["feasibility_status"] == "not_evaluated"


def test_cover_crop_practice_invalid_position():
    crops = load_crops()

    with pytest.raises(ValueError, match="after year 1 or 2"):
        create_cover_crop_practice("cereal_rye", 3, crops)


def test_cover_crop_practice_invalid_crop():
    crops = load_crops()

    with pytest.raises(ValueError, match="Unknown or non-cover crop"):
        create_cover_crop_practice("corn", 1, crops)



def test_generate_64_rotations():
    crops = load_crops()
    rotations = generate_rotations(crops)

    assert len(rotations) == 64


def test_generated_rotations_are_unique():
    crops = load_crops()
    rotations = generate_rotations(crops)

    assert len(rotations) == len(set(rotations))


def test_generated_rotations_exclude_cover_crops():
    crops = load_crops()
    rotations = generate_rotations(crops)

    for rotation in rotations:
        assert "cereal_rye" not in rotation


def test_generated_rotations_allow_repeated_crops():
    crops = load_crops()
    rotations = generate_rotations(crops)

    assert ("corn", "corn", "corn") in rotations


def test_all_generated_rotations_are_valid():
    crops = load_crops()
    rotations = generate_rotations(crops)

    for rotation in rotations:
        assert validate_rotation(rotation, crops) is True


def test_rotation_indicators_diverse_rotation():
    crops = load_crops()

    result = calculate_rotation_indicators(
        ("corn", "soybean", "oats"),
        crops
    )

    assert result["unique_crop_count"] == 3
    assert result["unique_family_count"] == 2
    assert result["adjacent_repeat_count"] == 0
    assert result["same_family_transition_count"] == 0
    assert result["cover_crop_present"] is False


def test_rotation_indicators_detect_repetition():
    crops = load_crops()

    result = calculate_rotation_indicators(
        ("corn", "corn", "soybean"),
        crops
    )

    assert result["unique_crop_count"] == 2
    assert result["unique_family_count"] == 2
    assert result["adjacent_repeat_count"] == 1


def test_rotation_indicators_detect_cover_crop():
    crops = load_crops()

    cover_crop_practice = {
        "cover_crop_id": "cereal_rye",
        "after_year": 1,
        "before_year": 2,
        "feasibility_status": "not_evaluated"
    }

    result = calculate_rotation_indicators(
        ("corn", "soybean", "oats"),
        crops,
        cover_crop_practice
    )

    assert result["cover_crop_present"] is True


def test_rotation_indicators_detect_same_family_transition():
    crops = load_crops()

    result = calculate_rotation_indicators(
        ("corn", "oats", "soybean"),
        crops
    )

    assert result["same_family_transition_count"] == 1

def test_baseline_components_diverse_rotation():
    indicators = {
        "unique_crop_count": 3,
        "cyclic_repeat_count": 0,
        "cyclic_same_family_count": 1,
    }

    result = calculate_baseline_components(indicators)

    assert result["crop_diversity"] == 1.0
    assert result["repeat_avoidance"] == 1.0
    assert result["family_alternation"] == pytest.approx(2 / 3)


def test_baseline_components_repeated_crop():
    indicators = {
        "unique_crop_count": 2,
        "cyclic_repeat_count": 1,
        "cyclic_same_family_count": 1,
    }

    result = calculate_baseline_components(indicators)

    assert result["crop_diversity"] == 0.5
    assert result["repeat_avoidance"] == pytest.approx(2 / 3)
    assert result["family_alternation"] == pytest.approx(2 / 3)

def test_normalize_priority_weights():
    priorities = {
        "soil_protection": 5,
        "water_suitability": 3,
        "climate_resilience": 2,
    }

    result = normalize_priority_weights(priorities)

    assert result["soil_protection"] == 0.5
    assert result["water_suitability"] == 0.3
    assert result["climate_resilience"] == 0.2
    assert sum(result.values()) == pytest.approx(1.0)


def test_normalize_equal_priority_weights():
    priorities = {
        "soil_protection": 1,
        "water_suitability": 1,
        "climate_resilience": 1,
    }

    result = normalize_priority_weights(priorities)

    assert result["soil_protection"] == pytest.approx(1 / 3)
    assert result["water_suitability"] == pytest.approx(1 / 3)
    assert result["climate_resilience"] == pytest.approx(1 / 3)


def test_priority_weights_reject_negative_values():
    priorities = {
        "soil_protection": 1,
        "water_suitability": -1,
    }

    with pytest.raises(ValueError, match="cannot be negative"):
        normalize_priority_weights(priorities)


def test_priority_weights_reject_all_zero():
    priorities = {
        "soil_protection": 0,
        "water_suitability": 0,
        "climate_resilience": 0,
    }

    with pytest.raises(ValueError, match="greater than zero"):
        normalize_priority_weights(priorities)


def test_prepare_soil_factors_all_missing():
    farm = {
        "soil": {
            "texture": None,
            "ph": None,
            "organic_matter_pct": None,
            "drainage_class": None,
            "available_water_capacity": None,
        }
    }

    result = prepare_soil_factors(farm)

    assert result["soil_data_available"] is False
    assert result["available_fields"] == []
    assert len(result["missing_fields"]) == 5


def test_prepare_soil_factors_partial_data():
    farm = {
        "soil": {
            "texture": "loam",
            "ph": None,
            "organic_matter_pct": None,
            "drainage_class": None,
            "available_water_capacity": None,
        }
    }

    result = prepare_soil_factors(farm)

    assert result["soil_data_available"] is True
    assert result["values"]["texture"] == "loam"
    assert "texture" in result["available_fields"]
    assert "ph" in result["missing_fields"]


def test_prepare_soil_factors_without_soil_section():
    farm = {}

    result = prepare_soil_factors(farm)

    assert result["soil_data_available"] is False
    assert len(result["missing_fields"]) == 5



def test_structural_soil_proxy_high_diversity():
    components = {
        "crop_diversity": 1.0,
        "repeat_avoidance": 1.0,
        "family_alternation": 1.0,
    }

    result = calculate_structural_soil_proxy(components)

    assert result == 1.0


def test_structural_soil_proxy_mixed_rotation():
    components = {
        "crop_diversity": 0.5,
        "repeat_avoidance": 2 / 3,
        "family_alternation": 2 / 3,
    }

    result = calculate_structural_soil_proxy(components)

    assert result == pytest.approx(
        (0.5 + (2 / 3) + (2 / 3)) / 3
    )


def test_structural_soil_proxy_requires_components():
    components = {
        "crop_diversity": 1.0,
    }

    with pytest.raises(
        ValueError,
        match="Missing baseline components",
    ):
        calculate_structural_soil_proxy(components)

def test_weighted_rotation_score_dry_scenario():
    priorities = {
        "soil_protection": 5,
        "water_suitability": 3,
        "climate_resilience": 2,
    }

    climate_component = {
        "value": 0.5,
        "status": "available",
        "basis": "relative_drought_resilience",
    }

    result = calculate_weighted_rotation_score(
        0.8,
        climate_component,
        priorities,
    )

    assert result["effective_weights"]["soil_protection"] == pytest.approx(
        5 / 7
    )
    assert result["effective_weights"]["climate_resilience"] == pytest.approx(
        2 / 7
    )

    assert result["score"] == pytest.approx(
        (0.8 * (5 / 7)) + (0.5 * (2 / 7))
    )

    assert "water_suitability" in result["unavailable_components"]


def test_weighted_rotation_score_typical_scenario():
    priorities = {
        "soil_protection": 5,
        "water_suitability": 3,
        "climate_resilience": 2,
    }

    climate_component = {
        "value": None,
        "status": "not_scored",
        "basis": None,
    }

    result = calculate_weighted_rotation_score(
        0.8,
        climate_component,
        priorities,
    )

    assert result["score"] == 0.8
    assert result["effective_weights"] == {
        "soil_protection": 1.0
    }

    assert "water_suitability" in result["unavailable_components"]
    assert "climate_resilience" in result["unavailable_components"]


def test_weighted_rotation_score_requires_available_component():
    priorities = {
        "soil_protection": 0,
        "water_suitability": 1,
        "climate_resilience": 1,
    }

    climate_component = {
        "value": None,
        "status": "not_scored",
        "basis": None,
    }

    with pytest.raises(
        ValueError,
        match="No weighted scoring components are available",
    ):
        calculate_weighted_rotation_score(
            0.8,
            climate_component,
            priorities,
        )


def test_recommend_rotations_returns_all_scenarios():
    farm = {}

    scenarios = load_climate_scenarios()

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    result = recommend_rotations(
        farm,
        scenarios,
        priorities,
    )

    assert set(result["scenario_results"]) == {
        "dry",
        "typical",
        "wet",
        "jul_aug_dry",
    }

    assert len(result["scenario_results"]["dry"]) == 64
    assert len(result["scenario_results"]["typical"]) == 64
    assert len(result["scenario_results"]["wet"]) == 64

    assert result["soil_factors"]["soil_data_available"] is False



def test_recommend_rotations_returns_top_three():
    farm = {}

    scenarios = load_climate_scenarios()

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    result = recommend_rotations(
        farm,
        scenarios,
        priorities,
    )

    assert set(result["recommendations"]) == {
        "dry",
        "typical",
        "wet",
        "jul_aug_dry",
    }

    for scenario_id, cards in result["recommendations"].items():
        assert len(cards) == 3

        scores = [card["score"] for card in cards]
        assert scores == sorted(scores, reverse=True)

        assert all(card["scenario_id"] == scenario_id for card in cards)




def test_recommendations_include_explanations():
    farm = {}

    scenarios = load_climate_scenarios()

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    result = recommend_rotations(
        farm,
        scenarios,
        priorities,
    )

    for cards in result["recommendations"].values():
        for card in cards:
            assert card["why"]

def test_build_cover_crop_options_both_slots_when_no_fall_crop():
    crops = load_crops()

    options = build_cover_crop_options(("oats", "soybean", "oats"), crops)

    assert [option["after_year"] for option in options] == [1, 2]
    assert all(option["cover_crop_id"] == "cereal_rye" for option in options)
    assert all(
        option["feasibility_status"] == "not_evaluated"
        for option in options
    )

def test_recommendations_include_cover_crop_options():
    result = recommend_rotations(
        {},
        load_climate_scenarios(),
        {
            "soil_protection": 1,
            "water_suitability": 0,
            "climate_resilience": 1,
        },
    )

    for cards in result["recommendations"].values():
        for card in cards:
            for option in card["cover_crop_options"]:
                next_crop = card["rotation"][option["after_year"]]
                assert next_crop != "winter_wheat"

def test_recommend_rotations_includes_baseline():
    result = recommend_rotations(
        {
            "current_rotation": (
                "corn",
                "soybean",
                "corn",
            )
        },
        load_climate_scenarios(),
        {
            "soil_protection": 1,
            "water_suitability": 0,
            "climate_resilience": 1,
        },
    )

    assert result["baseline"] is not None
    assert result["baseline"]["rotation"] == (
        "corn",
        "soybean",
        "corn",
    )




REAL_PRIORITIES = {
    "soil_protection": 1,
    "water_suitability": 0,
    "climate_resilience": 1,
}


@pytest.fixture(scope="module")
def real_profiles():
    """Climate profiles built from the real Ames files (no synthetic data)."""
    totals = load_monthly_precip_totals()
    scenarios = load_climate_scenarios()
    scenarios["jul_aug_dry"] = build_jul_aug_stress_scenario(totals)

    return build_climate_profiles(
        scenarios,
        calculate_monthly_percentiles(totals),
    )


def test_recommend_rotations_rejects_invalid_scenarios():
    bad = copy.deepcopy(load_climate_scenarios())
    bad["wet"]["total_precip_mm"] = bad["dry"]["total_precip_mm"] - 1

    with pytest.raises(ValueError):
        recommend_rotations({}, bad, REAL_PRIORITIES)


def test_recommend_rotations_includes_scenario_context():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    context = result["scenario_context"]

    assert context["dry"]["representative_year"] == 2022
    assert context["typical"]["representative_year"] == 2009
    assert context["wet"]["representative_year"] == 2025
    assert context["jul_aug_dry"]["representative_year"] == 2013


def test_recommend_rotations_reports_dry_months():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    context = result["scenario_context"]

    assert context["dry"]["dry_months"] == []
    assert context["typical"]["dry_months"] == []
    assert context["wet"]["dry_months"] == [5, 9]
    assert context["jul_aug_dry"]["dry_months"] == [7, 8]


def test_scored_results_include_score_basis():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    top = result["scenario_results"]["dry"][0]

    assert top["score_basis"] == ["climate_resilience", "soil_protection"]
    assert top["comparable_across_scenarios"] is False


def test_cyclic_indicators_count_year_three_to_year_one():
    crops = load_crops()

    result = calculate_rotation_indicators(
        ("winter_wheat", "oats", "winter_wheat"),
        crops,
    )

    assert result["adjacent_repeat_count"] == 0
    assert result["cyclic_repeat_count"] == 1
    assert result["cyclic_same_family_count"] == 3


def test_all_grass_rotation_scores_below_grass_legume_rotation():
    crops = load_crops()

    def proxy(rotation):
        indicators = calculate_rotation_indicators(rotation, crops)
        return calculate_structural_soil_proxy(
            calculate_baseline_components(indicators)
        )

    assert proxy(("winter_wheat", "oats", "winter_wheat")) < proxy(
        ("oats", "soybean", "winter_wheat")
    )


def test_canonical_cycle_treats_shifted_sequences_as_same():
    assert canonical_cycle(("corn", "soybean", "oats")) == canonical_cycle(
        ("soybean", "oats", "corn")
    )
    assert canonical_cycle(("corn", "soybean", "oats")) != canonical_cycle(
        ("corn", "oats", "soybean")
    )


def test_unique_cycles_returns_24():
    crops = load_crops()

    assert len(unique_cycles(generate_rotations(crops))) == 24


def test_cards_skip_repeats_and_duplicate_cycles():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    for cards in result["recommendations"].values():
        cycles = [canonical_cycle(card["rotation"]) for card in cards]

        assert len(cycles) == len(set(cycles))

        for card in cards:
            rotation = card["rotation"]
            assert all(
                rotation[i] != rotation[(i + 1) % 3]
                for i in range(3)
            )


def test_climate_component_2022_has_no_exposed_crops(real_profiles):
    windows = load_crop_critical_windows()

    result = calculate_scenario_climate_component(
        ("corn", "soybean", "oats"),
        windows,
        real_profiles["dry"],
    )

    assert result["value"] == 1.0
    assert result["exposed_crops"] == []
    assert result["basis"] == "critical_window_dry_exposure"


def test_climate_component_2013_exposes_corn_and_soybean(real_profiles):
    windows = load_crop_critical_windows()

    result = calculate_scenario_climate_component(
        ("corn", "soybean", "oats"),
        windows,
        real_profiles["jul_aug_dry"],
    )

    assert result["value"] == pytest.approx(1 / 3)
    assert result["exposed_crops"] == ["corn", "soybean"]


def test_climate_component_does_not_penalize_wettest_july(real_profiles):
    windows = load_crop_critical_windows()
    wet_2025 = real_profiles["wet"]

    assert wet_2025["month_percentiles"][7] == pytest.approx(1.0)

    result = calculate_scenario_climate_component(
        ("corn", "corn", "corn"),
        windows,
        wet_2025,
    )

    assert result["value"] == 1.0


def test_climate_component_rejects_unknown_crop(real_profiles):
    windows = load_crop_critical_windows()

    with pytest.raises(ValueError, match="Missing critical window"):
        calculate_scenario_climate_component(
            ("corn", "soybean", "unknown"),
            windows,
            real_profiles["dry"],
        )


def test_2013_prefers_small_grains_over_row_crops(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()
    priorities = {
        "soil_protection": 0,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    row_crops = score_rotation_for_scenario(
        ("corn", "soybean", "corn"), crops, windows, priorities,
        real_profiles["jul_aug_dry"],
    )
    small_grains = score_rotation_for_scenario(
        ("oats", "winter_wheat", "oats"), crops, windows, priorities,
        real_profiles["jul_aug_dry"],
    )

    assert small_grains["score"] > row_crops["score"]


def test_rank_all_rotations_for_2013(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    results = rank_rotations_for_scenario(
        generate_rotations(crops),
        crops,
        windows,
        REAL_PRIORITIES,
        real_profiles["jul_aug_dry"],
    )

    assert len(results) == 64

    scores = [result["score"] for result in results]
    assert scores == sorted(scores, reverse=True)


def test_ranking_reports_dense_rank_and_ties(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    results = rank_rotations_for_scenario(
        generate_rotations(crops),
        crops,
        windows,
        REAL_PRIORITIES,
        real_profiles["typical"],
    )

    top = results[0]
    same_score = [r for r in results if r["score"] == top["score"]]

    assert top["rank"] == 1
    assert all(r["rank"] == 1 for r in same_score)
    assert top["tied_with"] == len({r["cycle_id"] for r in same_score}) - 1


def test_rotation_explanations_name_exposed_crops(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    result = score_rotation_for_scenario(
        ("corn", "soybean", "oats"),
        crops,
        windows,
        REAL_PRIORITIES,
        real_profiles["jul_aug_dry"],
    )

    explanations = build_rotation_explanations(result)

    assert "Uses three different cash crops across the three-year rotation." in explanations
    assert any("In 2013" in text and "corn" in text for text in explanations)


def test_baseline_none_without_current_rotation(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    result = build_baseline_result(
        {}, crops, windows, REAL_PRIORITIES, real_profiles,
    )

    assert result is None


def test_baseline_scores_every_scenario(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    result = build_baseline_result(
        {"current_rotation": ("corn", "soybean", "corn")},
        crops, windows, REAL_PRIORITIES, real_profiles,
    )

    scores = result["scenario_scores"]

    assert set(scores) == {"dry", "typical", "wet", "jul_aug_dry"}
    assert scores["jul_aug_dry"]["score"] < scores["dry"]["score"]





def test_2013_cards_lead_with_rotations_without_corn():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    top_card = result["recommendations"]["jul_aug_dry"][0]

    assert top_card["representative_year"] == 2013
    assert "corn" not in top_card["rotation"]




def test_priority_weights_reject_unknown_name():
    priorities = {
        "soil_protecton": 5,  # misspelled on purpose
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    with pytest.raises(ValueError, match="Unknown priority name"):
        normalize_priority_weights(priorities)


def test_priority_weights_reject_missing_name():
    priorities = {
        "soil_protection": 1,
        "climate_resilience": 1,
    }

    with pytest.raises(ValueError, match="Missing priority value"):
        normalize_priority_weights(priorities)


def test_weighted_score_reports_dropped_priority_share():
    priorities = {
        "soil_protection": 5,
        "water_suitability": 3,
        "climate_resilience": 2,
    }

    climate_component = {
        "value": 0.5,
        "status": "available",
        "basis": "critical_window_dry_exposure",
    }

    result = calculate_weighted_rotation_score(0.8, climate_component, priorities)

    assert result["dropped_priority_share"] == pytest.approx(0.3)


def test_water_only_priorities_explain_what_to_change():
    priorities = {
        "soil_protection": 0,
        "water_suitability": 1,
        "climate_resilience": 0,
    }

    climate_component = {
        "value": 0.5,
        "status": "available",
        "basis": "critical_window_dry_exposure",
    }

    with pytest.raises(ValueError, match="water suitability is not scored"):
        calculate_weighted_rotation_score(0.8, climate_component, priorities)





def test_cover_crop_skipped_before_winter_wheat():
    crops = load_crops()

    options = build_cover_crop_options(("oats", "winter_wheat", "soybean"), crops)

    assert [option["after_year"] for option in options] == [2]


def test_cover_crop_before_corn_carries_caution():
    crops = load_crops()

    options = build_cover_crop_options(("soybean", "corn", "oats"), crops)

    before_corn = [option for option in options if option["after_year"] == 1]

    assert "caution" in before_corn[0]
    assert "10 days" in before_corn[0]["caution"]



def test_explanations_count_repeat_when_rotation_restarts(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()

    result = score_rotation_for_scenario(
        ("winter_wheat", "oats", "winter_wheat"),
        crops, windows, REAL_PRIORITIES, real_profiles["dry"],
    )

    explanations = build_rotation_explanations(result)

    assert any("1 time(s) per cycle" in text for text in explanations)
    assert any("includes no legume" in text for text in explanations)


def test_explanations_report_ties_on_cards():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    for cards in result["recommendations"].values():
        for card in cards:
            if card["tied_with"]:
                assert any("Tied with" in text for text in card["why"])


def test_explanations_report_dropped_water_weight(real_profiles):
    crops = load_crops()
    windows = load_crop_critical_windows()
    priorities = {
        "soil_protection": 5,
        "water_suitability": 3,
        "climate_resilience": 2,
    }

    result = score_rotation_for_scenario(
        ("corn", "soybean", "oats"),
        crops, windows, priorities, real_profiles["dry"],
    )

    explanations = build_rotation_explanations(result)

    assert any("30% of the farmer's priority weight" in text for text in explanations)


def test_explanations_make_no_outcome_claims():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    banned = ["soil health", "improve", "optimal", "yield", "will survive", "guarantee"]

    for cards in result["recommendations"].values():
        for card in cards:
            for text in card["why"]:
                for phrase in banned:
                    assert phrase not in text.lower()





def test_soil_status_none_partial_complete():
    none = prepare_soil_factors({})
    partial = prepare_soil_factors({"soil": {"texture": "loam"}})
    complete = prepare_soil_factors({"soil": {
        "texture": "loam",
        "ph": 6.5,
        "organic_matter_pct": 3.0,
        "drainage_class": "well drained",
        "available_water_capacity": 0.2,
    }})

    assert none["soil_data_status"] == "none"
    assert partial["soil_data_status"] == "partial"
    assert complete["soil_data_status"] == "complete"
    assert none["used_in_score"] is False


def test_real_soil_profile_contains_retrieved_usda_values():
    import json

    with open("data/processed/ames_soil_profile.json") as file:
        profile = json.load(file)

    result = prepare_soil_factors(profile)

    assert result["soil_data_status"] == "complete"
    assert result["soil_data_available"] is True
    assert result["used_in_score"] is False

    assert result["values"]["texture"] == "Loam"
    assert result["values"]["ph"] == 6.2
    assert result["values"]["organic_matter_pct"] == 3.5
    assert result["values"]["drainage_class"] == "Well drained"
    assert result["values"]["available_water_capacity"] == 0.21

    assert result["missing_fields"] == []




def test_cards_do_not_start_with_prior_crop():
    result = recommend_rotations(
        {"prior_crop": "oats"},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )

    assert result["prior_crop"] == "oats"

    for cards in result["recommendations"].values():
        assert len(cards) == 3

        for card in cards:
            assert card["rotation"][0] != "oats"
            assert any("prior crop (oats)" in text for text in card["why"])


def test_prior_crop_keeps_same_cycles_in_2013():
    without_prior = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    with_prior = recommend_rotations(
        {"prior_crop": "oats"},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )

    def top_two_cycles(result):
        cards = result["recommendations"]["jul_aug_dry"][:2]
        return {canonical_cycle(card["rotation"]) for card in cards}

    assert top_two_cycles(with_prior) == top_two_cycles(without_prior)


def test_unknown_prior_crop_rejected():
    with pytest.raises(ValueError, match="prior crop"):
        recommend_rotations(
            {"prior_crop": "cereal_rye"},
            load_climate_scenarios(),
            REAL_PRIORITIES,
        )


def test_no_prior_crop_means_no_prior_crop_note():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    assert result["prior_crop"] is None

    for cards in result["recommendations"].values():
        for card in cards:
            assert card["follows_prior_crop"] is None




def test_rotation_id_is_readable_string():
    assert rotation_id(("oats", "soybean", "winter_wheat")) == (
        "oats-soybean-winter_wheat"
    )


def test_cards_carry_rotation_ids_and_crops_by_year():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    for cards in result["recommendations"].values():
        for card in cards:
            assert card["rotation_id"] == "-".join(card["rotation"])
            assert card["cycle_key"] == "-".join(canonical_cycle(card["rotation"]))
            assert [entry["crop_id"] for entry in card["crops_by_year"]] == list(
                card["rotation"]
            )
            assert [entry["year"] for entry in card["crops_by_year"]] == [1, 2, 3]


def test_rotation_ids_unique_within_each_scenario():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    for ranked in result["scenario_results"].values():
        ids = [item["rotation_id"] for item in ranked]
        assert len(ids) == 64
        assert len(set(ids)) == 64


def test_baseline_has_rotation_id():
    result = recommend_rotations(
        {"current_rotation": ("corn", "soybean", "corn")},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )

    assert result["baseline"]["rotation_id"] == "corn-soybean-corn"





def test_climate_replay_has_one_row_per_cycle_with_all_scenarios():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    replay = result["climate_replay"]

    assert len(replay) == 24

    for row in replay:
        assert set(row["ranks"]) == {"dry", "typical", "wet", "jul_aug_dry"}
        assert row["rank_spread"] == row["worst_rank"] - row["best_rank"]


def test_climate_replay_shows_2013_ranking_change():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    replay = {row["cycle_key"]: row for row in result["climate_replay"]}

    corn_row = replay["corn-oats-soybean"]
    small_grain_row = replay["oats-soybean-winter_wheat"]

    assert corn_row["ranks"]["typical"] == 1
    assert corn_row["ranks"]["jul_aug_dry"] > 1
    assert corn_row["exposed_crops"]["jul_aug_dry"] == ["corn", "soybean"]

    assert small_grain_row["ranks"]["jul_aug_dry"] == 1
    assert small_grain_row["exposed_crops"]["jul_aug_dry"] == ["soybean"]


def test_climate_replay_marks_current_rotation():
    result = recommend_rotations(
        {"current_rotation": ("corn", "soybean", "corn")},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )

    current = [row for row in result["climate_replay"] if row["is_current_rotation"]]

    assert len(current) == 1
    assert current[0]["cycle_key"] == "corn-corn-soybean"
    assert current[0]["repeats_crop"] is True



def test_regret_is_zero_for_rotations_best_in_every_scenario():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    replay = {row["cycle_key"]: row for row in result["climate_replay"]}

    robust = replay["oats-soybean-winter_wheat"]

    assert all(value == 0 for value in robust["regret"].values())
    assert robust["max_regret"] == 0


def test_regret_peaks_in_2013_for_corn_soybean_rotations():
    result = recommend_rotations(
        {"current_rotation": ("corn", "soybean", "corn")},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )
    replay = {row["cycle_key"]: row for row in result["climate_replay"]}

    corn_row = replay["corn-oats-soybean"]
    baseline_row = replay["corn-corn-soybean"]

    assert corn_row["max_regret_scenario"] == "jul_aug_dry"
    assert corn_row["max_regret"] > 0
    assert baseline_row["max_regret"] > corn_row["max_regret"]


def test_regret_never_negative():
    result = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)

    for row in result["climate_replay"]:
        assert all(value >= 0 for value in row["regret"].values())



def test_irrigation_reported_but_not_scored():
    without = recommend_rotations({}, load_climate_scenarios(), REAL_PRIORITIES)
    irrigated = recommend_rotations(
        {"irrigation_available": True},
        load_climate_scenarios(),
        REAL_PRIORITIES,
    )

    assert without["irrigation"]["irrigation_available"] is None
    assert irrigated["irrigation"]["irrigation_available"] is True
    assert irrigated["irrigation"]["used_in_score"] is False
    assert "rainfall only" in irrigated["irrigation"]["note"]

    for scenario_id in without["recommendations"]:
        before = [card["score"] for card in without["recommendations"][scenario_id]]
        after = [card["score"] for card in irrigated["recommendations"][scenario_id]]
        assert before == after


def test_irrigation_must_be_true_false_or_missing():
    with pytest.raises(TypeError, match="irrigation_available"):
        recommend_rotations(
            {"irrigation_available": "yes"},
            load_climate_scenarios(),
            REAL_PRIORITIES,
        )