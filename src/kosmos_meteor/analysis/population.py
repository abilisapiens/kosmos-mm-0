import numpy as np

def calculate_affected_population(damage_footprint: float, pop_density: float = 15.21) -> float:
    """Estimates the number of people affected within a damage footprint.

    This is a highly simplified function that assumes a circular damage area
    and a uniform global average population density. A real implementation
    must use gridded population data (e.g., from an xarray DataSet) and
    perform a geospatial intersection.

    Args:
        damage_footprint (float): The characteristic size of the damage area.
            Can be a radius in km (for local damage) or another metric.
        pop_density (float): The population density in people per square km.
            Defaults to the global average from the paper.

    Returns:
        float: The estimated number of people affected.
    """
    if damage_footprint <= 0 or np.isnan(damage_footprint):
        return 0.0

    # Assume the footprint is a radius in km for this example
    area_km2 = np.pi * damage_footprint**2
    return area_km2 * pop_density