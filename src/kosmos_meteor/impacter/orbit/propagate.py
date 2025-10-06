"""Keplerian propagation using poliastro."""
from poliastro.bodies import Sun
from poliastro.twobody.orbit import Orbit
from astropy import units as u

def propagate(elements: dict, days: float):
    orb = Orbit.from_classical(
        attractor=Sun,
        a=float(elements["semi_major_axis"]) * u.AU,
        ecc=float(elements["eccentricity"]) * u.one,
        inc=float(elements["inclination"]) * u.deg,
        raan=float(elements["ascending_node_longitude"]) * u.deg, #
        argp=float(elements["perihelion_argument"]) * u.deg,
        nu=float(elements["mean_anomaly"]) * u.deg, # need keplerian true anomaly (not mean anomaly)
    )
    return orb.propagate(days * u.day)
