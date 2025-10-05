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

from src.kosmos_meteor.core.orchestrator import Orchestrator

st.set_page_config(layout="wide")

st.title("PyPAIR: Asteroid Impact Risk Simulation")
st.markdown("""
Welcome to the **Probabilistic Asteroid Impact Risk (PAIR)** simulator. This tool, inspired by NASA's PAIR model, lets you explore the potential consequences of an asteroid impact. 

**Adjust the parameters on the left to define a scenario, then run the simulation to see the results.** The visualizations will help you understand the range of possible outcomes and the different hazards involved.
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