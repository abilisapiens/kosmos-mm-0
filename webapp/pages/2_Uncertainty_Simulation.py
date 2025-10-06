import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# It's better to organize the project with a clear structure
# For example, by adding the project's root directory to Python's path
# This allows for cleaner imports
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from kosmos_meteor.core.orchestrator import Orchestrator

st.set_page_config(page_title="Uncertainty simulation",layout="wide")

st.title("Noob PAIR: Asteroid Impact Risk Simulation (for **Noobs**)")
st.markdown("""
Welcome to the **Probabilistic Asteroid Impact Risk (PAIR)** simulator for **Noobs**. This tool, inspired by NASA's PAIR model, lets you explore the potential consequences of an asteroid impact.       

**Adjust** the **absolute magnitude (H)** on the left to define a scenario, the **number of simulations** then run the simulation to see the results. The **visualizations** will help you understand the **range of possible outcomes and the different hazards involved**.
""")

with st.expander(f"ℹ️The H parameters - Intuitions", expanded=False):
    st.markdown("""
    # 💡 Understanding *H* — The Absolute Magnitude of an Asteroid

    ### 🪐 **What Is H?**

    In asteroid science, **H** (called the *absolute magnitude*) is a measure of how bright an asteroid would appear if it were:

    * **1 astronomical unit (AU)** from both the Sun and the Earth, and
    * fully illuminated (i.e., at **zero phase angle** — Sun, asteroid, and Earth perfectly aligned).

    It’s a **standardized measure of intrinsic brightness**, allowing astronomers to compare asteroids of different distances and lighting conditions.

    ---

    ### 🧠 **Intuitive Meaning**

    You can think of **H** as the asteroid’s **built-in brightness**, like a “lumen rating” of a cosmic flashlight — it tells us how much light the asteroid reflects if distance and geometry weren’t factors.

    * A **lower H** → brighter asteroid (usually larger or more reflective).
    * A **higher H** → dimmer asteroid (smaller or darker surface).

    ---

    ### ⚙️ **Relationship to Size**

    H alone doesn’t tell us the asteroid’s exact size — because brightness also depends on **albedo (reflectivity)**.
    However, we can estimate the diameter ( D ) (in kilometers) using:

    [
    D = \frac{1329}{\sqrt{p_V}} \times 10^{-H/5}
    ]

    where:

    * ( p_V ) = albedo (how reflective the surface is),
    * ( H ) = absolute magnitude.

    **Example:**

    * If two asteroids have the same H, but one has a darker surface (lower albedo), it must be **larger** to reflect the same brightness.

    ---

    ### 🔭 **Typical Ranges**

    | Object Type     | Typical H | Approx. Size (if albedo ≈ 0.15) |
    | --------------- | --------- | ------------------------------- |
    | Large asteroid  | 10        | ~40 km                          |
    | Medium asteroid | 20        | ~500 m                          |
    | Small NEO       | 25        | ~50 m                           |
    | Tiny fragment   | 30        | ~10 m                           |

    ---

    ### 🌍 **Why It Matters**

    * Used to **estimate asteroid diameters** when only optical data is available.
    * Key input for **impact energy** and **risk models** like **NASA PAIR** and **Sentry**.
    * Helps prioritize which NEOs to monitor closely (since smaller dim ones are harder to detect early).

    ---

    ### 🧾 **In short**

    > **H is the asteroid’s intrinsic brightness — a proxy for size and reflectivity, normalized for distance.**
    > It’s how astronomers turn *light into insight* about these distant rocks.

    """)

with st.expander(f"ℹ️📡 Original NASA PAIR - Intuitions", expanded=False):
    st.markdown("""
    # ☄️ NASA PAIR Model — Probabilistic Asteroid Impact Risk

    Focus on the **problem it solves**, the **intuition** behind how it works, and why it’s important. 
                           
    ### 🧩 **The Problem**

    Predicting whether an asteroid will impact Earth — and how severe that impact could be — is an extremely complex challenge.
    Asteroids are tracked using telescopes over short observation windows, leading to **uncertainty** in their orbital paths.
    Even a tiny error in position or velocity can result in a large difference in where the object is decades later.

    Traditional deterministic models (using a single “best-fit” orbit) **cannot capture the full range of possible futures** for such uncertain trajectories.
    That’s where NASA's **PAIR** comes in.

    ---

    ### 🧠 **The Intuition Behind PAIR**

    The **Probabilistic Asteroid Impact Risk (PAIR)** model developed by **NASA’s CNEOS** combines:

    1. **Asteroid Orbit Uncertainty (from Sentry or NEO databases)**
    2. **Monte Carlo or covariance-based orbit propagation**
    3. **Impact probability and consequence estimation**

    Think of it as a *cloud of possible asteroid paths* instead of one single line.
    PAIR simulates **thousands of potential future orbits** within the range of measurement uncertainties, then tracks how many of those paths intersect Earth’s position.

    Each simulated trajectory contributes to:

    * The **impact probability** (how likely it is to hit Earth),
    * The **impact location distribution** (where on Earth it might hit), **--> !!! NOT DONE !!!**
    * The **impact energy** (how severe it would be if it does).

    ---

    ### ⚙️ **Conceptual Flow**

    1. **Start with orbital elements** (from NASA’s Sentry/NEO data).
    2. **Quantify uncertainty** — small variations in orbital parameters based on observation errors.
    3. **Propagate forward** using orbital mechanics (numerical integration).
    4. **Count intersections** with Earth’s position and time window.
    5. **Estimate impact risk** as
    [
    \text{Risk} = \text{Impact Probability} \times \text{Expected Consequence (Energy, Damage)}
    ]
    6. Optionally, visualize as a **risk corridor** — the region on Earth most likely to experience impact.

    ---

    ### 🌍 **Why It Matters**

    * Helps prioritize **potentially hazardous asteroids (PHAs)** for observation and tracking.
    * Enables **early warning** and **risk communication** with clear uncertainty ranges.
    * Supports **mission design** for possible deflection or mitigation strategies.

    ---

    ### 📖 **In Short**

    PAIR turns uncertain asteroid data into **probabilistic impact maps** — giving us not only the “if” but the “how likely” and “how bad” of possible asteroid impacts.

    """)

st.sidebar.header("Scenario Configuration")
st.sidebar.write("Define the parameters for the hypothetical asteroid.")

h_magnitude = st.sidebar.slider(
    "Absolute Magnitude (H)",
    min_value=15.0,
    max_value=30.0,
    value=22.0,
    step=0.5,
    help="A measure of the asteroid's intrinsic brightness. Lower values mean a larger object."
)

num_cases = st.sidebar.select_slider(
    "Number of Monte Carlo Cases",
    options=[100, 500, 1000, 5000, 10000],
    value=1000,
    help="The number of simulations to run. More cases give better statistics but take longer."
)

# In-memory cache for simulation results
@st.cache_data
def run_cached_simulation(config):
    """Runs the simulation and caches the result."""
    orchestrator = Orchestrator(config)
    results_df = orchestrator.run_simulation()
    return results_df

if st.sidebar.button("Run Simulation"):
    scenario_config = {
        "h_magnitude": h_magnitude,
        "num_cases": num_cases,
        "distance_km": 0,
    }
    with st.spinner(f"Running {num_cases} simulations..."):
        results_df = run_cached_simulation(scenario_config)
        st.session_state['results_df'] = results_df
        st.success("Simulation complete!")

if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']
    st.header("Simulation Results")

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    mean_diameter = results_df['diameter_m'].mean()
    mean_energy = results_df['impact_energy_mt'].mean()
    mean_max_affected_pop = results_df['max_affected_population'].mean()
    max_max_affected_pop = results_df['max_affected_population'].max()    
    col1.metric("Mean Diameter (m)", f"{mean_diameter:.2f}")
    col2.metric("Mean Impact Energy (MT)", f"{mean_energy:.2f}")
    col3.metric("Mean Max Affected Population", f"{int(mean_max_affected_pop):,}")
    col4.metric("Max Max Affected Population", f"{int(max_max_affected_pop):,}")    

    # Display "wow" visualization
    st.subheader("Impact Energy vs. Affected Population")
    fig_wow = px.scatter(
        results_df,
        x="impact_energy_mt",
        y="max_affected_population",
        size="diameter_m",
        color="strength_mpa",
        hover_name=results_df.index,
        #log_x=True,
        #log_y=True,
        title="Each bubble represents a simulated impact scenario",
        labels={
            "impact_energy_mt": "Impact Energy (Megatons) - Log Scale",
            "max_affected_population": "Max Affected Population - Log Scale",
            "diameter_m": "Diameter (m)",
            "strength_mpa": "Strength (MPa)"
        },
        color_continuous_scale=px.colors.sequential.Plasma,
        size_max=60
    )
    st.plotly_chart(fig_wow, use_container_width=True)
    st.markdown("""
    This plot visualizes the relationship between impact energy and the number of people affected. Each bubble is a single simulation.
    - **Size of the bubble**: Represents the asteroid's diameter.
    - **Color**: Indicates the asteroid's strength (darker is weaker).
    - **Axes**: Both are on a logarithmic scale to show the vast range of possibilities.
    """)

    # Display plots
    st.subheader("Distribution of Key Parameters")
    fig1 = px.histogram(
        results_df,
        x="diameter_m",
        title="Distribution of Asteroid Diameters",
        labels={'diameter_m': 'Diameter (m)'}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Use log scale for energy and population as they span orders of magnitude
    fig2 = px.histogram(
        results_df,
        x="impact_energy_mt",
        #log_x=True,
        title="Distribution of Impact Energy",
        labels={'impact_energy_mt': 'Impact Energy (Megatons)'}
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(
        results_df[results_df['max_affected_population'] > 1],
        x="max_affected_population",
        #log_x=True,
        title="Distribution of Affected Population",
        labels={'max_affected_population': 'Maximum Affected Population'}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Raw Results Data")
    st.dataframe(results_df)


else:
    st.info("Configure a scenario in the sidebar and click 'Run Simulation' to begin.")