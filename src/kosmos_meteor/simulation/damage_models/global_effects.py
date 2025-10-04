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