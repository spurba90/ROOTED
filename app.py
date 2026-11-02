from pathlib import Path
import streamlit as st
from src.data_loader import load_farm_profile
from src.ui import pages

st.set_page_config(page_title="ROOTED | Farm Decision Support", page_icon="🌱", layout="wide")
ROOT = Path(__file__).parent
st.markdown(f"<style>{(ROOT/'src'/'ui'/'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "farm" not in st.session_state:
    st.session_state.farm = load_farm_profile()[0]

NAV = [("Dashboard", "⌂"), ("Farm Profile", "🌱"), ("Farm Memory", "▥"), ("Rotation Advisor", "⟳"), ("Climate Replay", "☁")]
with st.sidebar:
    logo = ROOT / "assets" / "rooted_logo.svg"
    if logo.exists():
        st.image(str(logo), width="stretch")
    else:
        st.markdown("<h1 style='color:white;text-align:center'>🌱 ROOTED</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    for label, icon in NAV:
        st.button(f"{icon}  {label}", key=f"nav_{label}", width="stretch", on_click=pages.go, args=(label,),
                  type="primary" if st.session_state.page == label else "secondary")
    st.markdown("<hr>", unsafe_allow_html=True)
    f = st.session_state.farm
    st.markdown(f"<div style='color:white;line-height:1.55;font-size:14px'>📍 <b>Demonstration Area</b><br>"
                f"&nbsp;&nbsp;&nbsp;{f['location']}<br>&nbsp;&nbsp;&nbsp;{f['county']}</div>", unsafe_allow_html=True)

st.markdown("<div class='rooted-topline'>🌱 &nbsp; Smarter Decisions. Healthier Fields.</div>", unsafe_allow_html=True)
{"Dashboard": pages.dashboard, "Farm Profile": pages.farm_profile, "Farm Memory": pages.farm_memory,
 "Rotation Advisor": pages.rotation_advisor, "Climate Replay": pages.climate_replay}[st.session_state.page]()
st.markdown("<div style='text-align:center;color:#829183;font-size:12px;padding:12px'>ROOTED · Ames, Iowa demonstration prototype</div>", unsafe_allow_html=True)
