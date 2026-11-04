import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "crop_id",
    "crop_name",
    "crop_family",
    "crop_type",
    "planting_season",
    "harvest_season",
}

VALID_CROP_TYPES = {"cash", "cover"}
VALID_SEASONS = {"spring", "summer", "fall", "winter"}


def load_crops(path="data/crops.csv"):
    path = Path(path)

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Crop CSV is empty")

        if set(reader.fieldnames) != REQUIRED_COLUMNS:
            raise ValueError("Crop CSV has missing or unexpected columns")

        crops = list(reader)

    if not crops:
        raise ValueError("Crop database has no records")

    for row_number, crop in enumerate(crops, start=2):
        if None in crop:
            raise ValueError(f"Extra columns found at CSV row {row_number}")

        for column in REQUIRED_COLUMNS:
            if not crop[column] or not crop[column].strip():
                raise ValueError(
                    f"Missing value in column '{column}' at CSV row {row_number}"
                )

            crop[column] = crop[column].strip()

    crop_ids = [crop["crop_id"] for crop in crops]

    if len(crop_ids) != len(set(crop_ids)):
        raise ValueError("Duplicate crop IDs found in the database")



    for crop in crops:
        if crop["crop_type"] not in VALID_CROP_TYPES:
            raise ValueError(
                f"Invalid crop type for {crop['crop_id']}: {crop['crop_type']}"
            )

        for column in ("planting_season", "harvest_season"):
            if crop[column] not in VALID_SEASONS:
                raise ValueError(
                    f"Invalid {column} for {crop['crop_id']}: {crop[column]}"
                )


    return crops

def load_crop_climate_traits(
    path="data/crop_climate_traits.csv"
):
    """
    Load documented crop climate traits used by the
    recommendation engine.

    The loader does not create or modify trait values.
    """
    traits = {}

    with open(path, newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "crop_id",
            "dry_resilience_rank",
        }

        if set(reader.fieldnames or []) != required_columns:
            raise ValueError(
                "Crop climate trait columns do not match expected schema"
            )

        for row in reader:
            crop_id = row["crop_id"].strip()
            rank_value = row["dry_resilience_rank"].strip()

            if not crop_id:
                raise ValueError("Missing crop_id in climate traits")

            if not rank_value:
                raise ValueError(
                    f"Missing dry resilience rank for '{crop_id}'"
                )

            if crop_id in traits:
                raise ValueError(
                    f"Duplicate climate trait crop ID: {crop_id}"
                )

            traits[crop_id] = {
                "dry_resilience_rank": int(rank_value)
            }

    return traits