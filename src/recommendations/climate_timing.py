"""
Monthly rainfall timing for ROOTED's climate component.

Reads Preethi's raw NASA POWER daily file (data/raw/) without
changing it, totals each May-September month, and ranks each month
against the same month in every other year of the record.
"""
import csv
from collections import defaultdict


GROWING_SEASON_MONTHS = range(5, 10)

# A crop's sensitive month counts as dry when its rainfall is in the
# driest quarter of the record for that month. This matches the
# 25th-percentile rule used to define the dry scenario.
DRY_WINDOW_PERCENTILE = 0.25


def load_monthly_precip_totals(
    path="data/raw/nasa_power_ames_iowa_2005_2025.csv"
):
    """
    Total daily NASA POWER precipitation (PRECTOTCORR, mm/day) into
    May-September monthly totals. Returns {(year, month): mm}.

    Missing values (-999 or blank) stop the calculation; nothing
    is filled in.
    """
    totals = defaultdict(float)

    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        missing_columns = {"date", "PRECTOTCORR"} - set(
            reader.fieldnames or []
        )

        if missing_columns:
            raise ValueError(
                f"Daily climate file is missing columns: "
                f"{sorted(missing_columns)}"
            )

        for row in reader:
            date = row["date"].strip()
            year, month = int(date[:4]), int(date[4:6])

            if month not in GROWING_SEASON_MONTHS:
                continue

            value = (row["PRECTOTCORR"] or "").strip()

            if value == "" or float(value) == -999:
                raise ValueError(f"Missing precipitation value on {date}")

            totals[(year, month)] += float(value)

    years = {year for year, _ in totals}

    for year in years:
        for month in GROWING_SEASON_MONTHS:
            if (year, month) not in totals:
                raise ValueError(
                    f"Missing precipitation for {year}-{month:02d}"
                )

    return dict(totals)


def calculate_monthly_percentiles(monthly_totals):
    """
    Rank each month's rainfall against the same month in every year
    of the record. Returns {year: {month: percentile}}, where values
    near 0 are the driest and 1.0 is the wettest. Ties share the
    average rank.
    """
    percentiles = defaultdict(dict)

    for month in GROWING_SEASON_MONTHS:
        values = {
            year: total
            for (year, m), total in monthly_totals.items()
            if m == month
        }
        count = len(values)

        for year, total in values.items():
            below = sum(1 for other in values.values() if other < total)
            equal = sum(1 for other in values.values() if other == total)
            percentiles[year][month] = (below + (equal + 1) / 2) / count

    return dict(percentiles)


def build_jul_aug_stress_scenario(monthly_totals):
    """
    Pick the year with the lowest combined July + August rainfall as a
    stress test. Corn (July) and soybean (August) are most
    water-sensitive in these months, which a May-September total can hide.
    """
    years = sorted({year for year, _ in monthly_totals})

    jul_aug = {
        year: monthly_totals[(year, 7)] + monthly_totals[(year, 8)]
        for year in years
    }

    stress_year = min(years, key=lambda year: (jul_aug[year], year))

    return {
        "representative_year": stress_year,
        "season_start_month": 5,
        "season_end_month": 9,
        "total_precip_mm": round(
            sum(
                monthly_totals[(stress_year, month)]
                for month in GROWING_SEASON_MONTHS
            ),
            2,
        ),
        "jul_aug_precip_mm": round(jul_aug[stress_year], 2),
    }


def build_climate_profiles(scenarios, monthly_percentiles):
    """
    For each scenario, record which growing-season months were in the
    driest quarter of the record in its representative year.

    Missing months are reported as errors, never filled in.
    """
    profiles = {}

    for scenario_id, scenario in scenarios.items():
        year = scenario["representative_year"]

        if year not in monthly_percentiles:
            raise ValueError(
                f"No monthly precipitation data for {scenario_id} "
                f"year {year}"
            )

        months = range(
            scenario["season_start_month"],
            scenario["season_end_month"] + 1,
        )

        missing_months = [
            month for month in months
            if month not in monthly_percentiles[year]
        ]

        if missing_months:
            raise ValueError(
                f"Missing monthly precipitation for {year}: "
                f"{missing_months}"
            )

        month_percentiles = {
            month: monthly_percentiles[year][month]
            for month in months
        }

        profiles[scenario_id] = {
            "scenario_id": scenario_id,
            "representative_year": year,
            "month_percentiles": month_percentiles,
            "dry_months": sorted(
                month
                for month, percentile in month_percentiles.items()
                if percentile <= DRY_WINDOW_PERCENTILE
            ),
        }

    return profiles