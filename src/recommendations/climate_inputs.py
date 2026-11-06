import csv


def load_climate_scenarios(
    path="data/processed/ames_climate_scenarios.csv"
):
    """
    Load historical climate scenarios prepared by the climate-data pipeline.

    The loader does not calculate or modify climate values.
    It only converts the scenario CSV into dictionaries for the
    recommendation engine.
    """
    scenarios = {}

    numeric_fields = {
        "representative_year": int,
        "season_start_month": int,
        "season_end_month": int,
        "avg_temp_c": float,
        "total_precip_mm": float,
        "temp_anomaly_c": float,
        "precip_anomaly_mm": float,
        "precip_anomaly_pct": float,
        "avg_daily_et_mj_m2_day": float,
        "total_et_energy_mj_m2": float,
    }

    with open(path, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            scenario_id = row["scenario_id"].strip()

            scenario = {}

            for field, converter in numeric_fields.items():
                value = row[field].strip()

                if value == "":
                    raise ValueError(
                        f"Missing value for '{field}' "
                        f"in scenario '{scenario_id}'"
                    )

                scenario[field] = converter(value)

            scenarios[scenario_id] = scenario

    return scenarios


def validate_climate_scenarios(scenarios):
    """
    Validate the climate scenario structure supplied to the
    recommendation engine.

    This checks the handoff structure and scenario ordering.
    It does not calculate crop suitability.
    """
    if not isinstance(scenarios, dict):
        raise TypeError("scenarios must be a dictionary")

    required_scenarios = {"dry", "typical", "wet"}

    if set(scenarios) != required_scenarios:
        raise ValueError(
            "scenarios must contain dry, typical, and wet"
        )

    required_fields = {
        "representative_year",
        "season_start_month",
        "season_end_month",
        "avg_temp_c",
        "total_precip_mm",
        "temp_anomaly_c",
        "precip_anomaly_mm",
        "precip_anomaly_pct",
        "avg_daily_et_mj_m2_day",
        "total_et_energy_mj_m2",
    }

    for scenario_name, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            raise TypeError(
                f"Scenario '{scenario_name}' must be a dictionary"
            )

        missing_fields = required_fields - set(scenario)

        if missing_fields:
            raise ValueError(
                f"Scenario '{scenario_name}' is missing fields: "
                f"{sorted(missing_fields)}"
            )

        for field in required_fields:
            if scenario[field] is None:
                raise ValueError(
                    f"Scenario '{scenario_name}' has missing value "
                    f"for '{field}'"
                )

    years = {
        scenarios[name]["representative_year"]
        for name in required_scenarios
    }

    if len(years) != 3:
        raise ValueError(
            "Climate scenarios must use three different representative years"
        )

    dry_precip = scenarios["dry"]["total_precip_mm"]
    typical_precip = scenarios["typical"]["total_precip_mm"]
    wet_precip = scenarios["wet"]["total_precip_mm"]

    if not dry_precip < typical_precip < wet_precip:
        raise ValueError(
            "Scenario precipitation must increase from dry to typical to wet"
        )

    return True