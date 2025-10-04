# PAIR

**Table of Contents**
- [Design](#design)
- [Implementation](#implementation)
- [Follow-up](#follow-up)

# Design

Based on the detailed research paper "Risk assessment for asteroid impact threat scenarios" by Wheeler et al. (2024), here is a proposal for a modular Python project designed for academic use, collaboration, and extensibility.

This proposal outlines the project structure, data flow, library choices, and documentation, adhering to modern Python development best practices.

### 1. Project High-Level Overview

The project, tentatively named **`PyPAIR`** (Python Probabilistic Asteroid Impact Risk), will be a Python implementation of the PAIR model described in the paper. It will be a modular toolkit allowing researchers and students to simulate asteroid impact scenarios, analyze risks, and visualize outcomes. The architecture is designed to be extensible, allowing for the substitution or enhancement of physics models as research evolves.

### 2. Project Management with `uv`

The project will use `uv` for dependency management and virtual environments, ensuring fast and reproducible setups.

**To set up the project:**
1.  Install `uv`: `pip install uv`
2.  Create the virtual environment: `uv venv`
3.  Activate the environment: `source .venv/bin/activate`
4.  Install dependencies: `uv pip install -e .[all]`

### 3. Proposed Project Structure

A modular structure separates concerns, making the codebase easier to understand, maintain, and contribute to.

```
PyPAIR/
├── .venv/                      # Virtual environment managed by uv
├── data/
│   ├── external/               # Raw external data (e.g., population grids)
│   └── processed/              # Processed data (e.g., HOB maps as .npy)
├── docs/
│   ├── index.md                # MkDocs homepage
│   ├── project_structure.md    # Explanation of the project structure
│   ├── data_flow.md            # Explanation of the data pipeline
│   └── ...                     # Other documentation pages (API, tutorials)
├── notebooks/
│   └── full_simulation_demo.ipynb # Colab-friendly notebook for a full run
├── scripts/
│   ├── run_scenario.py         # Example script to run a full scenario from CLI
│   └── preprocess_data.py      # Script to process raw data into usable formats
├── src/
│   └── pair_model/
│       ├── __init__.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── population.py   # Calculate affected population
│       │   ├── risk_assessment.py # Generate CCDFs, histograms, stats
│       │   └── mapping.py      # Generate KML/GeoJSON for risk swaths
│       ├── core/
│       │   ├── __init__.py
│       │   └── orchestrator.py # Main class to run the full simulation pipeline
│       ├── inputs/
│       │   ├── __init__.py
│       │   ├── asteroid_properties.py # APIN-like property generation
│       │   ├── case_generator.py # Combine properties and orbits
│       │   └── orbital_parameters.py # Process CNEOS-like trajectory files
│       ├── simulation/
│       │   ├── __init__.py
│       │   ├── entry_model.py  # Fragment-Cloud Model (FCM) for atmospheric entry
│       │   └── damage_models/
│       │       ├── __init__.py
│       │       ├── base_damage_model.py # Abstract base class for damage models
│       │       ├── local_damage.py # Blast and Thermal models
│       │       ├── tsunami.py      # Tsunami inundation model
│       │       └── global_effects.py # Global climate effects model
│       └── utils/
│           ├── __init__.py
│           ├── constants.py    # Physical and model constants
│           ├── data_io.py      # Helpers for loading/saving data (HDF5, etc.)
│           └── geometry.py     # Geometric calculations (e.g., footprint shapes)
├── webapp/
│   └── app.py                  # Streamlit web application
├── pyproject.toml              # Project metadata and dependencies for uv
├── mkdocs.yml                  # MkDocs configuration
└── README.md                   # Project overview and setup instructions
```

### 4. Key Documentation Files

Good documentation is critical for an academic project. Here is the proposed content for the main markdown files.

---

#### **`README.md`**

```markdown
# PyPAIR: A Python Model for Probabilistic Asteroid Impact Risk Assessment

**PyPAIR** is an open-source Python implementation of the Probabilistic Asteroid Impact Risk (PAIR) model, as detailed in the paper *Risk assessment for asteroid impact threat scenarios* (Wheeler et al., 2024). This project aims to provide a modular and extensible framework for simulating asteroid impact events and quantifying their potential consequences.

## Features

-   **Modular Architecture**: Easily swap, modify, or add new physics models for entry, damage, and risk analysis.
-   **Probabilistic Simulation**: Run millions of Monte Carlo cases based on uncertain asteroid properties and trajectories.
-   **Comprehensive Damage Modeling**: Includes models for local blast/thermal damage, tsunami inundation, and global climatic effects.
-   **Advanced Risk Analysis**: Generate key metrics like affected population histograms, damage exceedance probabilities (CCDFs), and risk breakdowns by hazard.
-   **Geospatial Visualization**: Create damage risk swaths and footprints as KML files for visualization in Google Earth.

## Getting Started

### Installation

This project uses `uv` for fast and reliable dependency management.

1.  **Install uv**:
    ```bash
    pip install uv
    ```

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/PyPAIR.git
    cd PyPAIR
    ```

3.  **Create virtual environment and install dependencies**:
    ```bash
    # Create the virtual environment
    uv venv

    # Activate the environment (on Linux/macOS)
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate

    # Install the project in editable mode with all optional dependencies
    uv pip install -e .[all]
    ```

### Running a Simulation

You can run a pre-defined scenario using the example script:

```bash
python scripts/run_scenario.py --config-file path/to/scenario_config.yml
```

### Launching the Web App

To explore results interactively, launch the Streamlit web app:

```bash
streamlit run webapp/app.py
```

## Documentation

Detailed documentation, including API references and tutorials, is generated using MkDocs and hosted on GitHub Pages. To build it locally:

```bash
mkdocs serve
```

---
```

#### **`docs/project_structure.md`**

```markdown
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
```

---

#### **`docs/data_flow.md`**

```markdown
# Data Flow and Modeling Pipeline

The `PyPAIR` simulation follows a sequential, modular pipeline that transforms initial uncertainties into final risk products. This flow is managed by the `Orchestrator` class in `src/pair_model/core/orchestrator.py`.

```mermaid
graph TD
    subgraph "1. Input Generation"
        A[Scenario Definition <br/> e.g., H-magnitude, Orbit File] --> B(Asteroid Properties <br/> `asteroid_properties.py`);
        A --> C(Orbital Parameters <br/> `orbital_parameters.py`);
        B & C --> D{Case Generator <br/> `case_generator.py`};
        D --> E[Monte Carlo Cases <br/> (DataFrame / HDF5 file)];
    end

    subgraph "2. Simulation"
        E --> F{Orchestrator <br/> `orchestrator.py`};
        F --> G(Atmospheric Entry <br/> `entry_model.py`);
        G --> H{Damage Models};
        H --> H_Local(Local Damage <br/> `local_damage.py`);
        H --> H_Tsunami(Tsunami <br/> `tsunami.py`);
        H --> H_Global(Global Effects <br/> `global_effects.py`);
    end

    subgraph "3. Analysis & Output"
        H_Local & H_Tsunami & H_Global --> I[Raw Damage Results <br/> (Radii, Energy, etc.)];
        I --> J(Affected Population <br/> `population.py`);
        J --> K{Risk Assessment <br/> `risk_assessment.py`};
        K --> L[Risk Statistics <br/> (CCDFs, Histograms)];
        J --> M{Mapping <br/> `mapping.py`};
        M --> N[Geospatial Outputs <br/> (KML/GeoJSON)];
    end

    style E fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#ccf,stroke:#333,stroke-width:2px
    style N fill:#ccf,stroke:#333,stroke-width:2px
```

1.  **Input Generation**:
    -   The process starts with high-level scenario parameters (e.g., an asteroid's absolute magnitude `H` and a file of possible trajectories).
    -   The **`AsteroidPropertyGenerator`** samples millions of property sets (diameter, density, strength, etc.) based on statistical distributions described in the paper.
    -   The **`OrbitalParameters`** module loads the entry points (latitude, longitude, velocity, angle).
    -   The **`CaseGenerator`** combines these into a comprehensive set of unique impact cases, which are stored efficiently (e.g., in a Pandas DataFrame or an HDF5 file).

2.  **Simulation**:
    -   The **`Orchestrator`** iterates through each case. For performance, this step should be parallelized.
    -   For each case, the **`entry_model`** (FCM) is called to calculate the atmospheric breakup, determining the effective burst altitude and any remaining surface impact energy.
    -   Based on the entry results, the relevant **`damage_models`** are invoked to calculate the extent of each hazard (e.g., blast radius, thermal radius, tsunami run-up height).

3.  **Analysis and Output**:
    -   The raw damage results (e.g., damage radii) are passed to the **`population`** module, which uses gridded population data to estimate the number of people affected for each hazard and severity level.
    -   The **`risk_assessment`** module aggregates the "affected population" data from all cases to generate the final statistical products: probability distributions, exceedance curves (CCDFs), and summary tables.
    -   The **`mapping`** module uses the damage footprints from all cases to compute and export geospatial files, such as a KML file showing the 95th percentile damage risk swath.
```

---

### 5. `pyproject.toml` Configuration

This file defines project metadata and dependencies for `uv`.

```toml
[project]
name = "pair_model"
version = "0.1.0"
description = "A Python model for Probabilistic Asteroid Impact Risk assessment."
authors = [{ name = "Your Name", email = "your.email@example.com" }]
readme = "README.md"
requires-python = ">=3.10"
license = { file = "LICENSE" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Astronomy",
]

# Core dependencies required for the simulation
dependencies = [
    "numpy",
    "scipy",
    "pandas",
    "xarray",
    "h5py",          # For efficient storage of large datasets
    "numba",         # For accelerating critical numerical functions
    "tqdm",          # For progress bars
]

[project.optional-dependencies]
# Dependencies for visualization and webapp
viz = [
    "matplotlib",
    "seaborn",
    "plotly",
    "streamlit",
    "folium",
    "streamlit-folium",
    "simplekml",     # For generating KML files
]

# Dependencies for building documentation
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
    "pymdown-extensions",
]

# A single group to install everything
all = [
    "pair_model[viz]",
    "pair_model[docs]",
]

[project.urls]
Homepage = "https://github.com/your-username/PyPAIR"
Repository = "https://github.com/your-username/PyPAIR"

[tool.uv.sources]
# You can add private package indexes here if needed
# my-index = { url = "https://my-index.com/simple" }

[tool.setuptools.packages.find]
where = ["src"]
```

This comprehensive project proposal provides a solid foundation for developing a high-quality, maintainable, and collaborative academic software project that faithfully models the research presented in the paper.

# Implementation

Here is a comprehensive implementation of the `PyPAIR` project structure. This includes the complete directory layout and starter code for all key modules. The Python code is functional, with clear placeholders (`NotImplementedError` or simplified logic) where complex physics or data processing is required.

This implementation is designed to be a robust starting point for your academic project.

### Project Files and Code

Below are the contents for each file in the `PyPAIR` project structure.

---
### **`pyproject.toml`**

This file manages the project's metadata and dependencies using `uv`.

```toml
[project]
name = "pair_model"
version = "0.1.0"
description = "A Python model for Probabilistic Asteroid Impact Risk assessment."
authors = [{ name = "Academic Project Contributor", email = "contributor@example.com" }]
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Astronomy",
]

# Core dependencies required for the simulation
dependencies = [
    "numpy",
    "scipy",
    "pandas",
    "xarray",          # For handling gridded data like population maps
    "h5py",            # For efficient storage of large datasets
    "numba",           # For accelerating critical numerical functions
    "tqdm",            # For progress bars
    "pathlib",
]

[project.optional-dependencies]
# Dependencies for visualization and webapp
viz = [
    "matplotlib",
    "seaborn",
    "plotly",
    "streamlit",
    "folium",
    "streamlit-folium",
    "simplekml",     # For generating KML files
]

# Dependencies for building documentation
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
    "pymdown-extensions",
    "mkdocs-mermaid2-plugin",
]

# A single group to install everything
all = [
    "pair_model[viz]",
    "pair_model[docs]",
]

[project.urls]
Homepage = "https://github.com/your-username/PyPAIR"
Repository = "https://github.com/your-username/PyPAIR"

[tool.setuptools.packages.find]
where = ["src"]
```

---
### **`README.md`**

```markdown
# PyPAIR: A Python Model for Probabilistic Asteroid Impact Risk Assessment

**PyPAIR** is an open-source Python implementation of the Probabilistic Asteroid Impact Risk (PAIR) model, as detailed in the paper *Risk assessment for asteroid impact threat scenarios* (Wheeler et al., 2024). This project aims to provide a modular and extensible framework for simulating asteroid impact events and quantifying their potential consequences.

## Features

-   **Modular Architecture**: Easily swap, modify, or add new physics models for entry, damage, and risk analysis.
-   **Probabilistic Simulation**: Run Monte Carlo cases based on uncertain asteroid properties and trajectories.
-   **Comprehensive Damage Modeling**: Includes models for local blast/thermal damage, tsunami inundation, and global climatic effects.
-   **Advanced Risk Analysis**: Generate key metrics like affected population histograms, damage exceedance probabilities (CCDFs), and risk breakdowns by hazard.
-   **Geospatial Visualization**: Create damage risk swaths and footprints as KML files for visualization in Google Earth.

## Getting Started

### Installation

This project uses `uv` for fast and reliable dependency management.

1.  **Install uv**:
    ```bash
    pip install uv
    ```

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/PyPAIR.git
    cd PyPAIR
    ```

3.  **Create virtual environment and install dependencies**:
    ```bash
    # Create the virtual environment
    uv venv

    # Activate the environment (on Linux/macOS)
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate

    # Install the project in editable mode with all optional dependencies
    uv pip install -e .[all]
    ```

### Running a Simulation

You can run a pre-defined scenario using the example script:

```bash
# This script is a placeholder and needs to be developed
python scripts/run_scenario.py --config-file path/to/scenario_config.yml
```

### Launching the Web App

To explore results interactively, launch the Streamlit web app:

```bash
streamlit run webapp/app.py
```

## Documentation

Detailed documentation, including API references and tutorials, is generated using MkDocs and hosted on GitHub Pages. To build it locally:

1.  **Install documentation dependencies** (if not already installed with `.[all]`):
    ```bash
    uv pip install -e .[docs]
    ```
2.  **Serve the documentation**:
    ```bash
    mkdocs serve
    ```
    Navigate to `http://127.0.0.1:8000` in your browser.
```

---
### **`mkdocs.yml`**

```yaml
site_name: PyPAIR Documentation
theme:
  name: material
  features:
    - navigation.tabs
    - content.code.annotate
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - mermaid2
  - mkdocstrings:
      handlers:
        python:
          options:
            show_root_heading: yes
            docstring_style: google

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.arithmatex:
      generic: true

nav:
  - Home: index.md
  - Project Structure: project_structure.md
  - Data Flow: data_flow.md
  - API Reference:
    - Core: api/core.md
    - Simulation: api/simulation.md
```

---
### **`docs/index.md`**

```markdown
# Welcome to PyPAIR

**PyPAIR** is an open-source Python framework for Probabilistic Asteroid Impact Risk (PAIR) assessment.

This documentation provides a guide to the project's structure, data flow, and API. Use the navigation to explore the different sections.
```

---
### **`docs/project_structure.md`**

(Content as provided in the previous response)

---
### **`docs/data_flow.md`**

(Content as provided in the previous response)

---
### **`src/pair_model/core/orchestrator.py`**

```python
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from ..inputs.case_generator import generate_cases
from ..simulation.entry_model import FragmentCloudModel
from ..simulation.damage_models.local_damage import LocalDamageModel
from ..simulation.damage_models.tsunami import TsunamiModel
from ..simulation.damage_models.global_effects import GlobalEffectsModel
from ..analysis.population import calculate_affected_population

class Orchestrator:
    """Manages the end-to-end execution of a PAIR simulation scenario.

    This class coordinates the entire workflow, from generating input cases to
    running simulations and performing post-analysis.
    """

    def __init__(self, scenario_config: dict):
        """Initializes the Orchestrator with a scenario configuration.

        Args:
            scenario_config (dict): A dictionary containing all parameters
                needed for the simulation, such as file paths, model settings,
                and scenario constraints (e.g., H magnitude).
        """
        self.config = scenario_config
        self.project_root = Path(__file__).resolve().parents[3]

        # Initialize models
        self.fcm = FragmentCloudModel()
        self.local_damage_model = LocalDamageModel()
        self.tsunami_model = TsunamiModel()
        self.global_effects_model = GlobalEffectsModel()

    def run_simulation(self) -> pd.DataFrame:
        """Executes the full simulation pipeline.

        The pipeline consists of:
        1. Generating Monte Carlo cases.
        2. Iterating through each case to simulate entry and damage.
        3. Calculating the affected population for each case.
        4. Aggregating and returning the results.

        Returns:
            pd.DataFrame: A DataFrame containing the results for every
                simulated case, including inputs and all calculated outputs.
        """
        print("Step 1: Generating impact cases...")
        impact_cases = generate_cases(
            num_cases=self.config.get("num_cases", 1000),
            h_magnitude=self.config.get("h_magnitude", 22.0)
        )
        print(f"Generated {len(impact_cases)} cases.")

        results = []
        print("\nStep 2: Running simulation for each case...")
        for _, case in tqdm(impact_cases.iterrows(), total=len(impact_cases)):
            # Simulate atmospheric entry
            entry_result = self.fcm.run_entry(case)

            # Simulate damage mechanisms
            local_damage = self.local_damage_model.calculate_damage(case, entry_result)
            tsunami_damage = self.tsunami_model.calculate_damage(case, entry_result)
            global_effects = self.global_effects_model.calculate_damage(case, entry_result)

            # Consolidate results for this case
            case_result = {
                **case.to_dict(),
                **entry_result,
                **local_damage,
                **tsunami_damage,
                **global_effects,
            }

            # Step 3: Calculate affected population
            # This is a simplified placeholder. A real implementation would need
            # gridded population data and geospatial intersection logic.
            case_result['affected_population_local'] = calculate_affected_population(
                damage_footprint=case_result['blast_radius_1psi_km']
            )
            case_result['affected_population_tsunami'] = calculate_affected_population(
                damage_footprint=case_result['tsunami_runup_m']
            )
            case_result['affected_population_global'] = (
                case_result['global_effects_fraction'] * 7.8e9  # Approx world pop
            )

            # Determine the single largest hazard
            case_result['max_affected_population'] = max(
                case_result['affected_population_local'],
                case_result['affected_population_tsunami'],
                case_result['affected_population_global']
            )
            results.append(case_result)

        print("\nStep 4: Aggregating results.")
        results_df = pd.DataFrame(results)
        return results_df
```

---
### **`src/pair_model/inputs/case_generator.py`**

```python
import pandas as pd
from .asteroid_properties import AsteroidPropertyGenerator
from .orbital_parameters import load_orbital_data

def generate_cases(num_cases: int, h_magnitude: float) -> pd.DataFrame:
    """Generates a full set of Monte Carlo impact cases.

    This function combines probabilistically sampled asteroid properties with
    sampled orbital trajectory parameters to create a comprehensive DataFrame
    of unique impact scenarios to be simulated.

    Args:
        num_cases (int): The total number of impact cases to generate.
        h_magnitude (float): The absolute magnitude (H) of the asteroid,
            used as a constraint for property generation.

    Returns:
        pd.DataFrame: A DataFrame where each row represents a unique impact
            case with all necessary input parameters.
    """
    # 1. Generate asteroid properties
    prop_generator = AsteroidPropertyGenerator(h_magnitude)
    properties_df = prop_generator.sample_properties(num_cases)

    # 2. Load orbital parameters
    # In a real scenario, this would load a file with many trajectory points.
    # Here, we create a sample DataFrame for demonstration.
    orbital_df = load_orbital_data(num_samples=num_cases)

    # 3. Combine them
    # For simplicity, we'll just concatenate them side-by-side.
    # A more complex approach might involve pairing each property set with
    # each orbit point, creating a much larger number of cases.
    if len(properties_df) != len(orbital_df):
        raise ValueError("Property and orbital samples must have the same length for this simple combination.")

    impact_cases_df = pd.concat([properties_df, orbital_df], axis=1)

    # Calculate initial impact energy (in Megatons of TNT)
    # E = 0.5 * m * v^2
    # 1 MT = 4.184e15 Joules
    mass_kg = impact_cases_df['mass_kg']
    velocity_mps = impact_cases_df['entry_velocity_kms'] * 1000
    energy_joules = 0.5 * mass_kg * velocity_mps**2
    impact_cases_df['impact_energy_mt'] = energy_joules / 4.184e15

    return impact_cases_df
```

---
### **`src/pair_model/inputs/asteroid_properties.py`**

```python
import numpy as np
import pandas as pd

class AsteroidPropertyGenerator:
    """Generates physically plausible asteroid properties based on statistical distributions.

    This class mimics the Asteroid Property Inference Network (APIN) described
    in the paper, sampling properties like diameter, density, and strength
    while considering correlations between them.
    """
    def __init__(self, h_magnitude: float):
        """Initializes the generator with a constraint.

        Args:
            h_magnitude (float): The asteroid's absolute magnitude (H), which
                constrains the possible size range.
        """
        self.h_magnitude = h_magnitude

    def sample_properties(self, n_samples: int) -> pd.DataFrame:
        """Samples a set of asteroid properties.

        This is a simplified implementation. A real model would involve more
        complex, correlated distributions as described in the paper.

        Args:
            n_samples (int): The number of property sets to generate.

        Returns:
            pd.DataFrame: A DataFrame containing the sampled properties.
        """
        # Albedo (log-uniform distribution)
        albedo = np.random.uniform(0.02, 0.5, n_samples)

        # Diameter (derived from H and albedo)
        # D = 1329 / sqrt(albedo) * 10^(-0.2 * H)
        diameter_km = (1329 / np.sqrt(albedo)) * (10**(-0.2 * self.h_magnitude))
        diameter_m = diameter_km * 1000

        # Density (bimodal distribution for stony vs. iron could be used)
        # Simplified uniform distribution for now.
        density_kg_m3 = np.random.uniform(1500, 7000, n_samples)

        # Mass (from diameter and density)
        volume_m3 = (4/3) * np.pi * (diameter_m / 2)**3
        mass_kg = density_kg_m3 * volume_m3

        # Aerodynamic Strength (log-uniform)
        strength_mpa = 10**np.random.uniform(-1, 1, n_samples) # 0.1 to 10 MPa

        df = pd.DataFrame({
            'h_magnitude': self.h_magnitude,
            'albedo': albedo,
            'diameter_m': diameter_m,
            'density_kg_m3': density_kg_m3,
            'mass_kg': mass_kg,
            'strength_mpa': strength_mpa,
        })
        return df
```

---
### **`src/pair_model/inputs/orbital_parameters.py`**

```python
import numpy as np
import pandas as pd

def load_orbital_data(filepath: str = None, num_samples: int = 1000) -> pd.DataFrame:
    """Loads or generates sample orbital entry parameters.

    In a real scenario, this would parse a standard format file from CNEOS/JPL.
    Here, we generate random data for demonstration.

    Args:
        filepath (str, optional): Path to the orbital data file. If None,
            random data is generated.
        num_samples (int): Number of samples to generate if no file is provided.

    Returns:
        pd.DataFrame: DataFrame with orbital entry parameters for each case.
    """
    if filepath:
        # Placeholder for reading a real file (e.g., CSV)
        # return pd.read_csv(filepath)
        raise NotImplementedError("File parsing is not yet implemented.")
    else:
        # Generate synthetic data
        latitude = np.random.uniform(-90, 90, num_samples)
        longitude = np.random.uniform(-180, 180, num_samples)
        entry_angle_deg = np.random.uniform(15, 75, num_samples) # Relative to horizontal
        entry_velocity_kms = np.random.uniform(11, 25, num_samples)

        df = pd.DataFrame({
            'latitude': latitude,
            'longitude': longitude,
            'entry_angle_deg': entry_angle_deg,
            'entry_velocity_kms': entry_velocity_kms,
        })
        return df
```

---
### **`src/pair_model/simulation/entry_model.py`**

```python
import pandas as pd

class FragmentCloudModel:
    """Simulates atmospheric entry and breakup of an asteroid.

    This is a simplified placeholder for the full Fragment-Cloud Model (FCM).
    A real implementation would solve differential equations of motion,
    ablation, and fragmentation.
    """
    def run_entry(self, case: pd.Series) -> dict:
        """Calculates the effective burst altitude and surface impact energy.

        Args:
            case (pd.Series): A row from the impact cases DataFrame containing
                all input parameters for a single case.

        Returns:
            dict: A dictionary with key results like 'burst_altitude_km' and
                'surface_impact_energy_mt'.
        """
        # Simplified logic: smaller/weaker objects burst higher,
        # larger/stronger objects burst lower or impact.
        strength = case['strength_mpa']
        diameter = case['diameter_m']
        impact_energy = case['impact_energy_mt']

        # Heuristic for burst altitude
        if diameter > 500 or strength > 5:  # Large or strong object
            burst_altitude_km = 0
            surface_impact_energy_mt = impact_energy
        else:
            # Weaker objects burst higher
            burst_altitude_km = max(0, 40 - (strength * 4) - (diameter / 10))
            surface_impact_energy_mt = 0 # Assume full airburst

        return {
            'burst_altitude_km': burst_altitude_km,
            'surface_impact_energy_mt': surface_impact_energy_mt
        }
```

---
### **`src/pair_model/simulation/damage_models/local_damage.py`**

```python
import numpy as np
import pandas as pd

class LocalDamageModel:
    """Estimates local ground damage from blast overpressure and thermal radiation."""

    def calculate_damage(self, case: pd.Series, entry_result: dict) -> dict:
        """Calculates blast and thermal damage radii.

        Args:
            case (pd.Series): The impact case data.
            entry_result (dict): The results from the atmospheric entry simulation.

        Returns:
            dict: A dictionary of damage radii for different thresholds.
        """
        blast_radii = self._calculate_blast(case, entry_result)
        thermal_radii = self._calculate_thermal(case, entry_result)
        return {**blast_radii, **thermal_radii}

    def _calculate_blast(self, case: pd.Series, entry_result: dict) -> dict:
        """Calculates blast damage radii using a simplified scaling law.

        A real implementation would use interpolated Height-of-Burst (HOB) maps.
        This uses a simple energy scaling law for a ground burst.
        R = C * Y^(1/3), where Y is yield in kT.
        """
        yield_kt = case['impact_energy_mt'] * 1000

        # Scaling constants (highly approximate)
        # These would be derived from HOB curves based on burst altitude
        c_1psi = 1.5 # km/kt^(1/3)
        c_4psi = 0.6 # km/kt^(1/3)

        radius_1psi = c_1psi * (yield_kt ** (1/3))
        radius_4psi = c_4psi * (yield_kt ** (1/3))

        return {
            'blast_radius_1psi_km': radius_1psi,
            'blast_radius_4psi_km': radius_4psi,
        }

    def _calculate_thermal(self, case: pd.Series, entry_result: dict) -> dict:
        """Calculates thermal damage radii.

        This is a placeholder. The model from the paper is more complex,
        involving luminous efficiency and exposure duration.
        """
        yield_mt = case['impact_energy_mt']
        # Simplified: thermal damage is often smaller than blast for many sizes
        thermal_radius_3rd_degree_burns = 0.5 * (yield_mt * 1000)**(1/3)

        return {
            'thermal_radius_3rd_degree_burns_km': thermal_radius_3rd_degree_burns
        }
```

---
### **Other `damage_models`**

The other damage models (`tsunami.py`, `global_effects.py`) would follow a similar structure. Here's a brief implementation for `global_effects.py` based on the paper's description.

#### **`src/pair_model/simulation/damage_models/global_effects.py`**

```python
import numpy as np
import pandas as pd

class GlobalEffectsModel:
    """Estimates global climatic effects from large impacts."""

    def calculate_damage(self, case: pd.Series, entry_result: dict) -> dict:
        """Calculates the fraction of world population affected.

        This implements the exponential curve fit described in Figure 6 of the
        Wheeler et al. (2024) paper.

        Args:
            case (pd.Series): The impact case data.
            entry_result (dict): The results from the atmospheric entry simulation.

        Returns:
            dict: A dictionary containing 'global_effects_fraction'.
        """
        energy_gt = case['impact_energy_mt'] / 1000  # Convert MT to Gigatons
        fraction = 0.0

        # Threshold from paper is ~40 Gt
        if energy_gt > 40:
            # These are approximate fits to the curves in Figure 6
            # log10(E_gt)
            log_e = np.log10(energy_gt)

            # Simplified linear fit in log-space for the "nominal" curve
            # This should be replaced with a proper fit from the paper's data
            # f = a * log_e + b
            # At 100 Gt (log_e=2), fraction is small. At 10,000 Gt (log_e=4), it's ~0.5
            if log_e > 2:
                fraction = min(1.0, 0.25 * (log_e - 2))

        return {'global_effects_fraction': fraction}
```

---
### **`src/pair_model/analysis/population.py`**

```python
import numpy as np

def calculate_affected_population(damage_footprint: float, pop_density: float = 15.21) -> float:
    """Estimates the number of people affected within a damage footprint.

    This is a highly simplified function that assumes a circular damage area
    and a uniform global average population density. A real implementation
    must use gridded population data (e.g., from an xarray DataSet) and
    perform a geospatial intersection.

    Args:
        damage_footprint (float): The characteristic size of the damage area.
            Can be a radius in km (for local damage) or another metric.
        pop_density (float): The population density in people per square km.
            Defaults to the global average from the paper.

    Returns:
        float: The estimated number of people affected.
    """
    if damage_footprint <= 0 or np.isnan(damage_footprint):
        return 0.0

    # Assume the footprint is a radius in km for this example
    area_km2 = np.pi * damage_footprint**2
    return area_km2 * pop_density
```

---
### **`webapp/app.py`**

This is a basic Streamlit app to demonstrate how results could be visualized.

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from pair_model.core.orchestrator import Orchestrator

st.set_page_config(layout="wide")

st.title("PyPAIR: Asteroid Impact Risk Simulation")

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
        log_x=True,
        title="Distribution of Impact Energy",
        labels={'impact_energy_mt': 'Impact Energy (Megatons)'}
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(
        results_df[results_df['max_affected_population'] > 1],
        x="max_affected_population",
        log_x=True,
        title="Distribution of Affected Population (Log Scale)",
        labels={'max_affected_population': 'Maximum Affected Population'}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Raw Results Data")
    st.dataframe(results_df)

else:
    st.info("Configure a scenario in the sidebar and click 'Run Simulation' to begin.")
```

# Follow-up

## run_scenario.py

Here is a complete implementation for `scripts/run_scenario.py`.

This script serves as the command-line interface (CLI) for the `PyPAIR` model. It is designed to be robust and user-friendly, using `argparse` for argument handling and `PyYAML` for configuration management.

First, we need to add `pyyaml` to our project's dependencies, as it's essential for this script.

### 1. Update `pyproject.toml`

Add `pyyaml` to the core `dependencies` list.

```toml
[project]
name = "pair_model"
version = "0.1.0"
description = "A Python model for Probabilistic Asteroid Impact Risk assessment."
authors = [{ name = "Academic Project Contributor", email = "contributor@example.com" }]
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Astronomy",
]

# Core dependencies required for the simulation
dependencies = [
    "numpy",
    "scipy",
    "pandas",
    "xarray",
    "h5py",
    "numba",
    "tqdm",
    "pathlib",
    "pyyaml",  # <-- Add this line
]

[project.optional-dependencies]
# Dependencies for visualization and webapp
viz = [
    "matplotlib",
    "seaborn",
    "plotly",
    "streamlit",
    "folium",
    "streamlit-folium",
    "simplekml",
]

# Dependencies for building documentation
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
    "pymdown-extensions",
    "mkdocs-mermaid2-plugin",
]

# A single group to install everything
all = [
    "pair_model[viz]",
    "pair_model[docs]",
]

[project.urls]
Homepage = "https://github.com/your-username/PyPAIR"
Repository = "https://github.com/your-username/PyPAIR"

[tool.setuptools.packages.find]
where = ["src"]
```

---

### 2. Create `scripts/run_scenario.py`

This script will parse command-line arguments, load a scenario configuration from a YAML file, run the simulation via the `Orchestrator`, and save the results to a CSV file.

```python
import argparse
import yaml
from pathlib import Path
import sys
import time

# Add the src directory to the Python path to allow importing the pair_model package
# This is a common pattern for running scripts in a project structure like this
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "src"))

from pair_model.core.orchestrator import Orchestrator

def main():
    """
    Main function to run the PAIR simulation from the command line.

    This script orchestrates the following steps:
    1. Parses command-line arguments for configuration and output files.
    2. Loads the scenario parameters from the specified YAML config file.
    3. Initializes and runs the simulation using the Orchestrator.
    4. Saves the resulting DataFrame to a specified CSV file.
    5. Prints a summary of the simulation results to the console.
    """
    parser = argparse.ArgumentParser(
        description="Run a Probabilistic Asteroid Impact Risk (PAIR) simulation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        required=True,
        help="Path to the YAML scenario configuration file."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Path to save the output results CSV file."
    )
    args = parser.parse_args()

    # --- 1. Load Scenario Configuration ---
    try:
        with open(args.config, 'r') as f:
            scenario_config = yaml.safe_load(f)
        print(f"✅ Successfully loaded scenario config from: {args.config}")
        print("   --- Scenario Parameters ---")
        for key, value in scenario_config.items():
            print(f"   - {key}: {value}")
        print("   -------------------------\n")
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found at {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error: Could not parse YAML configuration file: {e}")
        sys.exit(1)

    # --- 2. Run the Simulation ---
    print("🚀 Initializing simulation...")
    start_time = time.time()
    
    orchestrator = Orchestrator(scenario_config)
    results_df = orchestrator.run_simulation()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n✅ Simulation completed in {duration:.2f} seconds.")

    # --- 3. Save Results ---
    try:
        # Ensure the output directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(args.output, index=False)
        print(f"💾 Results saved to: {args.output}")
    except Exception as e:
        print(f"❌ Error: Failed to save results to {args.output}. Reason: {e}")
        sys.exit(1)

    # --- 4. Print Summary ---
    print("\n--- 📊 Run Summary ---")
    mean_diameter = results_df['diameter_m'].mean()
    mean_energy = results_df['impact_energy_mt'].mean()
    mean_affected_pop = results_df['max_affected_population'].mean()
    max_affected_pop = results_df['max_affected_population'].max()
    
    print(f"  Number of cases run: {len(results_df):,}")
    print(f"  Mean Asteroid Diameter: {mean_diameter:.2f} m")
    print(f"  Mean Impact Energy: {mean_energy:.2f} MT")
    print(f"  Mean Affected Population: {int(mean_affected_pop):,}")
    print(f"  Maximum Affected Population: {int(max_affected_pop):,}")
    print("-----------------------\n")


if __name__ == "__main__":
    main()
```

---

### 3. Create an Example Configuration File

For the script to be useful, users need an example of the YAML configuration file it expects. Let's create one in the `scripts` directory.

#### `scripts/scenario_config.yml`

```yaml
# -----------------------------------------------------------------------------
# Example Scenario Configuration for PyPAIR
# -----------------------------------------------------------------------------
# This file defines the input parameters for a single simulation run.
# It is used by the `scripts/run_scenario.py` script.
# -----------------------------------------------------------------------------

# num_cases: The total number of Monte Carlo simulations to run.
# Higher numbers provide better statistical accuracy but take longer to compute.
num_cases: 1000

# h_magnitude: The absolute magnitude of the hypothetical asteroid.
# This value is a primary constraint on the asteroid's size.
# A lower H magnitude corresponds to a larger, brighter object.
# Common values for exercises range from 15 (very large) to 30 (very small).
h_magnitude: 22.0

# --- Future parameters could be added here ---
# For example, you could specify paths to orbital data files,
# or flags to turn certain physics models on or off.

# orbital_data_file: "path/to/cneos_data.txt"
# enable_tsunami_model: true
```

### How to Use the Script

1.  **Make sure dependencies are installed**:
    ```bash
    # Run this once after cloning/pulling
    uv pip install -e .[all]
    ```

2.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

3.  **Run the simulation from the project's root directory**:
    ```bash
    python scripts/run_scenario.py --config scripts/scenario_config.yml --output results/run_1.csv
    ```

    This command will:
    *   Read the parameters from `scripts/scenario_config.yml`.
    *   Run 1,000 simulation cases.
    *   Create a `results` directory if it doesn't exist.
    *   Save the output data to `results/run_1.csv`.
    *   Print progress and a final summary to your terminal.

This setup provides a powerful and flexible way to execute and manage your simulations from the command line, which is essential for batch processing, scripting, and reproducibility in an academic context.