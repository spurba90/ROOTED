"""
Regret summary for ROOTED's climate replay.

Regret in a scenario = the best score any rotation achieved in that
scenario minus this rotation's score in that scenario. A rotation with
regret 0 was (tied for) best in that scenario. Maximum regret is the
largest of these across scenarios: the most a farmer would "give up"
relative to the best choice in hindsight, in the worst historical case.

Regret is measured in ROOTED's heuristic score units. It is a relative
comparison, not lost yield, income, or soil quality.
"""


def calculate_scenario_regret(scenario_results):
    """
    Return {cycle_key: {scenario_id: regret}} from ranked scenario results.

    Every start year of the same cycle has the same score, so one value
    per cycle and scenario is returned.
    """
    regret = {}

    for scenario_id, ranked in scenario_results.items():
        best_score = max(item["score"] for item in ranked)

        for item in ranked:
            regret.setdefault(item["cycle_key"], {})[scenario_id] = round(
                best_score - item["score"],
                6,
            )

    return regret