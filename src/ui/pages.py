import base64
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_climate_annual, load_scenarios, load_provenance
from src.recommendations import recommend_rotations, IS_MOCK

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
SOIL = ["Loam", "Silt loam", "Clay loam", "Sandy loam", "Clay", "Sandy", "Unknown"]
DRAIN = ["Well drained", "Moderately well drained", "Somewhat poorly drained", "Poorly drained", "Unknown"]
IRRIG = ["Rain-fed", "Irrigated", "Limited irrigation", "Unknown"]
CROPS = ["Corn", "Soybeans", "Oats", "Alfalfa", "Wheat"]
HIST = CROPS + ["Cover crops", "Other/Unknown"]
VARS = {"Mean temperature (°C)": "mean_temp_c", "Precipitation (mm/yr)": "precip_mm",
        "Reference ET (mm/yr)": "ref_et_mm", "P − reference ET (mm/yr)": "p_minus_et_mm"}
SCEN_LABEL = {"typical": "Typical", "dry": "Dry", "wet": "Wet"}


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


def sample_tag(flag, what="climate data"):
    if flag:
        st.markdown(f"<span class='rooted-tag'>SAMPLE {what} — not NASA observations</span>", unsafe_allow_html=True)


def results():
    farm = st.session_state.farm
    scen, _ = load_scenarios()
    return recommend_rotations(farm, scen, farm["weights"]), scen


def dashboard():
    ann, samp = load_climate_annual()
    hero = uri("farm_hero.jpg")
    img = f'<img src="{hero}" alt="Iowa farm field">' if hero else ""
    st.markdown(f"""<div class="rooted-hero-inline">{img}<div class="rooted-hero-overlay">
      <h1>Welcome to ROOTED!</h1><p>NASA-powered agricultural decision support<br>for climate-resilient farming.</p>
      </div></div>""", unsafe_allow_html=True)
    st.write("")
    m = st.columns(3)
    tag = "Sample data" if samp else f"{ann.year.min()}–{ann.year.max()} mean"
    m[0].metric("🌡️ Mean temperature", f"{ann.mean_temp_c.mean():.1f} °C", tag)
    m[1].metric("🌧️ Annual precipitation", f"{ann.precip_mm.mean():.0f} mm", tag)
    m[2].metric("🌿 Annual reference ET", f"{ann.ref_et_mm.mean():.0f} mm", tag)
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
                <div class='rooted-check'><span>✓</span> Compare three-year rotations</div>
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
        st.caption("Values shown are sample placeholders until real NASA POWER data is added to data/processed/.")


def farm_profile():
    title("Farm Profile", "Tell ROOTED about your field. Your inputs and priority weights drive feasibility and scoring.")
    p = st.session_state.farm
    with st.form("farm_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Farm name (optional)", p["farm_name"])
            acres = st.number_input("Field size (acres)", 1, 100000, int(p["acres"]))
            soil = st.selectbox("Soil texture", SOIL, index=SOIL.index(p["soil"]))
            drain = st.selectbox("Drainage class", DRAIN, index=DRAIN.index(p["drainage"]))
            irr = st.selectbox("Irrigation availability", IRRIG, index=IRRIG.index(p["irrigation"]))
        with c2:
            allowed = st.multiselect("Crops you can grow", CROPS, default=p["allowed"])
            cover = st.checkbox("Open to an optional cover-crop practice", value=p["cover_crop_ok"],
                                help="Cover crops depend on planting window, equipment and termination plans.")
            equip = st.text_input("Equipment constraints", p["equipment"])
            notes = st.text_area("Soil notes / soil-test details (optional)", p["soil_notes"])
        st.markdown("**Previous crops (most recent first)**")
        hc = st.columns(3)
        hist = [hc[i].selectbox(f"Year {i+1}", HIST, index=HIST.index(v) if v in HIST else 0, key=f"h{i}")
                for i, v in enumerate(p["crop_history"])]
        st.markdown("**Priorities (0 = ignore, 10 = very important)**")
        w = st.columns(3)
        ws = {"soil": w[0].slider("Soil protection", 0, 10, p["weights"]["soil"]),
              "water": w[1].slider("Water suitability", 0, 10, p["weights"]["water"]),
              "resilience": w[2].slider("Climate resilience", 0, 10, p["weights"]["resilience"])}
        ok = st.form_submit_button("Save Farm Profile", type="primary")
    if ok:
        st.session_state.farm = {**p, "farm_name": name, "acres": acres, "soil": soil, "drainage": drain,
                                 "irrigation": irr, "allowed": allowed, "cover_crop_ok": cover,
                                 "equipment": equip, "soil_notes": notes, "crop_history": hist, "weights": ws}
        st.success("Farm profile saved for this session.")
    st.caption("Soil inputs are farmer-entered or sample values; USDA soil maps may not represent this exact field.")
    with st.expander("Saved profile (JSON)"):
        st.json(st.session_state.farm)


def farm_memory():
    title("Farm Memory", "Historical climate context for the demonstration area.")
    ann, samp = load_climate_annual()
    f = st.session_state.farm
    sample_tag(samp)
    var = st.selectbox("Climate measure", list(VARS))
    col = VARS[var]
    d = ann.dropna(subset=[col])
    if len(d) < len(ann):
        st.caption(f"{len(ann)-len(d)} year(s) with missing values omitted.")
    fig = px.bar(d, x="year", y=col, labels={"year": "Year", col: var}) if col == "p_minus_et_mm" \
        else px.line(d, x="year", y=col, markers=True, labels={"year": "Year", col: var})
    fig.update_traces(marker_color="#2f7d3b") if col == "p_minus_et_mm" else fig.update_traces(line_color="#2f7d3b")
    st.plotly_chart(fig, width="stretch")
    st.caption("P − reference ET is a simplified climate water-balance indicator. It is not measured soil moisture, "
               "crop water demand or irrigation need.")
    a, b = st.columns([1.3, 1])
    with a:
        st.markdown("#### Data provenance")
        st.dataframe(load_provenance(), width="stretch", hide_index=True)
    with b:
        st.markdown("#### Location (approximate)")
        st.map(pd.DataFrame({"lat": [f["lat"]], "lon": [f["lon"]]}), zoom=8)
        st.caption(f"Farm ID {f['farm_id']} · {f['location']}, {f['county']}. NASA POWER is a gridded estimate, not a field measurement.")
    st.download_button("Download climate data (CSV)", ann.to_csv(index=False), "rooted_climate.csv", "text/csv")


def rotation_advisor():
    title("Rotation Advisor", "Feasible three-year rotations ranked by your priorities.")
    res, _ = results()
    f = st.session_state.farm
    if IS_MOCK:
        st.warning("Placeholder scoring engine: rankings are illustrative, not agronomic recommendations.")
    st.caption(f"Farm {f['farm_id']} · {f['acres']} acres · {f['soil']} · {f['drainage']} · {f['irrigation']} · "
               f"weights soil/water/resilience = {f['weights']['soil']}/{f['weights']['water']}/{f['weights']['resilience']}")
    if not res["rotations"]:
        st.error("No feasible rotation with your current crop list and previous crop. Add crops in Farm Profile.")
    for r in res["rotations"][:3]:
        with st.container(border=True):
            st.subheader(f"#{r['rank']} · Rotation {r['rotation_id']}")
            yc = st.columns(3)
            for i, c in enumerate(r["crops_by_year"]):
                yc[i].metric(f"Year {i+1}", c)
            cc = r["cover_crop"]
            if cc:
                st.markdown(f"**Optional cover-crop practice:** {cc['name']} · *{cc['window']}*. {cc['caveat']}")
            else:
                st.markdown("**Optional cover-crop practice:** none shown (not selected, or not suited to this rotation).")
            sc = st.columns(3)
            for col, (k, lab) in zip(sc, [("soil", "Soil protection"), ("water", "Water suitability"), ("resilience", "Climate resilience")]):
                col.caption(f"{lab}: {r['score_components'][k]:.0f}/100")
                col.progress(int(r["score_components"][k]))
            st.write(r["explanation"])
            with st.expander("Limitations"):
                for l in r["limitations"]:
                    st.write("• " + l)
    if res["excluded"]:
        with st.expander("Rotations excluded (infeasible for your inputs)"):
            for e in res["excluded"]:
                st.write(f"**{e['rotation_id']}** {e['crops']}: {e['reason']}")
    st.caption("Scores are modeled suitability, not guaranteed yields, savings, profits or soil improvement.")


def climate_replay():
    title("Climate Replay", "Re-score the same rotations under historical typical, dry and wet conditions.")
    res, scen = results()
    sample_tag(load_scenarios()[1], "scenario data")
    s = st.radio("Choose a scenario", list(SCEN_LABEL), format_func=SCEN_LABEL.get, horizontal=True)
    row = scen[scen.scenario == s].iloc[0]
    st.markdown(f"<div class='rooted-green-card'><h3 style='margin:0'>{row['label']} scenario · {row['growing_season']}</h3>"
                f"<p style='margin:6px 0 0'>{row['description']}</p></div>", unsafe_allow_html=True)
    st.write("")
    m = st.columns(3)
    m[0].metric("Precipitation", f"{row.precip_mm:.0f} mm")
    m[1].metric("Reference ET", f"{row.ref_et_mm:.0f} mm")
    m[2].metric("P − reference ET", f"{row.p_minus_et_mm:.0f} mm")
    rots = res["rotations"][:3]
    if not rots:
        st.error("No feasible rotations. Update your Farm Profile.")
        return
    table = pd.DataFrame([{"Rank": r["scenario_ranks"][s], "Rotation": r["rotation_id"],
                           "Crops": " → ".join(r["crops_by_year"]), "Score": r["scenario_scores"][s],
                           "Regret vs best": r["regret"][s], "Rank in typical": r["scenario_ranks"]["typical"]}
                          for r in rots]).sort_values("Rank")
    st.dataframe(table, width="stretch", hide_index=True)
    moved = [f"{r['rotation_id']}: #{r['scenario_ranks']['typical']} → #{r['scenario_ranks'][s]}"
             for r in rots if r["scenario_ranks"][s] != r["scenario_ranks"]["typical"]]
    st.info("Ranking changes vs typical — " + "; ".join(moved) if moved else "Ranking is the same as under typical conditions.")
    long = pd.DataFrame([{"Rotation": r["rotation_id"], "Scenario": SCEN_LABEL[k], "Score": v}
                         for r in rots for k, v in r["scenario_scores"].items()])
    fig = px.bar(long, x="Rotation", y="Score", color="Scenario", barmode="group",
                 color_discrete_map={"Typical": "#2f7d3b", "Dry": "#c98a1b", "Wet": "#3b7ea6"})
    st.plotly_chart(fig, width="stretch")
    with st.expander("Uncertainty notes", expanded=True):
        st.write("• Replay is a historical stress test, not a forecast of future weather.")
        st.write("• Scenarios come from gridded estimates (NASA POWER), not measurements on one field.")
        st.write("• Scores are modeled suitability/risk; they are not predicted yields, profits or soil change.")
        st.write("• Regret = gap between a rotation's score and the best rotation in that scenario.")
    st.button("Back to Rotation Advisor", on_click=go, args=("Rotation Advisor",))
