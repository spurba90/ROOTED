from src.recommendations.crop_rules import validate_cover_crop
from itertools import product

def create_cover_crop_practice(cover_crop_id, after_year, crops):
    """
    Create a proposed cover-crop practice between two cash-crop entries.

    This does not confirm agricultural feasibility.
    """

    validate_cover_crop(cover_crop_id, crops)

    if after_year not in (1, 2):
        raise ValueError("Cover crops must be placed after year 1 or 2")

    return {
        "cover_crop_id": cover_crop_id,
        "after_year": after_year,
        "before_year": after_year + 1,
        "feasibility_status": "not_evaluated"
    }

def generate_rotations(crops):
    """
    Generate all possible three-entry cash-crop sequences.

    These are candidates, not confirmed feasible rotations.
    """

    cash_crop_ids = [
        crop["crop_id"]
        for crop in crops
        if crop["crop_type"] == "cash"
    ]

    return list(product(cash_crop_ids, repeat=3))