# Project Structure

The `PyPAIR` project is organized into a modular structure to promote clarity, maintainability, and extensibility. Here is a breakdown of the key directories and their roles.

-   **`data/`**: Contains all data used by the model.
    -   `external/`: Raw, downloaded data like population grids (e.g., GPWv4) or coastal elevation maps.
    -   `processed/`: Data converted into efficient formats for the model, such as Height-of-Burst (HOB) maps stored as NumPy arrays.

-   **`docs/`**: Project documentation source files for MkDocs.

-   **`notebooks/`**: Jupyter notebooks for demonstration and analysis.
    -   `full_simulation_demo.ipynb`: A comprehensive walkthrough designed to run on Google Colab, showcasing an end-to-end simulation and reproducing key figures from the paper.

-   **`scripts/`**: Standalone Python scripts for command-line operations.
    -   `run_scenario.py`: The main entry point for running simulations from the terminal. It parses a configuration file to define the scenario.
    -   `preprocess_data.py`: A utility script to convert data from `data/external` to `data/processed`.

-   **`src/pair_model/`**: The core source code of the simulation library.
    -   **`inputs/`**: Modules for generating simulation inputs.
        -   `asteroid_properties.py`: Implements the Asteroid Property Inference Network (APIN) logic to sample physically plausible asteroid properties (diameter, density, etc.) from statistical distributions.
        -   `orbital_parameters.py`: Reads and parses trajectory data, typically from files formatted like those from CNEOS.
        -   `case_generator.py`: Creates the full set of Monte Carlo cases by combining asteroid properties and orbital parameters.

    -   **`simulation/`**: Modules containing the core physics models.
        -   `entry_model.py`: Implements the Fragment-Cloud Model (FCM) to simulate atmospheric entry, breakup, and energy deposition, yielding an effective burst altitude and surface impact energy.
        -   `damage_models/`: A package for all hazard models.
            -   `local_damage.py`: Calculates damage from blast (using HOB maps) and thermal radiation.
            -   `tsunami.py`: Models tsunami generation, propagation, and coastal run-up.
            -   `global_effects.py`: Estimates the fraction of the world population affected by global-scale climatic disruption based on impact energy.

    -   **`analysis/`**: Modules for processing and interpreting simulation results.
        -   `population.py`: Calculates the number of people affected by intersecting damage footprints with gridded population data.
        -   `risk_assessment.py`: Aggregates results from all cases to compute statistical products like CCDFs and probability histograms.
        -   `mapping.py`: Generates geospatial files (KML, GeoJSON) for visualizing risk swaths and damage areas.

    -   **`core/`**: The central orchestrator that connects all the pieces.
        -   `orchestrator.py`: A primary class that manages the entire simulation workflow: initializing inputs, running cases through the simulation models in parallel, and passing results to the analysis modules.

    -   **`utils/`**: Utility functions and shared resources.
        -   `constants.py`: Defines physical constants (e.g., Earth's radius) and model parameters.
        -   `data_io.py`: Functions for efficiently saving and loading large datasets (e.g., using HDF5 or Zarr).
        -   `geometry.py`: Helper functions for geometric operations.

-   **`webapp/`**: The Streamlit web application for interactive visualization.
