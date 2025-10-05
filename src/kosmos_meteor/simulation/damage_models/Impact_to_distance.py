   
        thermal_effect = thermal_radiation_model(v_final, g_diameter, density, R, airburst)
        
        
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

