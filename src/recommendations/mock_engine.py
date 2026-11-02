"""MOCK rotation engine with the agreed interface. Scores are illustrative placeholders,
NOT agronomic evidence. Replace with Sim's engine.recommend_rotations(farm, scenarios, priorities).
Real scenario P - ref ET values DO change water scores, so NASA data will affect results."""
SCENARIOS = ["typical", "dry", "wet"]

CANDIDATES = {
    "R1": dict(crops=["Corn", "Soybeans", "Oats"], soil=72, water=70, res=74, sens=12, wet=4,
               cover=dict(name="Cover crop after oat harvest", window="Seed soon after oat harvest (summer/early fall)",
                          caveat="Needs seed, drill/broadcast equipment and a termination plan.")),
    "R2": dict(crops=["Corn", "Soybeans", "Corn"], soil=50, water=66, res=52, sens=18, wet=6,
               cover=dict(name="Cereal rye after corn harvest", window="Short fall window before soybeans",
                          caveat="Late seeding limits growth; terminate before planting.")),
    "R3": dict(crops=["Corn", "Soybeans", "Alfalfa"], soil=78, water=62, res=70, sens=8, wet=8, cover=None),
    "R4": dict(crops=["Soybeans", "Corn", "Oats"], soil=70, water=68, res=72, sens=13, wet=5,
               cover=dict(name="Cover crop after oat harvest", window="Seed soon after oat harvest (summer/early fall)",
                          caveat="Needs seed, drill/broadcast equipment and a termination plan.")),
}


def _penalty(scen_pet, typ_pet, sens, irrigation, soil):
    p = sens * max(0.0, typ_pet - scen_pet) / 100.0
    p *= {"Irrigated": 0.5, "Limited irrigation": 0.75}.get(irrigation, 1.0)
    return p * (1.25 if soil in ("Sandy", "Sandy loam") else 1.0)


def recommend_rotations(farm, scenarios, priorities):
    pet = {r["scenario"]: float(r["precip_mm"]) - float(r["ref_et_mm"]) for _, r in scenarios.iterrows()}
    typ = pet["typical"]
    allowed, prior = set(farm["allowed"]), farm["crop_history"][0]
    w = {k: max(0, priorities.get(k, 0)) for k in ("soil", "water", "resilience")}
    if sum(w.values()) == 0:
        w = {k: 1 for k in w}
    results, excluded = [], []
    for rid, c in CANDIDATES.items():
        label = " → ".join(c["crops"])
        missing = [x for x in c["crops"] if x not in allowed]
        if missing:
            excluded.append({"rotation_id": rid, "crops": label, "reason": f"Not in your crop list: {', '.join(missing)}"})
            continue
        if c["crops"][0] == prior:
            excluded.append({"rotation_id": rid, "crops": label, "reason": f"Year 1 repeats the previous crop ({prior})"})
            continue
        cover = c["cover"] if farm.get("cover_crop_ok") else None
        soil_s = min(100, c["soil"] + (6 if cover else 0))
        comps, sc_scores = {}, {}
        for s in SCENARIOS:
            pen = _penalty(pet[s], typ, c["sens"], farm["irrigation"], farm["soil"])
            wet_pen = c["wet"] * (1.5 if "poor" in farm.get("drainage", "").lower() else 1.0) if s == "wet" else 0
            comps[s] = {"soil": round(soil_s, 1), "water": round(max(0, c["water"] - pen - wet_pen), 1),
                        "resilience": round(max(0, c["res"] - 0.5 * (pen + wet_pen)), 1)}
            sc_scores[s] = round(sum(w[k] * comps[s][k] for k in w) / sum(w.values()), 1)
        results.append(dict(rotation_id=rid, crops_by_year=c["crops"], cover_crop=cover,
                            score_components=comps["typical"], scenario_components=comps,
                            scenario_scores=sc_scores, total=round(sum(sc_scores.values()) / 3, 1)))
    results.sort(key=lambda r: r["total"], reverse=True)
    for s in SCENARIOS:
        best = max((r["scenario_scores"][s] for r in results), default=0)
        for i, r in enumerate(sorted(results, key=lambda r: r["scenario_scores"][s], reverse=True), 1):
            r.setdefault("scenario_ranks", {})[s] = i
            r.setdefault("regret", {})[s] = round(best - r["scenario_scores"][s], 1)
    for i, r in enumerate(results, 1):
        r["rank"] = i
        r["max_regret"] = max(r["regret"].values())
        top = max(w, key=lambda k: w[k] * r["score_components"][k])
        r["explanation"] = (f"Ranks #{i} overall. Strongest contribution for your priorities: {top}. "
                            f"Rank under dry: #{r['scenario_ranks']['dry']}; under wet: #{r['scenario_ranks']['wet']}.")
        r["limitations"] = ["Modeled suitability, not a yield, profit or soil-improvement forecast.",
                            "Placeholder scores pending Sim's cited crop rules.",
                            "Soil and climate inputs are proxies; confirm locally with Iowa State Extension."]
    return {"rotations": results, "excluded": excluded,
            "meta": {"mock": True, "weights_used": w, "scenario_pet_mm": pet}}
