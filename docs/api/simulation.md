# Simulation

## `orbital_parameters.py`

Standard headers in a detailed orbital data file for an asteroid impact scenario, like those provided by NASA's Center for Near-Earth Object Studies (CNEOS).
* **Case**: A unique identification number for each simulated impact trajectory. A single scenario file can contain thousands of possible paths, and this is the identifier for each one.
* **xi (ξ) and zeta (ζ)**: These are technical coordinates on the "target b-plane." The b-plane is an imaginary plane that is perpendicular to the asteroid's path and passes through the center of the Earth. `xi` and `zeta` pinpoint the exact location where the asteroid's trajectory would pierce this plane, which helps to define the impact location on Earth with high precision.
* **Lat**: **Latitude**. The geographic latitude on Earth where the asteroid enters the atmosphere (typically defined at 100 km altitude). This corresponds to the `latitude` variable in `orbital_parameters.py`.
* **ELon**: **East Longitude**. The geographic longitude, measured in degrees east from the prime meridian. This corresponds to the `longitude` variable in `orbital_parameters.py`.
* **Vel**: **Velocity**. The speed of the asteroid as it enters the atmosphere, relative to the Earth. It's usually measured in kilometers per second (km/s). This corresponds to the `entry_velocity_kms` variable.
* **Az**: **Azimuth**. The compass direction the asteroid is coming *from*, measured in degrees clockwise from North (0° = North, 90° = East, 180° = South, 270° = West).
* **El**: **Elevation / Entry Angle**. The angle of the asteroid's path relative to the local horizontal plane. An angle of 90° would be a direct, vertical impact, while a low angle would be a shallow, grazing entry. This corresponds to the `entry_angle_deg` variable.
* **Time**: The precise time of atmospheric entry or impact, often given as a Julian Date or a specific calendar date and time (UTC).

### data : https://cneos.jpl.nasa.gov/pd/cs/
* https://cneos.jpl.nasa.gov/pd/cs/pdc15/ : https://cneos.jpl.nasa.gov/pd/cs/pdc15/2015pdc_mts.txt
