import csv

import pytest


from src.recommendations.crop_data import (
    load_crops,
    load_crop_climate_traits,
)
from src.recommendations.crop_rules import validate_rotation, validate_cover_crop
from src.recommendations.rotation_generator import (
    create_cover_crop_practice,
    generate_rotations,
)


from src.recommendations.scoring import (
    calculate_rotation_indicators,
    calculate_baseline_components,
    normalize_priority_weights,
    prepare_soil_factors,
    calculate_scenario_climate_component,
    calculate_structural_soil_proxy,
    calculate_weighted_rotation_score,
    calculate_dry_resilience_index,
    score_rotation_for_scenario,
    rank_rotations_for_scenario,
    build_rotation_explanations,
    build_cover_crop_options,
    build_baseline_result,
    recommend_rotations,
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
        "adjacent_repeat_count": 0,
    }

    result = calculate_baseline_components(indicators)

    assert result["crop_diversity"] == 1.0
    assert result["repeat_avoidance"] == 1.0


def test_baseline_components_repeated_crop():
    indicators = {
        "unique_crop_count": 2,
        "adjacent_repeat_count": 1,
    }

    result = calculate_baseline_components(indicators)

    assert result["crop_diversity"] == pytest.approx(2 / 3)
    assert result["repeat_avoidance"] == 0.5

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


def test_load_crop_climate_traits():
    traits = load_crop_climate_traits()

    assert set(traits) == {
        "corn",
        "soybean",
        "oats",
        "winter_wheat",
    }

    assert traits["corn"]["dry_resilience_rank"] == 1
    assert traits["winter_wheat"]["dry_resilience_rank"] == 4


def test_crop_climate_traits_reject_duplicate_crop(tmp_path):
    test_file = tmp_path / "climate_traits.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "dry_resilience_rank",
        ])

        writer.writerow(["corn", 1])
        writer.writerow(["corn", 2])

    with pytest.raises(
        ValueError,
        match="Duplicate climate trait crop ID",
    ):
        load_crop_climate_traits(test_file)


def test_crop_climate_traits_reject_missing_rank(tmp_path):
    test_file = tmp_path / "climate_traits.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "crop_id",
            "dry_resilience_rank",
        ])

        writer.writerow(["corn", ""])

    with pytest.raises(
        ValueError,
        match="Missing dry resilience rank",
    ):
        load_crop_climate_traits(test_file)

def test_dry_resilience_index():
    traits = load_crop_climate_traits()

    result = calculate_dry_resilience_index(
        ("corn", "soybean", "oats"),
        traits,
    )

    assert result == pytest.approx(1 / 3)


def test_dry_resilience_index_high_resilience_rotation():
    traits = load_crop_climate_traits()

    result = calculate_dry_resilience_index(
        ("winter_wheat", "winter_wheat", "winter_wheat"),
        traits,
    )

    assert result == 1.0


def test_dry_resilience_index_missing_trait():
    traits = load_crop_climate_traits()

    with pytest.raises(
        ValueError,
        match="Missing climate traits",
    ):
        calculate_dry_resilience_index(
            ("corn", "soybean", "unknown"),
            traits,
        )


def test_dry_scenario_uses_drought_resilience():
    traits = load_crop_climate_traits()

    result = calculate_scenario_climate_component(
        ("corn", "soybean", "oats"),
        traits,
        "dry",
    )

    assert result["status"] == "available"
    assert result["basis"] == "relative_drought_resilience"
    assert result["value"] == pytest.approx(1 / 3)


def test_typical_scenario_has_no_climate_adjustment():
    traits = load_crop_climate_traits()

    result = calculate_scenario_climate_component(
        ("corn", "soybean", "oats"),
        traits,
        "typical",
    )

    assert result["value"] is None
    assert result["status"] == "not_scored"


def test_wet_scenario_has_no_unverified_penalty():
    traits = load_crop_climate_traits()

    result = calculate_scenario_climate_component(
        ("corn", "soybean", "oats"),
        traits,
        "wet",
    )

    assert result["value"] is None
    assert result["status"] == "not_scored"


def test_unknown_climate_scenario_rejected():
    traits = load_crop_climate_traits()

    with pytest.raises(
        ValueError,
        match="Unknown climate scenario",
    ):
        calculate_scenario_climate_component(
            ("corn", "soybean", "oats"),
            traits,
            "extreme",
        )

def test_structural_soil_proxy_high_diversity():
    components = {
        "crop_diversity": 1.0,
        "repeat_avoidance": 1.0,
    }

    result = calculate_structural_soil_proxy(components)

    assert result == 1.0


def test_structural_soil_proxy_mixed_rotation():
    components = {
        "crop_diversity": 2 / 3,
        "repeat_avoidance": 0.5,
    }

    result = calculate_structural_soil_proxy(components)

    assert result == pytest.approx(
        ((2 / 3) + 0.5) / 2
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

def test_score_rotation_for_dry_scenario():
    crops = load_crops()
    traits = load_crop_climate_traits()

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    result = score_rotation_for_scenario(
        ("corn", "soybean", "oats"),
        crops,
        traits,
        priorities,
        "dry",
    )

    assert result["scenario_id"] == "dry"
    assert 0 <= result["score"] <= 1
    assert result["climate_component"]["status"] == "available"


def test_dry_scenario_prefers_more_drought_resilient_rotation():
    crops = load_crops()
    traits = load_crop_climate_traits()

    priorities = {
        "soil_protection": 0,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    lower_resilience = score_rotation_for_scenario(
        ("corn", "corn", "corn"),
        crops,
        traits,
        priorities,
        "dry",
    )

    higher_resilience = score_rotation_for_scenario(
        ("winter_wheat", "winter_wheat", "winter_wheat"),
        crops,
        traits,
        priorities,
        "dry",
    )

    assert higher_resilience["score"] > lower_resilience["score"]


def test_rank_all_rotations_for_dry_scenario():
    crops = load_crops()
    traits = load_crop_climate_traits()
    rotations = generate_rotations(crops)

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    results = rank_rotations_for_scenario(
        rotations,
        crops,
        traits,
        priorities,
        "dry",
    )

    assert len(results) == 64

    scores = [
        result["score"]
        for result in results
    ]

    assert scores == sorted(scores, reverse=True)


def test_dry_climate_priority_ranks_winter_wheat_highest():
    crops = load_crops()
    traits = load_crop_climate_traits()
    rotations = generate_rotations(crops)

    priorities = {
        "soil_protection": 0,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    results = rank_rotations_for_scenario(
        rotations,
        crops,
        traits,
        priorities,
        "dry",
    )

    assert results[0]["rotation"] == (
        "winter_wheat",
        "winter_wheat",
        "winter_wheat",
    )

    assert results[0]["score"] == 1.0


def test_recommend_rotations_returns_all_scenarios():
    farm = {}

    scenarios = {
        "dry": {},
        "typical": {},
        "wet": {},
    }

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
    }

    assert len(result["scenario_results"]["dry"]) == 64
    assert len(result["scenario_results"]["typical"]) == 64
    assert len(result["scenario_results"]["wet"]) == 64

    assert result["soil_factors"]["soil_data_available"] is False



def test_recommend_rotations_returns_top_three():
    farm = {}

    scenarios = {
        "dry": {},
        "typical": {},
        "wet": {},
    }

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

    assert len(result["recommendations"]) == 3

    scores = [
        recommendation["score"]
        for recommendation in result["recommendations"]
    ]

    assert scores == sorted(scores, reverse=True)

    assert all(
        recommendation["scenario_id"] == "dry"
        for recommendation in result["recommendations"]
    )


def test_rotation_explanations_are_transparent():
    crops = load_crops()
    traits = load_crop_climate_traits()

    priorities = {
        "soil_protection": 1,
        "water_suitability": 0,
        "climate_resilience": 1,
    }

    result = score_rotation_for_scenario(
        ("corn", "soybean", "oats"),
        crops,
        traits,
        priorities,
        "dry",
    )

    explanations = build_rotation_explanations(result)

    assert (
        "Uses three different cash crops across the three-year rotation."
        in explanations
    )

    assert (
        "Avoids planting the same cash crop in consecutive years."
        in explanations
    )

    assert any(
        "drought-resilience" in explanation
        for explanation in explanations
    )


def test_recommendations_include_explanations():
    farm = {}

    scenarios = {
        "dry": {},
        "typical": {},
        "wet": {},
    }

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

    assert len(result["recommendations"]) == 3

    for recommendation in result["recommendations"]:
        assert "why" in recommendation
        assert recommendation["why"]

def test_build_cover_crop_options():
    crops = load_crops()

    options = build_cover_crop_options(crops)

    assert len(options) == 2

    assert options[0]["cover_crop_id"] == "cereal_rye"
    assert options[0]["after_year"] == 1
    assert options[0]["before_year"] == 2

    assert options[1]["cover_crop_id"] == "cereal_rye"
    assert options[1]["after_year"] == 2
    assert options[1]["before_year"] == 3

    assert all(
        option["feasibility_status"] == "not_evaluated"
        for option in options
    )


def test_recommendations_include_cover_crop_options():
    result = recommend_rotations(
        {},
        {
            "dry": {},
            "typical": {},
            "wet": {},
        },
        {
            "soil_protection": 1,
            "water_suitability": 0,
            "climate_resilience": 1,
        },
    )

    for recommendation in result["recommendations"]:
        assert "cover_crop_options" in recommendation
        assert len(recommendation["cover_crop_options"]) == 2


def test_baseline_none_without_current_rotation():
    crops = load_crops()
    traits = load_crop_climate_traits()

    result = build_baseline_result(
        {},
        crops,
        traits,
        {
            "soil_protection": 1,
            "water_suitability": 0,
            "climate_resilience": 1,
        },
    )

    assert result is None


def test_baseline_scores_current_rotation():
    crops = load_crops()
    traits = load_crop_climate_traits()

    farm = {
        "current_rotation": (
            "corn",
            "soybean",
            "corn",
        )
    }

    result = build_baseline_result(
        farm,
        crops,
        traits,
        {
            "soil_protection": 1,
            "water_suitability": 0,
            "climate_resilience": 1,
        },
    )

    assert result["rotation"] == (
        "corn",
        "soybean",
        "corn",
    )

    assert set(result["scenario_scores"]) == {
        "dry",
        "typical",
        "wet",
    }


def test_recommend_rotations_includes_baseline():
    result = recommend_rotations(
        {
            "current_rotation": (
                "corn",
                "soybean",
                "corn",
            )
        },
        {
            "dry": {},
            "typical": {},
            "wet": {},
        },
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