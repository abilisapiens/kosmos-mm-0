import pandas as pd
import math
import numpy as np
from scipy.integrate import solve_ivp

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
        # speed=30000;density=5000;diameter=300;angle=np.radians(90)
        #from math import *
        # Simplified logic: smaller/weaker objects burst higher,
        # larger/stronger objects burst lower or impact.
        speed = case['speed']*1000
        diameter = case['diameter']
        density=case['density']
        angle=np.radians(case['angle'])

        #variables calculees
        E = np.pi/12*diameter**3*density*speed**2

        #z in km#
        def vi(z):
            vi_ms=speed*math.exp(-3*p(z)*2*8/(4*density*diameter*math.sin(angle)))
            return(vi_ms)  # Speed in ms
              
        def p(z):
                b=math.exp(-z/8)
                return(b)
        #Pressure on the impactor#
        def Y(z):
            P = p(z)*vi(z)**2
            return(P)

        #Yield strength : minimal force that must be used to have it undergo plastic changes --> valid for density of 1000-8000 kg.m**-3#
        Ym_strength = 10**(2.107+0.0624*math.sqrt(density))
        #break up altitude#
        If_value = 4.07*2*8*Ym_strength/(density*diameter*speed**2*math.sin(angle))
        if If_value<1:
            burst_altitude_km = -8*(math.log(Ym_strength/speed**2) + 1.308 - 0.314*If_value -1.303*math.sqrt(1-If_value))
            speed_at_breakup_ms=vi(burst_altitude_km)
        else:
            burst_altitude_km = 0
            speed_at_breakup=0        

        return {
            'burst_altitude_km': burst_altitude_km,
            'speed_at_breakup_ms':speed_at_breakup_ms
        }
        
 