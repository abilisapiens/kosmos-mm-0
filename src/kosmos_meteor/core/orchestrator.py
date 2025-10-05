import pandas as pd
from tqdm import tqdm
from pathlib import Path

from ..inputs.case_generator import generate_cases
from ..simulation.entry_model import FragmentCloudModel
from ..simulation.crater_model import CraterModel
from ..simulation.damage_models.local_damage import LocalDamageModel
from ..simulation.damage_models.tsunami import TsunamiModel
from ..simulation.damage_models.global_effects import GlobalEffectsModel
from ..analysis.population import calculate_affected_population
from ..simulation.damage_models.vulnerability_models import VulnerabilityCalculator

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
        self.crm = CraterModel()
        self.local_damage_model = LocalDamageModel()
        self.tsunami_model = TsunamiModel()
        self.global_effects_model = GlobalEffectsModel()
        self.vulnerability = VulnerabilityCalculator()

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
            h_magnitude=self.config.get("h_magnitude", 22.0), 
            density=self.config.get("density", 5000),
            diameter=self.config.get("diameter", 1000),
            speed=self.config.get("speed", 11),
            angle=self.config.get("angle", 8),
            longitude=self.config.get("longitude", 0),
            latitude=self.config.get("latitude", 0)
        )
        print(f"Generated {len(impact_cases)} cases.")

        results = []
        print("\nStep 2: Running simulation for each case...")
        for _, case in tqdm(impact_cases.iterrows(), total=len(impact_cases)):
            # Simulate atmospheric entry
            entry_result = self.fcm.run_entry(case)
            cr_result= self.crm.run_impact_crater_model(case,entry_result)

            # Simulate damage mechanisms
            local_damage = self.local_damage_model.calculate_damage(case, entry_result)
            tsunami_damage = self.tsunami_model.calculate_damage(case, entry_result)
            global_effects = self.global_effects_model.calculate_damage(case, entry_result)
            # Simulate Severity + Vulnerability (by 7 effects + combined)
            vulnerability = self.vulnerability.calculate_all_vulnerabilities(case,entry_result,cr_result)
            # Consolidate results for this case
            case_result = {
                **case.to_dict(),
                **entry_result,
                **cr_result,
                **local_damage,
                **tsunami_damage,
                **global_effects,
                **vulnerability,
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