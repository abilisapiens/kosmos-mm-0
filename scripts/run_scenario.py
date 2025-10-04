import argparse
import yaml
from pathlib import Path
import sys
import time

# Add the src directory to the Python path to allow importing the pair_model package
# This is a common pattern for running scripts in a project structure like this
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "src"))

#from pair_model.core.orchestrator import Orchestrator
from kosmos_meteor.core.orchestrator import Orchestrator

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