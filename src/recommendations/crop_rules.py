def validate_rotation(rotation, crops):
    """
    Check whether a three-year cash-crop sequence is structurally valid.

    This does not evaluate farm-specific or agronomic feasibility.
    """

    if len(rotation) != 3:
        raise ValueError("A rotation must contain exactly three crops")

    cash_crop_ids = {
        crop["crop_id"]
        for crop in crops
        if crop["crop_type"] == "cash"
    }

    for crop_id in rotation:
        if crop_id not in cash_crop_ids:
            raise ValueError(
                f"Unknown or non-cash crop in rotation: {crop_id}"
            )

    return True

def validate_cover_crop(cover_crop_id, crops):
    """
    Check whether a crop is registered as a cover crop.

    This checks crop classification only.
    It does not establish whether planting is feasible.
    """

    cover_crop_ids = {
        crop["crop_id"]
        for crop in crops
        if crop["crop_type"] == "cover"
    }

    if cover_crop_id not in cover_crop_ids:
        raise ValueError(
            f"Unknown or non-cover crop: {cover_crop_id}"
        )

    return True