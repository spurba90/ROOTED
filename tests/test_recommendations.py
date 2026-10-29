import csv

import pytest

from src.recommendations.crop_data import load_crops


def test_duplicate_crop_ids(tmp_path):
    # Create a temporary CSV containing duplicate crop IDs.
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


    # The loader should reject duplicate crop IDs.
    with pytest.raises(ValueError, match="Duplicate crop IDs"):
        load_crops(test_file)



def test_missing_crop_value(tmp_path):
    # Create a temporary CSV with a missing crop family.
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

    # The loader should reject the missing value.
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
    # Start with a valid crop record.
    crop = {
        "crop_id": "corn",
        "crop_name": "Corn",
        "crop_family": "Poaceae",
        "crop_type": "cash",
        "planting_season": "spring",
        "harvest_season": "fall",
    }

    # Introduce one invalid value for each test case.
    crop[column] = invalid_value

    test_file = tmp_path / "invalid_crop.csv"

    with test_file.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=crop.keys())
        writer.writeheader()
        writer.writerow(crop)

    # Confirm the loader rejects the invalid value.
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