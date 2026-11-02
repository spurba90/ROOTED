import csv

import pytest

from src.recommendations.crop_data import load_crops
from src.recommendations.crop_rules import validate_rotation, validate_cover_crop
from src.recommendations.rotation_generator import create_cover_crop_practice
from src.recommendations.rotation_generator import (
    create_cover_crop_practice,
    generate_rotations,
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