import pandas as pd
import math
import numpy as np
from scipy.integrate import solve_ivp

class CraterModel:
    """
        Simulates infoarmation at the crater level.    
    """
           
    def run_impact_crater_model(self, case: pd.Series, entry_result: dict)-> dict:  
        """
        Simulate descent of a meteor fragment cloud using Collins pancake model.
        
        Parameters:
        - diameter: initial diameter of impactor (m)
        - density: impactor density (kg/m^3)
        - burst_altitude_km: breakup altitude (km)
        - speed_at_breakup: velocity at breakup (m/s)
        - angle: entry angle from horizontal (degrees)
        - Cd: drag coefficient
        - Ch: heat transfer coefficient
        - Q: heat of ablation (J/kg)
        - rho0: sea-level atmospheric density (kg/m^3)
        - H: scale height of atmosphere (m)
        - pancake_coefficient: max expansion factor (default: 7)
        - expansion_rate: rate of lateral expansion (m/s)
        
        Returns:
        - Final velocity at ground level (m/s)
        - Final diameter of debris cloud at ground level (m)
        - Whether full expansion occurred (bool)
        """
        # Part 1  -Collins pancake
        speed_at_breakup_ms=entry_result.get('speed_at_breakup_ms',0)
        print(entry_result)
        print(f"""speed_at_breakup_ms = {speed_at_breakup_ms}; check not 0""")        
        diameter = case['diameter']
        density=case['density']
        angle_rad=np.radians(case['angle']) # TBC: is it the same as initial angle?? Shouldn't it be changed at breakup?
        breakup_altitude_km=entry_result.get('breakup_altitude_km', 0)
        print(f"""breakup_altitude_km = {breakup_altitude_km}; check not 0""")        

        Cd=2.0
        Ch=0.1
        Q=1e7
        rho0=1.2
        H=8000
        pancake_coefficient=7
        expansion_rate=100

        theta_rad = np.radians(angle_rad)
        h0 = breakup_altitude_km * 1000
        # Initial geometry
        radius0 = diameter / 2
        area0 = np.pi * radius0**2
        area_expanded = pancake_coefficient * area0
        radius_expanded = np.sqrt(area_expanded / np.pi)
        diameter_expanded = 2 * radius_expanded
        volume = (4/3) * np.pi * radius0**3
        mass0 = density * volume
        def deriv(t, y):
            v, m, h = y
            rho = rho0 * np.exp(-h / H)
            dvdt = - (Cd * rho * area_expanded / (2 * m)) * v**2
            dmdt = - (Ch * rho * area_expanded / (2 * Q)) * v**3
            dhdt = -v * np.sin(theta_rad)
            return [dvdt, dmdt, dhdt]
        
        y0 = [speed_at_breakup_ms, mass0, h0]
        t_span = (0, 500)
        sol = solve_ivp(deriv, t_span, y0, method='RK45', dense_output=True,
                        events=lambda t, y: y[2] - 0)
        
        # -- Special from Copilot for the burst_atitude ---
        # Compute energy deposition profile
        altitudes = sol.y[2]
        velocities = sol.y[0]
        masses = sol.y[1]
        kinetic_energies = 0.5 * masses * velocities**2

        # Compute energy loss per meter of altitude
        energy_loss = -np.gradient(kinetic_energies, altitudes)

        # Find altitude of maximum energy deposition (burst altitude)
        max_deposition_index = np.argmax(energy_loss)
        burst_altitude_m = altitudes[max_deposition_index]
        burst_altitude_km = burst_altitude_m / 1000
        speed_at_burst_ms = velocities[max_deposition_index]

        # -- Emd of Special from Copilot for the burst_atitude ---

        speed_at_ground_ms = sol.y[0][-1]
        descent_time = sol.t[-1]

        # Estimate expansion time
        expansion_distance = radius_expanded - radius0
        expansion_time = expansion_distance / expansion_rate

        if descent_time >= expansion_time:
            diameter_ground_m = diameter_expanded
            airburst_bool = True
            burst_altitude_km=burst_altitude_km
            speed_at_burst_ms=speed_at_burst_ms
        else:
            # Partial expansion
            radius_partial = radius0 + expansion_rate * descent_time
            diameter_ground_m = 2 * radius_partial
            airburst_bool = False
            burst_altitude_km=0
            speed_at_burst_ms=  speed_at_ground_ms 

        print(f""""speed_at_burst_ms={speed_at_burst_ms}""")
        print(f""""speed_at_ground_ms={speed_at_ground_ms}""")
        #return {
        #    'speed_at_ground_ms': speed_at_ground_ms,
        #    'diameter_ground_m':diameter_ground_m,
        #    'airburst_bool':airburst_bool
        #}

        """# def run_impact_crater_model(self, case: pd.Series)-> dict:"""
        """# Example usage
            result = impact_crater_model(
            v=20000,         # velocity in m/s
            d=100,           # diameter in meters
            rho_p=3000,      # projectile density in kg/m³
            rho_t=2500,      # target density in kg/m³
            theta_rad=math.radians(45)  # impact angle in radians
        )"""

        # Part 2 - Impact crater model
        v = speed_at_ground_ms
        d = diameter_ground_m
        rho_p = density
        rho_t = 2000    # TBC: to be variablized based on the latatitude longitude
        theta_rad=angle_rad # TBC: same angle t strike ground? YEs pour Abel
        
        # Constants
        g = 9.81    # gravity (m/s²)

        # Step 3: Pi-group scaling for transient crater diameter (D_tr)
        # Equation from Collins et al. (2005):
        k1 = 1.161      # empirical constant for rock targets
        D_tr = k1 * (g**-0.22) * (rho_p / rho_t*math.sin(theta_rad))**0.333 * d**0.78 * v**0.44

        # Step 4: Final crater diameter (D_f)
        # Simple-to-complex transition threshold ~3.2 km
        if D_tr < 3200:
            D_f = 1.25 * D_tr  # simple crater
        else:
            D_f = 1.3 * D_tr**1.13 / 3200**0.13  # complex crater scaling

        # Step 5: Crater depth (approximate)
        depth = D_f * 0.2 if D_f < 4000 else D_f * 0.1

        # Step 6: Ejecta thickness at rim (T_ejecta)
        # From Melosh (1989): T = 0.14 * D_f^0.74 / (1 + (D_f / 1000)^2)
        T_ejecta = 0.14 * D_f**0.74 / (1 + (D_f / 1000)**2)

        # Step 7: Impact energy
        if airburst_bool == True:
            eta = 0.05
        else:
            eta = 0.03
        # Step 6.1: Impactor mass
        volume = (4/3) * math.pi * (d / 2)**3
        mass = rho_p * volume
        # Step 6.2: Impact energy
        impact_energy_j = 0.5 * mass * v**2 # in joules
        impact_energy_kt = impact_energy_j /  4184000000000 # in kt
        return {
            'speed_at_ground_ms': speed_at_ground_ms,
            'diameter_ground_m':diameter_ground_m,
            'airburst_bool':airburst_bool,
            'burst_altitude_km':burst_altitude_km,
            'speed_at_burst_ms': speed_at_burst_ms,
            "transient_crater_diameter_m": round(D_tr, 2),
            "final_crater_diameter_m": round(D_f, 2),
            "crater_depth_m": round(depth, 2),
            "ejecta_thickness_at_rim_m": round(T_ejecta, 2),
            'impact_energy_j':impact_energy_j,
            'impact_energy_kt':impact_energy_kt
        }

