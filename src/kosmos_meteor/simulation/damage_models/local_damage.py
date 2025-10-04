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