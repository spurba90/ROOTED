import base64
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
        head = f"#{card.get('rank', '—')} · {crops_text(card)}"
        st.subheader(("⭐ Your current rotation · " if current else "") + head)
        m = st.columns(3)
        m[0].metric("Relative score", num(card.get("score")))
        m[1].metric("Rank", card.get("rank", "—"))
        m[2].caption(f"Representative year: {card.get('representative_year', '—')}")
        tied = card.get("tied_with") or 0
        if (tied if isinstance(tied, (int, float)) else len(tied)) > 0:
            n = tied if isinstance(tied, (int, float)) else len(tied)
            st.warning(f"Tied with {n} other(s) — order not meaningful.")
        share = card.get("dropped_priority_share") or 0
        if share > 0:
            pct = share * 100 if share <= 1 else share
            st.info(f"{pct:.0f}% of your priority weight (water) isn't scored yet.")
        st.markdown("**Why this rotation**")
        for line in card.get("why") or []:
            st.write("• " + str(line))
        exposed = (card.get("climate_component") or {}).get("exposed_crops")
        if exposed:
            st.write("**Crops exposed to climate stress this year:** " + ", ".join(label_crop(c) for c in exposed))
        covers = card.get("cover_crop_options") or []
        if covers:
            st.markdown("**Optional cover-crop practice**")
            for o in covers:
                if isinstance(o, dict):
                    nm = o.get("name") or o.get("label") or o.get("cover_crop") or o.get("id") or "Cover crop"
                    st.write(f"• {nm}" + (f" — ⚠️ {o['caution']}" if o.get("caution") else ""))
                else:
                    st.write(f"• {o}")
        with st.expander("Score details"):
         weights = card.get("effective_weights") or {}

    if isinstance(weights, dict) and weights:
        st.markdown("**Effective scoring weights**")
        for name, value in weights.items():
            st.write(f"• {name.replace('_', ' ').title()}: {num(value, 2)}")
    else:
        st.caption("Detailed scoring weights are not available.")

    st.caption(
        "Scores are relative comparisons based on the criteria "
        "supported by the recommendation engine."
    )


def _baseline(base, scn, farm):
    st.markdown("### Your current rotation")

    # Select the requested scenario when the baseline is scenario-specific.
    b = base.get(scn, base) if isinstance(base, dict) else {}

    if not isinstance(b, dict):
        b = {}

    # Use the engine's crop sequence when available.
    crops = b.get("crops_by_year") or b.get("rotation") or []

    # Fall back to the rotation saved in the Farm Profile.
    if not crops:
        crops = farm.get("current_rotation") or []

    # Build a display-friendly card.
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
    with st.expander("How to read these results"):
        for l in res.get("method_notes") or []:
            st.write("• " + str(l))
    with st.expander("Developer: raw engine output"):
        st.json(res, expanded=False)


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
