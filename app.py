
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ROOTED | The Farm That Remembers",
    page_icon="🌱",
    layout="wide"
)

# --------------------------------------------------
# DEMONSTRATION LOCATION
# --------------------------------------------------

LOCATION = "Ames, Iowa"
COUNTY = "Story County"

# --------------------------------------------------
# MOCK CLIMATE DATA
# Illustrative values only - not NASA observations
# --------------------------------------------------

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

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🌱 ROOTED")
st.subheader("The Farm That Remembers")

st.write(
    "NASA-powered agricultural decision support "
    "for climate-resilient farming."
)

st.divider()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

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

# --------------------------------------------------
# FARM PROFILE
# --------------------------------------------------

if page == "Farm Profile":

    st.title("🌾 Farm Profile")

    st.write(
        "Tell ROOTED about your farm so we can "
        "identify suitable crop rotations and evaluate "
        "climate risks."
    )

    st.divider()

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

    st.subheader("💧 Irrigation Availability")

    irrigation = st.radio(
        "Does this field have irrigation?",
        ["Yes", "No", "Limited"],
        horizontal=True
    )

    st.divider()

    st.subheader("🎯 Farming Priorities")

    col1, col2 = st.columns(2)

    with col1:
        priority_yield = st.checkbox("Maximize crop yield")
        priority_soil = st.checkbox("Improve soil health")

    with col2:
        priority_climate = st.checkbox("Reduce climate risk")
        priority_cost = st.checkbox("Reduce input costs")

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

    if st.button("Save Farm Profile", type="primary"):

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

        st.success("Your farm profile has been saved!")

    if "farm_profile" in st.session_state:

        st.subheader("Your Saved Farm Profile")
        st.json(st.session_state["farm_profile"])


# --------------------------------------------------
# FARM MEMORY
# --------------------------------------------------

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
        "Prototype data: The charts below use illustrative "
        "mock values. They are not actual NASA observations."
    )

    st.divider()

    st.subheader("📅 Climate Overview")

    st.write(
        "The following charts demonstrate how ROOTED will "
        "display historical climate information once the "
        "NASA data connection is integrated."
    )

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_temp = climate_data["Temperature (°C)"].mean()
        st.metric(
            "Average Monthly Temperature",
            f"{avg_temp:.1f} °C"
        )

    with col2:
        total_rain = climate_data["Precipitation (mm)"].sum()
        st.metric(
            "Illustrative Annual Precipitation",
            f"{total_rain:.0f} mm"
        )

    with col3:
        total_et = climate_data["Reference ET₀ (mm)"].sum()
        st.metric(
            "Illustrative Annual ET₀",
            f"{total_et:.0f} mm"
        )

    st.divider()

    # Temperature chart
    st.subheader("🌡️ Monthly Average Temperature")

    temp_chart = px.line(
        climate_data,
        x="Month",
        y="Temperature (°C)",
        markers=True,
        title="Illustrative Monthly Temperature Pattern"
    )

    temp_chart.update_layout(
        xaxis_title="Month",
        yaxis_title="Temperature (°C)"
    )

    st.plotly_chart(
        temp_chart,
        use_container_width=True
    )

    st.divider()

    # Precipitation chart
    st.subheader("🌧️ Monthly Precipitation")

    rain_chart = px.bar(
        climate_data,
        x="Month",
        y="Precipitation (mm)",
        title="Illustrative Monthly Precipitation"
    )

    rain_chart.update_layout(
        xaxis_title="Month",
        yaxis_title="Precipitation (mm)"
    )

    st.plotly_chart(
        rain_chart,
        use_container_width=True
    )

    st.divider()

    # Reference ET chart
    st.subheader("💧 Reference Evapotranspiration (ET₀)")

    et_chart = px.line(
        climate_data,
        x="Month",
        y="Reference ET₀ (mm)",
        markers=True,
        title="Illustrative Monthly Reference ET₀"
    )

    et_chart.update_layout(
        xaxis_title="Month",
        yaxis_title="Reference ET₀ (mm)"
    )

    st.plotly_chart(
        et_chart,
        use_container_width=True
    )

    st.divider()

    # Climate data table
    st.subheader("📊 Climate Data Table")

    st.dataframe(
        climate_data,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# ROTATION ADVISOR PLACEHOLDER
# --------------------------------------------------

elif page == "Rotation Advisor":

    st.title("🌽 Rotation Advisor")

    st.write(
        "ROOTED will compare feasible three-year crop "
        "rotations using your farm profile and climate data."
    )

    st.info(
        "Crop rotation recommendations will be connected "
        "when the recommendation module is ready."
    )

    if "farm_profile" in st.session_state:
        st.success("Farm profile detected!")
        st.json(st.session_state["farm_profile"])
    else:
        st.warning("Please save your Farm Profile first.")


# --------------------------------------------------
# CLIMATE REPLAY PLACEHOLDER
# --------------------------------------------------

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

