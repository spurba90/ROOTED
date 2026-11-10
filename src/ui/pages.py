import base64
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_climate_annual, load_provenance
from src.ui import engine_bridge

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
SOIL = ["Loam", "Silt loam", "Clay loam", "Sandy loam", "Clay", "Sandy", "Unknown"]
DRAIN = ["Well drained", "Moderately well drained", "Somewhat poorly drained", "Poorly drained", "Unknown"]
CROPS = ["Corn", "Soybeans", "Oats", "Winter wheat"]
CROP_OPTS = CROPS + ["Unknown / other"]
TILE = ["Don't know", "Yes", "No"]
COL_LABEL = {"avg_temp_c": "Mean temperature, May–Sep (°C)",
             "total_precip_mm": "Total precipitation, May–Sep (mm)",
             "avg_daily_et_mj_m2_day": "ET energy flux (EVPTRNS), May–Sep mean (MJ/m²/day)",
             "total_et_energy_mj_m2": "ET energy flux (EVPTRNS), May–Sep total (MJ/m²)",
             "temp_anomaly_c": "Temperature anomaly vs 2005–2025 (°C)",
             "precip_anomaly_mm": "Precipitation anomaly vs 2005–2025 (mm)",
             "precip_anomaly_pct": "Precipitation anomaly vs 2005–2025 (%)"}
SCN_LABEL = {"dry": "Dry year", "typical": "Typical year", "wet": "Wet year",
             "jul_aug_dry": "2013 stress test: driest July–August on record"}
DISCLAIMER = ("ROOTED provides data-informed rotation possibilities based on historical environmental conditions and "
              "documented crop characteristics. Scores are relative scores, not yield, profit or soil-health predictions. "
              "Recommendations are exploratory and should be reviewed with local farmers, soil specialists, and "
              "agricultural experts before implementation.")
DEFAULT_FARM = {"farm_id": "IA-AMES-01", "farm_name": "", "location": "Ames, Iowa", "county": "Story County",
                "lat": 42.03, "lon": -93.62, "acres": 160, "soil": "Silt loam", "drainage": "Moderately well drained",
                "soil_notes": "", "tile_drained": "Don't know", "prior_crop": "Soybeans",
                "current_rotation": ["Corn", "Soybeans", "Corn"], "irrigation_available": False,
                "weights": {"soil": 6, "water": 5, "resilience": 5}}


def ensure_farm():
    f = st.session_state.farm
    for k, v in DEFAULT_FARM.items():
        f.setdefault(k, dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v))
    for k, v in DEFAULT_FARM["weights"].items():
        f["weights"].setdefault(k, v)
    return f


def go(page):
    st.session_state.page = page


def uri(name):
    p = ASSETS / name
    if not p.exists():
        return ""
    mime = "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def title(t, sub):
    st.markdown(f"<h1 style='margin-bottom:0'>{t}</h1><p class='rooted-muted'>{sub}</p>", unsafe_allow_html=True)


def label_crop(c):
    if isinstance(c, dict):
        c = c.get("crop_id") or c.get("id") or c.get("name") or c.get("label") or "Unknown"
    return engine_bridge.ID_LABEL.get(c, str(c).replace("_", " ").title())


def crops_text(card):
    crops = card.get("crops_by_year") or []
    return " → ".join(label_crop(c) for c in crops)


def num(x, nd=1):
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) else ("—" if x is None else str(x))


# ---------------------------------------------------------------- Dashboard
def dashboard():
    ensure_farm()
    ann, samp = load_climate_annual()
    hero = uri("farm_hero.jpg")
    img = f'<img src="{hero}" alt="Iowa farm field">' if hero else ""
    st.markdown(f"""<div class="rooted-hero-inline">{img}<div class="rooted-hero-overlay">
      <h1>Welcome to ROOTED!</h1><p>NASA-powered agricultural decision support<br>for climate-resilient farming.</p>
      </div></div>""", unsafe_allow_html=True)
    st.write("")
    tag = "Sample data" if samp else f"{int(ann.year.min())}–{int(ann.year.max())}, May–Sep"
    shown = [c for c in ("avg_temp_c", "total_precip_mm", "avg_daily_et_mj_m2_day") if c in ann.columns]
    cols = st.columns(max(1, len(shown)))
    units = {"avg_temp_c": ("🌡️ Mean temperature", "{:.1f} °C"), "total_precip_mm": ("🌧️ Seasonal precipitation", "{:.0f} mm"),
             "avg_daily_et_mj_m2_day": ("🌿 ET energy flux (EVPTRNS)", "{:.2f} MJ/m²/day")}
    for col, c in zip(cols, shown):
        col.metric(units[c][0], units[c][1].format(ann[c].mean()), tag)
    left, right = st.columns([2.15, 1], gap="small")
    with left:
        a, b = st.columns([.9, 1.5], gap="small")
        with a:
            if (ASSETS / "seedling.jpg").exists():
                with st.container(key="seedling_panel"):
                    st.image(str(ASSETS / "seedling.jpg"), width="stretch")
        with b:
            with st.container(border=True, key="feature_panel"):
                st.markdown("""<h2>Grow Smarter with ROOTED</h2>
                <p>Combine NASA climate insights with documented crop strategies to compare rotations for your farm.</p>
                <div class='rooted-check'><span>✓</span> Explore historical climate patterns</div>
                <div class='rooted-check'><span>✓</span> Compare your rotation with alternatives</div>
                <div class='rooted-check'><span>✓</span> Replay climate stress scenarios</div>""", unsafe_allow_html=True)
                st.button("Get Started  →", type="primary", key="get_started", on_click=go, args=("Farm Profile",))
    with right:
        st.markdown("""<div class='rooted-green-card rooted-quick'><h2>💡 Quick Start</h2>
        <div class='rooted-step'><b>1</b><div><strong>Complete your Farm Profile</strong><br><small>Tell us about your farm.</small></div></div>
        <div class='rooted-step'><b>2</b><div><strong>Explore Farm Memory</strong><br><small>View historical climate data.</small></div></div>
        <div class='rooted-step'><b>3</b><div><strong>Check Rotation Options</strong><br><small>Compare crop rotations.</small></div></div>
        <div class='rooted-step'><b>4</b><div><strong>Replay Climate Scenarios</strong><br><small>See how rankings change.</small></div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class='rooted-footer'><div>🌱 Climate-Smart Farming</div><div>📈 Data-Driven Decisions</div>
    <div>🛡️ A More Resilient Tomorrow</div></div>""", unsafe_allow_html=True)
    if samp:
        st.caption("Climate values shown are sample placeholders until real NASA POWER data is in data/processed/.")


# ------------------------------------------------------------- Farm Profile
def farm_profile():
    p = ensure_farm()
    title("Farm Profile", "Tell ROOTED about your field. Your inputs and priority weights drive the comparison.")
    with st.form("farm_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Farm name (optional)", p["farm_name"])
            acres = st.number_input("Field size (acres)", 1, 100000, int(p["acres"]))
            soil = st.selectbox("Soil texture", SOIL, index=SOIL.index(p["soil"]) if p["soil"] in SOIL else 0)
            drain = st.selectbox("Drainage class", DRAIN, index=DRAIN.index(p["drainage"]) if p["drainage"] in DRAIN else 0)
            tile = st.selectbox("Is this field tile-drained?", TILE, index=TILE.index(p["tile_drained"]) if p["tile_drained"] in TILE else 0)
            notes = st.text_area("Soil notes / soil-test details (optional)", p["soil_notes"])
            st.caption("Soil and tile-drainage answers are saved but not used in scoring yet.")
        with c2:
            prior = st.selectbox("Previous crop (last season)", CROP_OPTS,
                                 index=CROP_OPTS.index(p["prior_crop"]) if p["prior_crop"] in CROP_OPTS else len(CROP_OPTS) - 1)
            st.markdown("**Your current rotation**")
            rc = st.columns(3)
            cur = []
            for i in range(3):
                v = p["current_rotation"][i] if i < len(p["current_rotation"]) else CROPS[0]
                cur.append(rc[i].selectbox(f"Year {i+1}", CROPS, index=CROPS.index(v) if v in CROPS else 0, key=f"cur{i}"))
            irr = st.checkbox("Irrigation available", value=bool(p["irrigation_available"]))
            st.caption("Irrigation is recorded but not used in the score yet.")
        st.markdown("**Priorities (0 = ignore, 10 = very important)**")
        w = st.columns(3)
        ws = {"soil": w[0].slider("Soil protection", 0, 10, int(p["weights"]["soil"])),
              "water": w[1].slider("Water suitability (not scored yet)", 0, 10, int(p["weights"]["water"])),
              "resilience": w[2].slider("Climate resilience", 0, 10, int(p["weights"]["resilience"]))}
        ok = st.form_submit_button("Save Farm Profile", type="primary")
        if ok:
          st.session_state.farm = {**p, "farm_name": name, "acres": acres, "soil": soil, "drainage": drain,
                                 "tile_drained": tile, "soil_notes": notes, "prior_crop": prior,
                                 "current_rotation": cur, "irrigation_available": irr, "weights": ws}
        st.success("Farm profile saved for this session.")

    # USDA mapped soil information for the Ames demonstration area
    st.markdown("### USDA mapped soil profile")
    st.caption(
        "This is a separate reference profile for the Ames demonstration location. "
        "It does not replace your field-specific soil answers above."
    )

    usda_profile = engine_bridge.load_usda_soil_metadata()

    if not usda_profile:
        st.warning("USDA soil profile is currently unavailable.")
    else:
        usda_soil = usda_profile.get("soil", {})
        usda_source = usda_profile.get("source", {})
        usda_location = usda_profile.get("location", {})

        with st.container(border=True):
            st.markdown(
                f"**Mapped soil unit:** "
                f"{usda_source.get('map_unit_name', 'Not available')}"
            )

            st.caption(
                f"Location: {usda_location.get('name', 'Ames, Iowa')} · "
                f"Dominant component: "
                f"{usda_source.get('component_name', 'Not available')} "
                f"({usda_source.get('component_percentage', 'Not available')}%)"
            )

            soil_cols = st.columns(3)
            soil_cols[0].metric(
                "Texture", usda_soil.get("texture") or "Not available"
            )
            soil_cols[1].metric(
                "pH", usda_soil.get("ph") if usda_soil.get("ph") is not None else "Not available"
            )
            soil_cols[2].metric(
                "Organic matter",
                f"{usda_soil['organic_matter_pct']}%"
                if usda_soil.get("organic_matter_pct") is not None
                else "Not available",
            )

            soil_cols = st.columns(2)
            soil_cols[0].metric(
                "Drainage", usda_soil.get("drainage_class") or "Not available"
            )
            soil_cols[1].metric(
                "Available water capacity (cm/cm)",
                usda_soil.get("available_water_capacity")
                if usda_soil.get("available_water_capacity") is not None
                else "Not available",
            )

            st.caption(
                f"Surface horizon: {usda_source.get('surface_horizon', 'Not available')} · "
                f"Depth: {usda_source.get('surface_depth_cm', 'Not available')} cm"
            )

            st.markdown(
                f"**Source:** {usda_source.get('name', 'USDA NRCS Soil Data Access')}"
            )
            source_url = usda_source.get("url")
            if source_url:
                st.markdown(f"[View USDA Soil Data Access]({source_url})")

            st.info(
                "These are representative mapped soil estimates, not measurements "
                "from an individual farm field. Available water capacity describes "
                "the soil's capacity to hold plant-available water; it is not "
                "current soil moisture."
            )

            limitations = usda_profile.get("limitations", [])
            if limitations:
                with st.expander("USDA data limitations"):
                    for limitation in limitations:
                        st.markdown(f"- {limitation}")

with st.expander("Saved profile (JSON)"):
    if "farm" in st.session_state:
        st.json(st.session_state.farm)
    else:
        st.info("No saved farm profile yet. Save your profile above.")


# -------------------------------------------------------------- Farm Memory
def farm_memory():
    f = ensure_farm()
    title("Farm Memory", "Historical NASA climate context for the demonstration area.")
    ann, samp = load_climate_annual()
    if samp:
        st.markdown("<span class='rooted-tag'>SAMPLE climate data — not NASA observations</span>", unsafe_allow_html=True)
    options = {COL_LABEL.get(c, c): c for c in ann.columns
               if c not in ("farm_id", "year", "days_observed") and pd.api.types.is_numeric_dtype(ann[c])}
    if not options or "year" not in ann.columns:
        st.error("climate_annual.csv needs a 'year' column and at least one numeric column.")
        return
    label = st.selectbox("Climate measure", list(options))
    col = options[label]
    d = ann.dropna(subset=[col])
    if len(d) < len(ann):
        st.caption(f"{len(ann)-len(d)} year(s) with missing values omitted.")
    fig = px.line(d, x="year", y=col, markers=True, labels={"year": "Year", col: label})
    fig.update_traces(line_color="#2f7d3b")
    st.plotly_chart(fig, width="stretch")
    st.caption("May–September growing-season summaries from NASA POWER (T2M, PRECTOTCORR, EVPTRNS), a gridded estimate for this "
               "location, not a measurement on one field. EVPTRNS is an energy flux, not a water depth: do not subtract it from rainfall in mm.")
    a, b = st.columns([1.3, 1])
    with a:
        st.markdown("#### Data provenance")
        st.dataframe(load_provenance(), width="stretch", hide_index=True)
    with b:
        st.markdown("#### Location (approximate)")
        st.map(pd.DataFrame({"lat": [f["lat"]], "lon": [f["lon"]]}), zoom=8)
        st.caption(f"Farm ID {f['farm_id']} · {f['location']}, {f['county']}")
    st.download_button("Download climate data (CSV)", ann.to_csv(index=False), "rooted_climate.csv", "text/csv")


# -------------------------------------------------------- Rotation Advisor
def _card(card, current=False):
    with st.container(border=True):
        rank_label = "Baseline" if current else f"#{card.get('rank', '—')}"
        head = f"{rank_label} · {crops_text(card)}"
        st.subheader(("⭐ Your current rotation · " if current else "") + head)

        metrics = st.columns(3)
        metrics[0].metric("Relative score", num(card.get("score")))
        metrics[1].metric("Comparison", "Baseline" if current else card.get("rank", "—"))
        metrics[2].caption(
            f"Representative year: {card.get('representative_year', '—')}"
        )

        tied = card.get("tied_with") or 0
        tie_count = tied if isinstance(tied, (int, float)) else len(tied)

        if tie_count > 0:
            st.warning(
                f"Equal score with {tie_count} other distinct rotation cycle(s) "
                "in the full candidate ranking. The order among tied options "
                "is not meaningful."
            )

        share = card.get("dropped_priority_share") or 0
        if share > 0:
            pct = share * 100 if share <= 1 else share
            st.info(
                f"{pct:.0f}% of your selected priority weight is for "
                "water suitability, which is not scored yet."
            )

        st.markdown("**Why this rotation**")
        explanations = card.get("why") or []

        for line in explanations:
            # The tie is already explained in the warning above.
            if str(line).startswith("Tied with "):
                continue
            st.write("• " + str(line))

        climate = card.get("climate_component") or {}
        exposed = climate.get("exposed_crops")

        if exposed:
            st.write(
                "**Crops exposed to historical climate stress:** "
                + ", ".join(label_crop(c) for c in exposed)
            )

        covers = card.get("cover_crop_options") or []
        if covers:
            st.markdown("**Optional cover-crop practices**")
            for option in covers:
                if isinstance(option, dict):
                    name = (
                        option.get("name")
                        or option.get("label")
                        or option.get("cover_crop")
                        or option.get("id")
                        or "Cover crop"
                    )
                    caution = option.get("caution")
                    st.write(
                        f"• {name}" + (f" — ⚠️ {caution}" if caution else "")
                    )
                else:
                    st.write(f"• {option}")

        with st.expander("Score details"):
            weights = card.get("effective_weights") or {}

            st.markdown("**Effective scoring weights**")
            if isinstance(weights, dict) and weights:
                for name, value in weights.items():
                    st.write(
                        f"• {name.replace('_', ' ').title()}: {num(value, 2)}"
                    )
            else:
                st.caption("Detailed scoring weights are not available.")

            st.markdown("**Scored components**")

            soil_proxy = card.get("structural_soil_proxy")
            if soil_proxy is not None:
                st.write(
                    f"• Structural soil-protection proxy: {num(soil_proxy, 2)}"
                )
                st.caption(
                    "This is a rotation-structure heuristic, not a measured "
                    "soil-health result."
                )

            climate_value = climate.get("value")
            if climate_value is not None:
                st.write(
                    f"• Historical climate-resilience component: "
                    f"{num(climate_value, 2)}"
                )

            unavailable = card.get("unavailable_components") or []
            if unavailable:
                names = ", ".join(
                    name.replace("_", " ") for name in unavailable
                )
                st.caption(f"Components not included in this score: {names}.")

            st.caption(
                "Scores are relative comparisons within the selected "
                "historical scenario. They are not yield, profit, or "
                "measured soil-health predictions."
            )

def _baseline(base, scn, farm):
    st.markdown("### Your current rotation")

    if not isinstance(base, dict):
        base = {}

    # The engine stores scenario-specific baseline scores here.
    scenario_scores = base.get("scenario_scores") or {}

    if isinstance(scenario_scores, dict) and scn in scenario_scores:
        b = scenario_scores[scn]
    else:
        # Support the older scenario-specific baseline structure too.
        b = base.get(scn, base)

    if not isinstance(b, dict):
        b = {}

    # Prefer the scenario result's rotation, then the top-level baseline,
    # and finally the saved Farm Profile rotation.
    crops = (
        b.get("crops_by_year")
        or b.get("rotation")
        or base.get("rotation")
        or farm.get("current_rotation")
        or []
    )

    display_card = dict(b)
    display_card["crops_by_year"] = crops

    if crops:
        st.markdown("**Your three-year crop sequence**")
        st.success(" → ".join(label_crop(c) for c in crops))

        if b.get("score") is not None or b.get("rank") is not None:
            _card(display_card, current=True)
        else:
            st.caption(
                "This is the rotation saved in your Farm Profile. "
                "A baseline score was not returned for this scenario."
            )
    else:
        st.warning(
            "No current rotation is available. "
            "Please enter your three-year rotation in Farm Profile."
        )


def rotation_advisor():
    f = ensure_farm()
    title("Rotation Advisor", "Your current rotation compared with alternatives, using relative scores.")
    res, err = engine_bridge.run(f)
    if err:
        st.error(err)
        return
    st.info(DISCLAIMER)
    scn = st.radio("Scenario", list(SCN_LABEL), format_func=SCN_LABEL.get, horizontal=True)
    if scn == "jul_aug_dry":
        st.caption("A historical stress test, not a forecast.")
    ctx = (res.get("scenario_context") or {}).get(scn) or {}
    if ctx:
        st.caption(f"Historical year: {ctx.get('year', '—')} · Source: {ctx.get('source', '—')}")
    if res.get("baseline"):
        _baseline(res["baseline"], scn, f)
    else:
        st.caption("Enter a valid current rotation in Farm Profile to compare against it.")
    st.markdown("### Alternatives")
    cards = (res.get("recommendations") or {}).get(scn) or []
    if not cards:
        st.warning("No recommendations returned for this scenario.")
    for c in cards:
        _card(c)
    soil = res.get("soil_factors") or {}
    if soil.get("soil_data_status") == "none":
        st.info("Soil data not available. Soil is not used in the score.")
    irr = res.get("irrigation") or {}
    if irr.get("note"):
        st.info(str(irr["note"]))
    with st.expander("Limitations"):
        for l in res.get("limitations") or []:
            st.write("• " + str(l))


# ----------------------------------------------------------- Climate Replay
def climate_replay():
    f = ensure_farm()
    title(
        "Climate Replay",
        "Re-score the same rotations under historical dry, typical, wet and 2013 conditions."
    )

    res, err = engine_bridge.run(f)
    if err:
        st.error(err)
        return

    # ---------------------------------------------------------
    # Scenario context
    # ---------------------------------------------------------
    ctx = res.get("scenario_context") or {}
    rows = []

    month_names = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    for scenario_id, details in ctx.items():
        if not isinstance(details, dict):
            continue

        year = details.get("representative_year")

        if scenario_id == "jul_aug_dry":
            rainfall = details.get("jul_aug_precip_mm")
            rainfall_period = "July–August"
        else:
            rainfall = details.get("total_precip_mm")
            rainfall_period = "May–September"

        dry_months = details.get("dry_months") or []
        dry_month_labels = [
            month_names[m - 1]
            for m in dry_months
            if isinstance(m, int) and 1 <= m <= 12
        ]

        rows.append({
            "Scenario": SCN_LABEL.get(scenario_id, scenario_id),
            "Representative year": year if year is not None else "—",
            "Rainfall period": rainfall_period,
            "Rainfall (mm)": num(rainfall, 1),
            "Dry months": (
                ", ".join(dry_month_labels)
                if dry_month_labels
                else "Not specified"
            ),
            "Source": details.get("source") or "Not specified",
        })

    if rows:
        st.markdown("#### Scenarios replayed")
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True
        )
        st.caption(
            "The 2013 stress test identifies the year with the lowest "
            "combined July–August rainfall. This is a historical replay, "
            "not a forecast."
        )

    # ---------------------------------------------------------
    # Rotation replay results
    # ---------------------------------------------------------
    df = pd.DataFrame(res.get("climate_replay") or [])

    if df.empty:
        st.warning("No replay data returned.")
        return

    # The engine returns crop IDs in the "cycle" field.
    # Convert them into farmer-friendly rotation names.
    def rotation_name(row):
        cycle = row.get("cycle")

        if isinstance(cycle, (list, tuple)):
            return " → ".join(label_crop(crop) for crop in cycle)

        # Fallback for outputs that contain only the cycle key.
        cycle_key = row.get("cycle_key")
        if cycle_key:
            return " → ".join(
                label_crop(crop)
                for crop in str(cycle_key).split("-")
            )

        return "Rotation unavailable"

    df["Rotation"] = df.apply(rotation_name, axis=1)

    # Hide rotations that repeat a crop, except the farmer's
    # current rotation.
    if "repeats_crop" in df.columns and "is_current_rotation" in df.columns:
        repeats = df["repeats_crop"].fillna(False).astype(bool)
        current = df["is_current_rotation"].fillna(False).astype(bool)
        df = df[(~repeats) | current].copy()

    # ---------------------------------------------------------
    # Comparison table
    # ---------------------------------------------------------
    current_rotation = (
        df["is_current_rotation"].fillna(False).astype(bool)
        if "is_current_rotation" in df.columns
        else pd.Series(False, index=df.index)
    )

    out = pd.DataFrame({
        "Rotation": df["Rotation"],
        "Your current?": current_rotation.map({
            True: "⭐ Yes",
            False: ""
        }),
        "Best rank": df["best_rank"] if "best_rank" in df else "—",
        "Worst rank": df["worst_rank"] if "worst_rank" in df else "—",
        "Max regret": df["max_regret"] if "max_regret" in df else "—",
        "Worst scenario": [
            (
                "—"
                if pd.isna(regret) or regret == 0
                else SCN_LABEL.get(scenario, scenario)
            )
            for regret, scenario in zip(
                df["max_regret"] if "max_regret" in df else [None] * len(df),
                df["max_regret_scenario"] if "max_regret_scenario" in df else [None] * len(df)
            )
        ],
    })

    st.markdown("#### How each rotation holds up across scenarios")
    st.dataframe(
        out.sort_values(["Worst rank", "Best rank"]),
        width="stretch",
        hide_index=True
    )

    st.caption(
        "Regret = how far a rotation's relative score falls below the best "
        "option in a scenario. Rotations that repeat last season's crop "
        "are hidden, except your own."
    )

    # ---------------------------------------------------------
    # Rank chart
    # ---------------------------------------------------------
    try:
        longrows = []

        for _, row in df.iterrows():
            ranks = row.get("ranks") or {}

            if not isinstance(ranks, dict):
                continue

            for scenario_id, rank in ranks.items():
                longrows.append({
                    "Rotation": row["Rotation"],
                    "Scenario": SCN_LABEL.get(scenario_id, scenario_id),
                    "Rank": rank,
                })

        lr = pd.DataFrame(longrows)

        if not lr.empty:
            top_rotations = (
                df.sort_values("best_rank")["Rotation"]
                .head(6)
                .tolist()
            )

            current_names = df.loc[
                current_rotation,
                "Rotation"
            ].tolist()

            keep_names = set(top_rotations) | set(current_names)
            lr = lr[lr["Rotation"].isin(keep_names)]

            if not lr.empty:
                fig = px.line(
                    lr,
                    x="Scenario",
                    y="Rank",
                    color="Rotation",
                    markers=True,
                )
                fig.update_yaxes(autorange="reversed", dtick=1)
                st.plotly_chart(fig, width="stretch")

    except Exception:
        st.caption("Rank chart unavailable for this output format.")

    # ---------------------------------------------------------
    # Limitations and navigation
    # ---------------------------------------------------------
    with st.expander("Uncertainty notes", expanded=True):
        st.write(
            "• Replay is a historical stress test, not a forecast of future weather."
        )
        st.write(
            "• Scores are relative scores, not predicted yields, profits or soil-health changes."
        )
        st.write(
            "• Climate inputs are gridded estimates, not measurements on one field."
        )
        st.write(
            "• Soil, tile drainage, irrigation and water suitability are not scored yet."
        )

    st.button(
        "Back to Rotation Advisor",
        on_click=go,
        args=("Rotation Advisor",)
    )


# -------------------------------------------------------- Science & Sources
def science_sources():
    ensure_farm()
    title(
        "Science & Sources",
        "Explore the environmental data, agricultural references, "
        "and transparent methods behind ROOTED."
    )

    project_root = Path(__file__).resolve().parents[2]

    data_sources_path = project_root / "docs" / "data_sources.md"
    methodology_path = project_root / "docs" / "methodology.md"
    provenance_path = project_root / "data" / "processed" / "provenance.json"
    soil_path = project_root / "data" / "processed" / "ames_soil_profile.json"

    sources_tab, methods_tab, nasa_tab, soil_tab = st.tabs([
        "Data Sources",
        "How ROOTED Works",
        "NASA Data Provenance",
        "USDA Soil Profile",
    ])

    with sources_tab:
        st.markdown("### Agricultural data and references")
        if data_sources_path.exists():
            st.markdown(data_sources_path.read_text(encoding="utf-8"))
        else:
            st.error("The data sources documentation file could not be found.")

    with methods_tab:
        st.markdown("### Recommendation methodology")
        if methodology_path.exists():
            st.markdown(methodology_path.read_text(encoding="utf-8"))
        else:
            st.error("The methodology documentation file could not be found.")

    with nasa_tab:
        st.markdown("### NASA POWER climate data")
        st.write(
            "ROOTED uses historical, gridded NASA POWER data for the "
            "Ames, Iowa demonstration coordinates. These values provide "
            "regional climate context; they are not measurements from "
            "an individual farm field."
        )

        if provenance_path.exists():
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

            summary = pd.DataFrame([
                {
                    "Climate variable": item.get("variable", "—"),
                    "Definition": item.get("definition", "—"),
                    "Units": item.get("units", "—"),
                    "Data access date": item.get("access_date", "Not recorded"),
                }
                for item in provenance
            ])

            st.dataframe(summary, width="stretch", hide_index=True)

            st.warning(
                "The NASA POWER retrieval date has not yet been recorded "
                "in the project provenance file."
            )

            with st.expander("View processing details"):
                for item in provenance:
                    st.markdown(f"**{item.get('variable', 'Climate variable')}**")
                    st.write(f"Source: {item.get('source', 'Not specified')}")
                    st.write(f"Resolution: {item.get('resolution', 'Not specified')}")
                    st.write(
                        f"Transformation: {item.get('transformations', 'Not specified')}"
                    )
                    st.divider()
        else:
            st.error("The NASA provenance file could not be found.")

        st.info(
            "EVPTRNS represents evapotranspiration energy flux. It is not "
            "a water-depth measurement or reference ET, and should not be "
            "subtracted from precipitation in millimeters."
        )

        st.markdown("[NASA POWER data portal](https://power.larc.nasa.gov/)")

    with soil_tab:
        st.markdown("### USDA NRCS mapped soil profile")
        st.write(
            "This profile describes a mapped soil component near the Ames "
            "demonstration coordinates. It is not a laboratory test or a "
            "verified measurement from an individual farm field."
        )

        if soil_path.exists():
            soil_data = json.loads(soil_path.read_text(encoding="utf-8"))
            soil = soil_data.get("soil", {})
            source = soil_data.get("source", {})
            location = soil_data.get("location", {})

            st.markdown("#### Demonstration location")
            st.write(
                f"{location.get('name', 'Ames, Iowa')} · "
                f"{location.get('latitude', '—')}, "
                f"{location.get('longitude', '—')}"
            )

            st.markdown("#### Mapped soil component")
            st.write(f"**Map unit:** {source.get('map_unit_name', '—')}")
            st.write(
                f"**Dominant component:** {source.get('component_name', '—')} "
                f"({source.get('component_percentage', '—')}% of map unit)"
            )

            st.markdown("#### Representative surface-soil values")
            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Texture", soil.get("texture", "—"))
            c2.metric("pH", soil.get("ph", "—"))
            c3.metric(
                "Organic matter",
                f"{soil.get('organic_matter_pct', '—')}%"
            )
            c4.metric(
                "Available water capacity",
                f"{soil.get('available_water_capacity', '—')} "
                f"{source.get('awc_unit', 'cm/cm')}"
            )

            st.write(
                f"**Drainage class:** {soil.get('drainage_class', '—')}"
            )

            depth = source.get("surface_depth_cm", [])
            if len(depth) == 2:
                st.caption(
                    f"Surface horizon: {source.get('surface_horizon', '—')} · "
                    f"Depth: {depth[0]}–{depth[1]} cm"
                )

            source_url = source.get("url")
            if source_url:
                st.markdown(
                    f"**Source:** [{source.get('name', 'USDA NRCS Soil Data Access')}]"
                    f"({source_url})"
                )

            st.markdown("#### Important limitations")
            for limitation in soil_data.get("limitations", []):
                st.write(f"• {limitation}")
        else:
            st.error("The USDA soil profile file could not be found.")

    st.divider()
    st.caption(
        "ROOTED is an exploratory decision-support prototype. "
        "Its relative scores are not yield, profit, or measured "
        "soil-health predictions."
    )
