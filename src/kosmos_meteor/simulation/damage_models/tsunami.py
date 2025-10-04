# placeholder

import numpy as np
import pandas as pd

class TsunamiModel:
    """Estimates tsunami damage"""

    def calculate_damage(self, case: pd.Series, entry_result: dict) -> dict:
        """Calculates blast and thermal damage radii.

        Args:
            case (pd.Series): The impact case data.
            entry_result (dict): The results from the atmospheric entry simulation.

        Returns:
            dict: A dictionary of damage radii for different thresholds.
        """
        #blast_radii = self._calculate_blast(case, entry_result)
        #thermal_radii = self._calculate_thermal(case, entry_result)
        #return {**blast_radii, **thermal_radii}
        return {'tsunami_runup_m':0}