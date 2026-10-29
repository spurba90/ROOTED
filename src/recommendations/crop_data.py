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

'''Code Notes:
Here we are loading our crop info from crops.csv and checking that the columns have the correct columns and data.
Returns and list of dictionaries representing one crop and its characteristics.

Later on, our recommendation engine will use this info to identify available crops and build possible rotations. 
When we validate data here it helps us catch any formatting issues before they cause problems. 

Duplicate ID Validation:
-Each crop needs a unique identifier so the recommendation engine can distinguish between different crops.
-We can compare the number of crop IDs with the number of unique IDs using a set.

If they are different we raise an error.

Crop catecory Validation:
-I check that each crop has a supported crop type and valid planting/harvest season labels.
-Prevents spelling mistakes or inconsistent values from going into the recomenndation engine.
These validate data formatting.


'''