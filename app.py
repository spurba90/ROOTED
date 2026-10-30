
import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# ROOTED - THE FARM THAT REMEMBERS
# Application / UI
# Demonstration Area: Ames, Iowa
# ==================================================

# PAGE CONFIGURATION
st.set_page_config(
    page_title="ROOTED | The Farm That Remembers",
    page_icon="🌱",
    layout="wide"
)

# ==================================================
# DEMONSTRATION LOCATION
# ==================================================

LOCATION = "Ames, Iowa"
COUNTY = "Story County"

# ==================================================
# MOCK CLIMATE DATA
# Illustrative values only - NOT NASA observations
# ==================================================

climate_data = pd.DataFrame({
    "Month": [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ],
    "Temperature (°C)": [
        -5, -3, 3, 10, 16, 21,
        23, 22, 17, 10, 3, -3
    ],
    "Precipitation (mm)": [
        25, 28, 55, 95, 115, 125,
        110, 105, 85, 65, 45, 30
    ],
    "Reference ET₀ (mm)": [
        8, 14, 35, 65, 105, 130,
        145, 125, 85, 45, 18, 8
    ]
})

# ==================================================
# HEADER
# ==================================================

st.title("🌱 ROOTED")
st.subheader("The Farm That Remembers")

st.write(
    "NASA-powered agricultural decision support "
    "for climate-resilient farming."
)

st.divider()

# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("🌱 ROOTED Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Farm Profile",
        "Farm Memory",
        "Rotation Advisor",
        "Climate Replay"
    ]
)

st.sidebar.divider()

st.sidebar.caption("Demonstration Area")
st.sidebar.write("📍 Ames, Iowa")
st.sidebar.write("Story County")

# ==================================================
# PAGE 1: FARM PROFILE
# ==================================================

if page == "Farm Profile":

    st.title("🌾 Farm Profile")

    st.write(
        "Tell ROOTED about your farm so we can identify "
        "suitable crop rotations and evaluate climate risks."
    )

    st.divider()

    # FARM LOCATION
    st.subheader("📍 Farm Location")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "City",
            value="Ames",
            disabled=True
        )

        st.text_input(
            "County",
            value="Story County",
            disabled=True
        )

    with col2:

        farm_name = st.text_input(
            "Farm Name (optional)",
            placeholder="Enter your farm name"
        )

        field_acres = st.number_input(
            "Field Size (acres)",
            min_value=0.1,
            value=40.0,
            step=1.0
        )

    st.divider()

    # SOIL INFORMATION
    st.subheader("🌱 Soil Information")

    soil_type = st.selectbox(
        "Primary Soil Type",
        [
            "Not sure",
            "Loam",
            "Sandy Loam",
            "Clay",
            "Silty Clay Loam",
            "Silt Loam",
            "Other"
        ]
    )

    st.divider()

    # PREVIOUS CROP
    st.subheader("🚜 Previous Crop History")

    previous_crop = st.selectbox(
        "Which crop was grown in this field last year?",
        [
            "Corn",
            "Soybeans",
            "Oats",
            "Wheat",
            "Alfalfa",
            "Other",
            "Not sure"
        ]
    )

    st.divider()

    # IRRIGATION
    st.subheader("💧 Irrigation Availability")

    irrigation = st.radio(
        "Does this field have irrigation?",
        ["Yes", "No", "Limited"],
        horizontal=True
    )

    st.divider()

    # FARMING PRIORITIES
    st.subheader("🎯 Farming Priorities")

    col1, col2 = st.columns(2)

    with col1:

        priority_yield = st.checkbox(
            "Maximize crop yield"
        )

        priority_soil = st.checkbox(
            "Improve soil health"
        )

    with col2:

        priority_climate = st.checkbox(
            "Reduce climate risk"
        )

        priority_cost = st.checkbox(
            "Reduce input costs"
        )

    priorities = []

    if priority_yield:
        priorities.append("Maximize crop yield")

    if priority_soil:
        priorities.append("Improve soil health")

    if priority_climate:
        priorities.append("Reduce climate risk")

    if priority_cost:
        priorities.append("Reduce input costs")

    st.divider()

    # SAVE FARM PROFILE
    if st.button(
        "Save Farm Profile",
        type="primary"
    ):

        st.session_state["farm_profile"] = {
            "farm_name": farm_name,
            "location": LOCATION,
            "county": COUNTY,
            "field_acres": field_acres,
            "soil_type": soil_type,
            "previous_crop": previous_crop,
            "irrigation": irrigation,
            "priorities": priorities
        }

        st.success(
            "Your farm profile has been saved!"
        )

    # DISPLAY SAVED PROFILE
    if "farm_profile" in st.session_state:

        st.subheader("Your Saved Farm Profile")

        st.json(
            st.session_state["farm_profile"]
        )


# ==================================================
# PAGE 2: FARM MEMORY
# ==================================================

elif page == "Farm Memory":

    st.title("🌎 Farm Memory")

    st.write(
        "Explore historical climate patterns for the "
        "ROOTED demonstration area in Ames, Iowa."
    )

    st.info(
        "📍 Location: Ames, Story County, Iowa"
    )

    st.warning(
        "Prototype data: The climate values shown here "
        "are illustrative mock values, not actual NASA observations."
    )

    st.divider()

    st.subheader("📅 Climate Overview")

    st.write(
        "Explore monthly temperature, precipitation, "
        "and reference evapotranspiration patterns."
    )

    # CLIMATE SUMMARY METRICS
    col1, col2, col3 = st.columns(3)

    with col1:

        avg_temp = climate_data[
            "Temperature (°C)"
        ].mean()

        st.metric(
            "Average Monthly Temperature",
            f"{avg_temp:.1f} °C"
        )

    with col2:

        total_rain = climate_data[
            "Precipitation (mm)"
        ].sum()

        st.metric(
            "Illustrative Annual Precipitation",
            f"{total_rain:.0f} mm"
        )

    with col3:

        total_et = climate_data[
            "Reference ET₀ (mm)"
        ].sum()

        st.metric(
            "Illustrative Annual ET₀",
            f"{total_et:.0f} mm"
        )

    st.divider()

    # INTERACTIVE CLIMATE EXPLORER
    st.subheader("📊 Explore Climate Patterns")

    metric = st.selectbox(
        "Choose a climate variable",
        [
            "Temperature (°C)",
            "Precipitation (mm)",
            "Reference ET₀ (mm)"
        ]
    )

    chart = px.line(
        climate_data,
        x="Month",
        y=metric,
        markers=True,
        title=f"Monthly {metric} — Ames, Iowa"
    )

    chart.update_layout(
        xaxis_title="Month",
        yaxis_title=metric
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )

    st.divider()

    # CLIMATE DATA TABLE
    st.subheader("Climate Data Table")

    st.dataframe(
        climate_data,
        use_container_width=True,
        hide_index=True
    )

    # CSV DOWNLOAD
    csv_data = climate_data.to_csv(
        index=False
    )

    st.download_button(
        label="Download Climate Data (CSV)",
        data=csv_data,
        file_name="ames_iowa_mock_climate_data.csv",
        mime="text/csv"
    )

    st.caption(
        "Source: ROOTED prototype mock dataset. "
        "NASA data integration is pending."
    )


# ==================================================
# PAGE 3: ROTATION ADVISOR
# ==================================================

elif page == "Rotation Advisor":

    st.title("🌽 Rotation Advisor")

    st.write(
        "Compare possible three-year crop rotations "
        "for your farm in Ames, Iowa."
    )

    # CHECK FOR SAVED FARM PROFILE
    if "farm_profile" not in st.session_state:

        st.warning(
            "Please complete and save your Farm Profile first."
        )

    else:

        profile = st.session_state["farm_profile"]

        st.success(
            f"Using your saved profile: "
            f"{profile['field_acres']} acres in "
            f"{profile['county']}"
        )

        st.caption(
            "The rotations below are illustrative examples. "
            "Final feasibility and rankings will come from "
            "the crop recommendation rules."
        )

        # SAMPLE ROTATION OPTIONS
        rotations = [

            {
                "name": "Rotation A",
                "crops": [
                    "Corn",
                    "Soybeans",
                    "Oats"
                ],
                "focus": "Crop diversity",
                "benefits": [
                    "Includes three different crops",
                    "Provides a break from continuous corn"
                ],
                "tradeoffs": [
                    "Requires planning for different crop needs"
                ]
            },

            {
                "name": "Rotation B",
                "crops": [
                    "Soybeans",
                    "Corn",
                    "Soybeans"
                ],
                "focus": "Corn-soybean system",
                "benefits": [
                    "Uses familiar Iowa crop options",
                    "Includes a crop break before corn"
                ],
                "tradeoffs": [
                    "Less crop diversity than a three-crop rotation"
                ]
            },

            {
                "name": "Rotation C",
                "crops": [
                    "Oats",
                    "Corn",
                    "Soybeans"
                ],
                "focus": "Diversified sequence",
                "benefits": [
                    "Introduces a small-grain crop",
                    "Offers a different crop sequence"
                ],
                "tradeoffs": [
                    "May require different equipment or market planning"
                ]
            }
        ]

        st.divider()

        st.subheader(
            "Compare Three-Year Rotations"
        )

        cols = st.columns(3)

        # DISPLAY ROTATION CARDS
        for i, rotation in enumerate(rotations):

            with cols[i]:

                with st.container(border=True):

                    st.subheader(
                        rotation["name"]
                    )

                    st.caption(
                        rotation["focus"]
                    )

                    for year, crop in enumerate(
                        rotation["crops"],
                        start=1
                    ):

                        st.write(
                            f"**Year {year}:** {crop}"
                        )

                    st.divider()

                    st.markdown(
                        "**Potential benefits**"
                    )

                    for benefit in rotation["benefits"]:

                        st.write(
                            f"✓ {benefit}"
                        )

                    st.markdown(
                        "**Trade-offs to consider**"
                    )

                    for tradeoff in rotation["tradeoffs"]:

                        st.write(
                            f"• {tradeoff}"
                        )

        st.divider()

        # FARM PROFILE SUMMARY
        st.subheader(
            "Farm Profile Used"
        )

        st.write(
            f"**Previous crop:** {profile['previous_crop']}"
        )

        st.write(
            f"**Soil type:** {profile['soil_type']}"
        )

        st.write(
            f"**Irrigation:** {profile['irrigation']}"
        )

        if profile["priorities"]:

            st.write(
                "**Farmer priorities:** "
                + ", ".join(profile["priorities"])
            )

        else:

            st.write(
                "No farming priorities selected yet."
            )

        st.info(
            "These example rotations are not yet scored or "
            "validated against the farm's soil and climate. "
            "The recommendation engine will be integrated next."
        )


# ==================================================
# PAGE 4: CLIMATE REPLAY
# ==================================================

elif page == "Climate Replay":

    st.title("🌦️ Climate Replay")

    st.write(
        "Explore how historical dry, typical, and wet "
        "conditions could affect crop rotation decisions."
    )

    st.info(
        "Historical climate scenario comparisons will be "
        "added in the next development stage."
    )

    st.write(
        "Future functionality will include:"
    )

    st.markdown(
        """
        - Historical dry-year scenarios
        - Typical climate-year scenarios
        - Historical wet-year scenarios
        - Crop rotation comparison under different conditions
        - Changes in recommendation rankings
        """
    )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "ROOTED | The Farm That Remembers | "
    "Ames, Iowa Demonstration Prototype"
)
