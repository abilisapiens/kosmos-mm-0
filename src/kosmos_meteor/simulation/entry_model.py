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