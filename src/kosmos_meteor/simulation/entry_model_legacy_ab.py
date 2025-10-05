import pandas as pd
import math
import numpy as np
from scipy.integrate import solve_ivp

class FragmentCloudModel_ab:
    """Simulates atmospheric entry and breakup of an asteroid.

    This is a simplified placeholder for the full Fragment-Cloud Model (FCM).
    A real implementation would solve differential equations of motion,
    ablation, and fragmentation.
    """
    def run_entry_ab(self, case: pd.Series) -> dict:
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
            bb=speed*math.exp(-3*p(z)*2*8/(4*density*diameter*math.sin(angle)))
            return(bb)  
              
        def airburst_model():
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
        else:
            burst_altitude_km = 0
        
        return {
            'burst_altitude_km': burst_altitude_km
        }
        
    
    def _collins_pancake_descent(diameter, density, burst_altitude_km, v0, angle_deg,
                                Cd=2.0, Ch=0.1, Q=1e7, rho0=1.2, H=8000,
                                pancake_coefficient=7, expansion_rate=100):  
        """
        Simulate descent of a meteor fragment cloud using Collins pancake model.
        
        Parameters:
        - diameter: initial diameter of impactor (m)
        - density: impactor density (kg/m^3)
        - burst_altitude_km: breakup altitude (km)
        - v0: velocity at breakup (m/s)
        - angle_deg: entry angle from horizontal (degrees)
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
        theta_rad = np.radians(angle_deg)
        h0 = burst_altitude_km * 1000
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
        
        y0 = [v0, mass0, h0]
        t_span = (0, 500)
        sol = solve_ivp(deriv, t_span, y0, method='RK45', dense_output=True,
                        events=lambda t, y: y[2] - 0)
        
        v_final = sol.y[0][-1]
        descent_time = sol.t[-1]

        # Estimate expansion time
        expansion_distance = radius_expanded - radius0
        expansion_time = expansion_distance / expansion_rate

        if descent_time >= expansion_time:
            diameter_ground = diameter_expanded
            airburst = True
        else:
            # Partial expansion
            radius_partial = radius0 + expansion_rate * descent_time
            diameter_ground = 2 * radius_partial
            airburst = False

        return v_final,     diameter_ground,     airburst


    def impact_crater_model(v, d, rho_p, rho_t, theta_rad):
        # Constants
        g = 9.81  # gravity (m/s²)

        # Step 3: Pi-group scaling for transient crater diameter (D_tr)
        # Equation from Collins et al. (2005):
        # D_tr = k1 * (g^-0.22) * (rho_p/rho_t)^0.333 * d^0.78 * v_vertical^0.44
        k1 = 1.161  # empirical constant for rock targets
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

        return {
            "Transient Crater Diameter (m)": round(D_tr, 2),
            "Final Crater Diameter (m)": round(D_f, 2),
            "Crater Depth (m)": round(depth, 2),
            "Ejecta Thickness at Rim (m)": round(T_ejecta, 2),
        }

    """# Example usage
    result = impact_crater_model(
        v=20000,         # velocity in m/s
        d=100,           # diameter in meters
        rho_p=3000,      # projectile density in kg/m³
        rho_t=2500,      # target density in kg/m³
        theta_rad=math.radians(45)  # impact angle in radians
        )
    #for key, value in result.items():
        print(f"{key}: {value}")"""
    
    #attention airburst true or false corresponds to data sent by fully expanded fo function impact#
    def thermal_radiation_model(v, d, rho, R, airburst):
        """
        Computes thermal radiation at a given distance from a meteor impact or airburst.
        Based on Collins et al. (2005) scaling laws.

        Parameters:
        v        : impact velocity (m/s)
        d        : impactor diameter (m)
        rho      : impactor density (kg/m³)
        R        : distance from impact site or airburst center (m)
        eta      : luminous efficiency (default 0.003)
        airburst : boolean flag indicating if the event is an airburst

        Returns:
        dict with impact energy, thermal energy, fireball radius, and thermal dose at R
        """
        if airburst == True:
            eta = 0.05
        else:
            eta = 0.03
        # Step 1: Impactor mass
        volume = (4/3) * math.pi * (d / 2)**3
        mass = rho * volume

        # Step 2: Impact energy
        E_impact = 0.5 * mass * v**2

        # Step 3: Thermal energy
        E_thermal = eta * E_impact

        # Step 4: Fireball radius (yield scaling)
        # Airbursts typically have larger fireballs due to atmospheric expansion
        k = 0.13 if airburst else 0.05
        R_fireball = k * E_thermal**(1/3)

        # Step 5: Thermal flux at distance R
        flux = E_thermal / (2 * math.pi * R**2)

        # Step 6: Thermal dose (J/m²)
        dose = flux  # assuming instantaneous release

        return {
            "Impactor Mass (kg)": round(mass, 2),
            "Impact Energy (J)": round(E_impact, 2),
            "Thermal Energy (J)": round(E_thermal, 2),
            "Fireball Radius (m)": round(R_fireball, 2),
            "Thermal Dose at Distance R (J/m²)": round(dose, 2),
            "Event Type": "Airburst" if airburst else "Surface Impact"
        }

    """# Example usage
    result = thermal_radiation_model(
        v=20000,       # velocity in m/s
        d=50,          # diameter in meters
        rho=3000,      # density in kg/m³
        R=10000,       # distance in meters
        airburst=True  # toggle for airburst scenario
    )

    for key, value in result.items():
        print(f"{key}: {value}")"""


    def seismic_model_collins(v, d, rho, R, epsilon=1e-3):
        """
        Simulates seismic effects of a meteor impact using Collins et al. (2005) equations.
        
        Parameters:
        v       : impact velocity (m/s)
        d       : impactor diameter (m)
        rho     : impactor density (kg/m³)
        R       : distance from impact site (m)
        epsilon : seismic efficiency (default 0.001)
        
        Returns:
        dict with impact energy, seismic energy, magnitude, and Mercalli intensity
        """
        # Step 1: Impactor mass
        volume = (4/3) * math.pi * (d / 2)**3
        mass = rho * volume

        # Step 2: Impact energy
        E_impact = 0.5 * mass * v**2
        
        # Step 3: Seismic energy
        E_seismic = epsilon * E_impact
        
        # Step 4: Richter magnitude (Equation 40)
        M = (2/3) * math.log10(E_seismic) - 5.87

        # Step 5: Mercalli intensity (Equations 41a–c)
        if R <= 60000:
            MMI = 1.78 * M - 1.55 * math.log10(R) - 3.78
        elif R <= 700000:
            MMI = 1.66 * M - 3.61 * math.log10(R) + 3.17
        else:
            MMI = 2.20 * M - 4.27 * math.log10(R) + 0.94

        return {
            "Impactor Mass (kg)": round(mass, 2),
            "Impact Energy (J)": round(E_impact, 2),
            "Seismic Energy (J)": round(E_seismic, 2),
            "Richter Magnitude": round(M, 2),
            "Modified Mercalli Intensity": round(MMI, 2),
            "Distance from Impact (m)": R
        }


    def air_blast_model(v, d, rho, R, airburst=False, burst_altitude=0):
        """
        Simulates air blast effects from a meteor impact using Collins et al. (2005).
        
        Parameters:
        v             : impact velocity (m/s)
        d             : impactor diameter (m)
        rho           : impactor density (kg/m³)
        R             : horizontal distance from impact or burst point (m)
        airburst      : True if airburst, False if surface impact
        burst_altitude: altitude of airburst (m), ignored if airburst=False
        
        Returns:
        dict with impact energy, overpressure, wind speed, and blast type
        """
        # Step 1: Impactor mass
        volume = (4/3) * math.pi * (d / 2)**3
        mass = rho * volume
        
        # Step 2: Impact energy
        E = 0.5 * mass * v**2  # in joules

        # Step 3: Effective blast distance
        R_eff = math.sqrt(R**2 + burst_altitude**2) if airburst else R
        
        # Step 4: Overpressure (Pa)
        P = 1.8e7 * (E**(1/3) / R_eff)**1.3

        # Step 5: Wind speed (m/s)
        W = 290 * (E**(1/3) / R_eff)**0.6
        
        return {
            "Impactor Mass (kg)": round(mass, 2),
            "Impact Energy (J)": round(E, 2),
            "Effective Distance (m)": round(R_eff, 2),
            "Peak Overpressure (Pa)": round(P, 2),
            "Wind Speed (m/s)": round(W, 2),
            "Blast Type": "Airburst" if airburst else "Surface Impact"
        }
    

    if airburst_model() > 0:
        break_up = airburst_model()
        v_final, g_diameter, airburst = collins_pancake_descent(diameter,density,break_up,vi(break_up),np.degrees(angle))
    else: 
        v_final = vi(0)
        g_diameter = diameter
        airburst = False

    thermal_effect = thermal_radiation_model(v_final, g_diameter, density, R, airburst)