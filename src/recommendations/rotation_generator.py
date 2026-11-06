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



def canonical_cycle(rotation):
    """
    Return one standard form for a repeating three-year cycle.

    Sequences that are the same cycle started in a different year
    (for example corn-soybean-oats and soybean-oats-corn) share
    the same canonical form.
    """
    rotation = tuple(rotation)

    return min(
        rotation[index:] + rotation[:index]
        for index in range(len(rotation))
    )


def unique_cycles(rotations):
    """
    Keep one sequence per distinct repeating cycle.
    """
    seen = {}

    for rotation in rotations:
        seen.setdefault(canonical_cycle(rotation), tuple(rotation))

    return list(seen.values())




def rotation_id(rotation):
    """
    Return a readable string ID for a rotation, e.g.
    ("oats", "soybean", "winter_wheat") -> "oats-soybean-winter_wheat".
    """
    return "-".join(rotation)