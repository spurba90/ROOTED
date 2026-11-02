def recommend_rotations(farm, scenarios, priorities):
    """
    Main entry point for ROOTED's recommendation engine.

    Parameters
    ----------
    farm : dict
        Farm profile, including current rotation and constraints.

    scenarios : dict
        Climate scenarios generated from NASA data.
        Environmental variables must include their units.

    priorities : dict
        Farmer preferences used when comparing rotations.

    Returns
    -------
    dict
        Baseline, recommendations, scenario results,
        and limitations.
    """

    if not isinstance(farm, dict):
        raise TypeError("farm must be a dictionary")

    if not isinstance(scenarios, dict):
        raise TypeError("scenarios must be a dictionary")

    if not isinstance(priorities, dict):
        raise TypeError("priorities must be a dictionary")

    return {
        "baseline": None,
        "recommendations": [],
        "scenario_results": {},
        "limitations": [
            "Recommendation scoring has not been implemented.",
            "Farm-specific feasibility has not been evaluated.",
            "Climate variables and units require validation."
        ]
    }