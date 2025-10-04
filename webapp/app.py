import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#from pair_model.core.orchestrator import Orchestrator
from kosmos_meteor.core.orchestrator import Orchestrator

st.set_page_config(layout="wide")

st.title("Kosmos Meteor - PyPAIR: Asteroid Impact Risk Simulation")

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
    }
    with st.spinner(f"Running {num_cases} simulations..."):
        results_df = run_cached_simulation(scenario_config)
        st.session_state['results_df'] = results_df
        st.success("Simulation complete!")

if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']
    st.header("Simulation Results")

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    mean_diameter = results_df['diameter_m'].mean()
    mean_energy = results_df['impact_energy_mt'].mean()
    mean_affected_pop = results_df['max_affected_population'].mean()
    col1.metric("Mean Diameter (m)", f"{mean_diameter:.2f}")
    col2.metric("Mean Impact Energy (MT)", f"{mean_energy:.2f}")
    col3.metric("Mean Affected Population", f"{int(mean_affected_pop):,}")

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
        title="Distribution of Affected Population", # (Log Scale)",
        labels={'max_affected_population': 'Maximum Affected Population'}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Raw Results Data")
    st.dataframe(results_df)

else:
    st.info("Configure a scenario in the sidebar and click 'Run Simulation' to begin.")