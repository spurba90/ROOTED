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



def load_crop_critical_windows(
    path="data/crop_critical_windows.csv"
):
    """
    Load each crop's documented drought-sensitive calendar month.

    The month is when the crop's most water-sensitive growth stage
    typically occurs in Iowa. It is a timing assumption with a cited
    basis, not a measured field observation.
    """
    windows = {}

    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = {"crop_id", "critical_month"}
        missing_columns = required_columns - set(reader.fieldnames or [])

        if missing_columns:
            raise ValueError(
                f"Critical-window file is missing columns: "
                f"{sorted(missing_columns)}"
            )

        for row in reader:
            crop_id = (row["crop_id"] or "").strip()
            month_value = (row["critical_month"] or "").strip()

            if not crop_id:
                raise ValueError("Missing crop_id in critical windows")

            if not month_value:
                raise ValueError(
                    f"Missing critical month for '{crop_id}'"
                )

            if crop_id in windows:
                raise ValueError(
                    f"Duplicate critical-window crop ID: {crop_id}"
                )

            month = int(month_value)

            if not 1 <= month <= 12:
                raise ValueError(
                    f"Invalid critical month for '{crop_id}': {month}"
                )

            windows[crop_id] = {
                "critical_month": month,
                "critical_stage": (row.get("critical_stage") or "").strip(),
                "source_url": (row.get("source_url") or "").strip(),
            }

    return windows