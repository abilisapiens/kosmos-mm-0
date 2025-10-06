import streamlit as st
import requests
import asyncio
import numpy as np
import plotly.graph_objects as go
from astropy import units as u
from kosmos_meteor.impacter.data.neo import fetch_neo
from kosmos_meteor.impacter.orbit.propagate import propagate
from kosmos_meteor.impacter.impact.compute import compute_impact
from poliastro.twobody import Orbit
from poliastro.bodies import Sun
from astropy import units as u
import numpy as np

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="Asteroid Orbit Tracker", layout="wide")
st.title("🚀 Asteroid Orbit Tracker [Sentry + NEO - Based Simulator]")

# -----------------------------
# 1️⃣ Fetch and show Sentry objects
# -----------------------------
st.header("1️⃣ Select a Sentry (Impact-Risk) Object")

# Query Sentry summary
SENTRY_API = "https://ssd-api.jpl.nasa.gov/sentry.api"
# mode S (default) returns summary of objects
try:
    resp = requests.get(SENTRY_API)
    sentry_summary = resp.json()
    # The JSON has e.g. a “data” field with list of objects
    items = sentry_summary.get("data", [])
except Exception as e:
    st.error(f"Failed to fetch Sentry summary: {e}")
    st.stop()

# Build options: designation + perhaps H or diameter as label
options = {}
for obj in items:
    des = obj.get("des")  # e.g. "99942"
    name = obj.get("fullname", des)
    h = obj.get("h")  # absolute magnitude
    diam = obj.get("diameter")  # in km
    v_inf = obj.get("v_inf")  # km/s
    cum_prob = obj.get("ps_cum")
    #label = f"{name} — H={h} — D≈{diam:.3f} km — v_inf={v_inf:.2f} km/s"
    label = f"Name = {name}  — Summary : Cumulative Impact Prob≈{cum_prob} — H={h} — D≈{diam} km — v_inf={v_inf} km/s"
    options[label] = des

if not options:
    st.error("No Sentry objects found.")
    st.stop()

chosen_label = st.selectbox("Choose a Sentry object", list(options.keys()))
sentry_des = options[chosen_label]

# -----------------------------
# 2️⃣ Fetch Sentry detailed + NEO (orbital) data
# -----------------------------
st.header("2️⃣ Load Object & Orbit Data")

# Fetch Sentry detailed info (mode O)
try:
    resp_det = requests.get(f"{SENTRY_API}?des={sentry_des}")
    sentry_detail = resp_det.json()
except Exception as e:
    st.error(f"Failed fetching Sentry details: {e}")
    st.stop()

# Show Sentry detail JSON (for debugging / info)
with st.expander(f"ℹ️📡 NASA JPL CNEOS - Sentry API Data Explained", expanded=False):
    st.markdown("""
    # NASA JPL [Sentry](https://cneos.jpl.nasa.gov/sentry/) API Data Explained
    

    ## Introduction

    The **NASA JPL Sentry system** is a database that continuously monitors the orbits of **near-Earth objects (NEOs)** to assess their risk of impacting Earth. The Sentry API provides predictions about **possible future impacts** and detailed orbital parameters for these objects.

    The data returned for a given NEO includes:

    1. **Impact events** (`data`) – Each possible future close approach or impact.
    2. **Object summary** (`summary`) – Aggregate information about the NEO.
    3. **Metadata** (`signature`) – Information about the source and version of the data.

    ---

    ## 1. Individual Impact Data Points (`data`)

    Each element in the `data` array represents a **potential impact scenario**. Here’s what the fields mean:

    | Field      | Example Value     | Meaning / Intuition                                                                                                                                                     |
    | ---------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `date`     | `"2113-12-14.75"` | The predicted date of the potential impact. The decimal indicates a fraction of the day (e.g., 0.75 ≈ 18:00 UTC).                                                       |
    | `sigma_vi` | `"0.4902"`        | The **1-sigma uncertainty** in the velocity component at the virtual impactor. Smaller values → more precise predictions. Think of this as the "error bar" in velocity. |
    | `ts`       | `"0"`             | Time of **closest approach in Julian centuries** (typically set to 0). Often used internally in computations.                                                           |
    | `ps`       | `"-3.10"`         | The **impact probability in log base 10**. `-3.10` means ~1 in 1,258 chance (10^-3.10). Intuition: smaller (more negative) → rarer impact.                              |
    | `energy`   | `"3.026e+04"`     | **Kinetic energy of impact** in kilotons of TNT. Higher = bigger potential explosion.                                                                                   |
    | `ip`       | `"5.532e-07"`     | **Impact probability**, expressed as a fraction. 1 = 100% chance; 0.000000553 ≈ very low.                                                                               |
    | `ts`       | `"0"`             | Same as above (can be ignored for intuition purposes).                                                                                                                  |


    * This means: On **December 14, 2113**, there is a very low chance (~0.00005%) of impact, with energy roughly **30,260 kt** and a velocity uncertainty of 0.49 km/s.

    ---

    ## 2. Object Summary (`summary`)

    This section aggregates overall properties and statistics about the asteroid:

    | Field       | Example Value           | Meaning / Intuition                                                        |
    | ----------- | ----------------------- | -------------------------------------------------------------------------- |
    | `des`       | `"1979 XB"`             | Designation of the NEO.                                                    |
    | `fullname`  | `"(1979 XB)"`           | Full name including parentheses.                                           |
    | `diameter`  | `"0.659988873958651"`   | Estimated diameter in **kilometers** (~660 m here).                        |
    | `mass`      | `"3.92e+11"`            | Mass in kilograms.                                                         |
    | `v_inf`     | `"23.76"`               | Velocity relative to Earth before gravitational acceleration, km/s.        |
    | `v_imp`     | `"26.24"`               | Predicted impact velocity if collision occurs, km/s.                       |
    | `energy`    | `"3.234e+04"`           | Maximum predicted impact energy in kilotons of TNT.                        |
    | `h`         | `"18.54"`               | Absolute magnitude. Smaller numbers = brighter/larger objects.             |
    | `nobs`      | `18`                    | Number of observations used in orbit determination.                        |
    | `first_obs` | `"1979-12-11"`          | Date of first observation.                                                 |
    | `last_obs`  | `"1979-12-15"`          | Date of last observation.                                                  |
    | `pdate`     | `"2025-10-05 14:30:32"` | Date of the prediction.                                                    |
    | `cdate`     | `"2022-09-17 04:54:54"` | Date of creation of this dataset entry.                                    |
    | `ndel`      | `0`                     | Number of **deleted virtual impactors**. Usually 0.                        |
    | `ndop`      | `0`                     | Number of Doppler measurements used.                                       |
    | `nsat`      | `0`                     | Number of satellite observations used.                                     |
    | `n_imp`     | `4`                     | Number of potential impacts predicted.                                     |
    | `ps_max`    | `"-3.00"`               | Maximum impact probability in log base 10 across predicted events.         |
    | `ts_max`    | `"0"`                   | Maximum value of `ts` (not usually needed for intuition).                  |
    | `ps_cum`    | `"-2.70"`               | Cumulative impact probability across all virtual impactors (~0.002%).      |
    | `darc`      | `"3.9189 days"`         | **Observation arc length**: time span between first and last observations. |
    | `method`    | `"IOBS"`                | Orbit determination method. IOBS = used observations.                      |

    **Intuition:** The summary gives a **big-picture view** of the object: size, mass, potential impact energy, likelihood of hitting Earth, and the reliability of these estimates based on observation history.

    ## Notes

    * Impact probabilities (`ip` / `ps`) are often **very low**, reflecting that most NEOs do not pose immediate threats.
    * `sigma_vi` and `darc` help gauge **uncertainty** in predictions.
    * `energy` allows a **quick assessment of potential damage** if an impact occurs.
    * `v_inf` vs `v_imp` shows how Earth's gravity accelerates the asteroid.
    """)


with st.expander(f"🗄️📡 Sentry details for {sentry_des}", expanded=False):
    st.json(sentry_detail)


# From Sentry detail, try to extract defaults
summary = sentry_detail.get("signature", {})  # or other parts
# Actually the “object” details often under e.g. sentry_detail["data"][0] etc
obj_data = sentry_detail.get("data", [])
default_v_inf = None
default_diam = None
if obj_data and isinstance(obj_data, list):
    first = obj_data[0]
    default_v_inf = first.get("v_inf")
    default_diam = first.get("diameter")
# fallback:
if default_v_inf is None:
    default_v_inf = 12.0  # km/s (fallback guess)
if default_diam is None:
    default_diam = 0.1  # km fallback


# Next: fetch orbital elements via your existing NEO API (if possible)
with st.expander(f"ℹ️📡 NASA JPL NEO API Data Explained", expanded=False):
    st.markdown("""
    # NASA JPL NEO API Data Explanation

    The **NASA JPL NEO API** provides detailed orbital and observational information about near-Earth objects (NEOs), including asteroids and comets. This database is maintained by NASA’s **Center for Near-Earth Object Studies (CNEOS)**. It allows researchers and the public to track objects that may approach or intersect Earth’s orbit. You can access the database and API [here](https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html).


    ## **Datapoints Explanation**

    ### **Orbit Identification and Observations**

    * **orbit_id**: Unique identifier for this computed orbit. Useful to reference a specific solution among multiple computations.
    * **orbit_determination_date**: The date when the orbital solution was last calculated. This tells you how recent and accurate the orbit data is.
    * **first_observation_date / last_observation_date**: Dates of the earliest and latest observations used in orbit determination. A longer time span generally leads to more accurate orbits.
    * **data_arc_in_days**: Number of days between the first and last observations. Indicates the observational baseline.
    * **observations_used**: Total number of observations included in orbit calculation. More observations → higher confidence.
    * **orbit_uncertainty**: A scale (0–9) estimating how precisely the orbit is known. 0 = very precise, 9 = highly uncertain.

    ---

    ### **Orbit Geometry and Intersection**

    * **minimum_orbit_intersection (MOID)**: Minimum distance between the asteroid’s orbit and Earth’s orbit (in AU). Helps assess potential impact risk.
    * **jupiter_tisserand_invariant**: A measure of orbital interaction with Jupiter. Helps classify dynamical behavior (comet vs asteroid) and predict perturbations.

    ---

    ### **Orbital Elements**

    * **epoch_osculation**: The reference date for which orbital elements are computed.
    * **eccentricity (e)**: Describes the orbit shape (0 = circular, 0–1 = elliptical).
    * **semi_major_axis (a)**: Average distance from the Sun in astronomical units (AU). Defines the size of the orbit.
    * **inclination (i)**: Tilt of the orbit relative to Earth’s orbital plane (degrees).
    * **ascending_node_longitude (Ω)**: Angle where the object crosses the ecliptic from south to north.
    * **orbital_period**: Time (in days) for one complete orbit around the Sun.
    * **perihelion_distance (q)**: Closest distance to the Sun.
    * **aphelion_distance (Q)**: Farthest distance from the Sun.
    * **perihelion_argument (ω)**: Angle from ascending node to perihelion. Determines orientation of the ellipse.
    * **perihelion_time (Tp)**: Time when the object reaches perihelion.
    * **mean_anomaly (M)**: Position of the asteroid along its orbit at the epoch (degrees).
    * **mean_motion (n)**: Average angular speed along orbit (degrees/day).
    * **equinox**: Reference frame for the orbital elements, typically J2000.

    ---

    ### **Orbit Classification**

    * **orbit_class_type**: Standard type (e.g., **APO**, **AMO**, **ATE**) describing Earth-crossing or near-Earth orbits:

    * **APO (Apollo)**: Crosses Earth’s orbit with a > 1 AU.
    * **AMO (Amor)**: Approaches Earth but does not cross (q > 1.017 AU).
    * **ATE (Aten)**: Crosses Earth’s orbit with a < 1 AU.
    * **orbit_class_description**: Intuitive explanation of the orbit type.
    * **orbit_class_range**: Quantitative criteria for the class (semi-major axis and perihelion distance).

    ---

    ### **Intuition**

    Think of these orbital elements like a **cosmic GPS**:

    * Semi-major axis and eccentricity define the size and shape of the “track” around the Sun.
    * Inclination and node define the tilt and orientation in 3D space.
    * Perihelion and aphelion mark the closest and farthest points.
    * MOID tells you how close it could get to Earth.
    * Observation data and uncertainty indicate how confident we are about this cosmic trajectory.
                
    ---
    """)


# Display a local image file
st.image("webapp/images/neo_schema.png", caption="Asteroid Orbit Diagram", width=400)



neo_data = None
elements = None
try:
    neo_data = asyncio.run(fetch_neo(sentry_des))
    elements = neo_data["orbital_data"]
    st.success(f"Loaded orbit from NEO API for {sentry_des}")
    with st.expander(f"🗄️📡 NEO details for {sentry_des}", expanded=False):
        st.json(elements)
except Exception as e:
    st.warning(f"Failed to fetch orbit from NEO API: {e}. You may need manual input.")
    # Optionally fallback to user input elements
    # For now, stop if no elements
    if elements is None:
        st.error("No orbital elements available; cannot propagate.")
        st.stop()

# -----------------------------
# 3️⃣ Physical parameters (defaults from Sentry, user override)
# -----------------------------
st.header("3️⃣ Physical / Impact Parameters (editable)")

col1, col2 = st.columns(2)
with col1:
    # size: diam → convert to radius, then mass if density known
    diam_km = default_diam  # in km
    # ask user to input diameter or keep default
    diam_input = st.number_input(
        "Estimated diameter (km)", value=float(diam_km), min_value=0.0001, step=0.0001, format="%.6f"
    )
    density = st.number_input("Density (kg/m³)", min_value=500, max_value=8000, value=3000)
    # compute a default mass from diam & density
    # diam_input in km → convert to m
    radius_m = (diam_input * 1e3) / 2
    default_mass = (4/3) * np.pi * radius_m**3 * density
    mass = st.number_input("Mass (kg)", value=float(default_mass), min_value=1e3, step=1e5, format="%.3e")
with col2:
    # default velocity from v_inf (km/s)
    v_inf_default = default_v_inf
    velocity = st.number_input("Relative velocity (km/s)", value=float(v_inf_default), step=0.1, format="%.2f")
    entry_angle = st.slider("Entry angle (° from horizontal)", 0, 90, 45)

# -----------------------------
# 4️⃣ Propagation period & orbit plotting
# -----------------------------
st.header("4️⃣ Propagate & Visualize Orbit")

prop_days = st.slider("Propagation period (days)", min_value=10, max_value=365, value=30, step=5)

with st.expander(f"ℹ️📡 How to Propagate Orbits", expanded=False):
    st.markdown("""
    ### Orbit Propagation Plot

    This plot visualizes the projected trajectory of the asteroid over a user-defined period of days. Using the classical orbital elements, the orbit is numerically propagated around the Sun.

    **Intuitive explanation of orbital elements used:**

    - **Semi-major axis (a):** Average distance from the Sun; defines the size of the orbit.  
    - **Eccentricity (ecc):** Measures how stretched the orbit is; 0 is circular, close to 1 is very elongated.  
    - **Inclination (inc):** Tilt of the orbit relative to the ecliptic plane (Earth's orbital plane).  
    - **Longitude of ascending node (RAAN):** Angle from a reference direction to where the asteroid crosses the ecliptic plane going north.  
    - **Argument of perihelion (argp):** Angle from the ascending node to the orbit’s closest approach to the Sun.  
    - **True anomaly (nu):** Position of the asteroid along its orbit at the starting epoch; defines where we begin propagation.

    **Propagation calculation:**  
    The orbit is advanced in time by numerically computing (using *poliastro*) the asteroid's position at each time step. We then extract the x and y coordinates to plot its path in the plane.  

    **Plot elements:**  
    - Orange line: Asteroid's path.  
    - 🌍 marker: Earth's position at the origin.  
    - Axes: x and y coordinates in kilometers, scaled equally for correct distances.

    **Limitations:**  
    - The plot assumes only Sun’s gravity (two-body problem); perturbations from planets are ignored.  
    - True anomaly is used for the initial position; mean anomaly alone would not give the exact location.  
    - Units are simplified for visualization; real orbits are three-dimensional and can be affected by other forces.
    """)

# Propagate orbit
time_steps = np.linspace(0, prop_days, num=200)

x_positions = []
y_positions = []
for t in time_steps:
    orb = propagate(elements, t)
    x_positions.append(orb.r[0].to_value())
    y_positions.append(orb.r[1].to_value())

# Plot
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=np.array(x_positions),
        y=np.array(y_positions),
        mode="lines",
        name="Asteroid path",
        line=dict(color="orange", width=2),
    )
)
fig.add_trace(
    go.Scatter(
        x=[0],
        y=[0],
        mode="text",
        text=["🌍"],
        textfont=dict(size=20),
        name="Earth",
        hoverinfo="skip",
    )
)
x_margin = (max(x_positions) - min(x_positions)) * 0.1
y_margin = (max(y_positions) - min(y_positions)) * 0.1
fig.update_layout(
    title=f"Orbit over {prop_days} days",
    xaxis=dict(
        title="x (km)",
        scaleanchor="y",
        scaleratio=1,
        range=[min(min(x_positions), -x_margin), max(max(x_positions), x_margin)],
    ),
    yaxis=dict(
        title="y (km)",
        range=[min(min(y_positions), -y_margin), max(max(y_positions), y_margin)],
    ),
    width=600,
    height=600,
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=False)

# -----------------------------
# 5️⃣ Impact estimation
# -----------------------------
st.header("5️⃣ Estimate Impact Consequences")

impact = compute_impact(
    mass=mass, density=density, velocity=velocity, angle=entry_angle
)

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Kinetic Energy", f"{impact['energy'] / 1e15:.2f} PJ")
col_b.metric("Crater Diameter", f"{impact['crater_diam']:.1f} km")
col_c.metric("Seismic Mw", f"{impact['seismic_mw']:.2f}")
col_d.metric("Tsunami run-up (≈10 km)", f"{impact['tsunami_height']:.1f} km")

st.caption(
    "Formulas: Eₖ = ½ m v²; D ≈ 1.8 (Eₖ/10¹⁵ J)⁰·²² km; Mw ≈ (2/3) log₁₀(Eₖ/10⁷ J) − 2.9; R ≈ 0.14 (Eₖ/10¹⁵ J)⁰·³ km"
)
st.success("All calculations done locally — no data is sent externally.")

# -----------------------------
# 6️⃣ Asteroid Deflection Simulation (Kinetic Impactor & Gravity Tractor)
# -----------------------------
st.header("6️⃣ Deflection Experiment — Kinetic Impactor & Gravity Tractor")

st.markdown("""
You can now explore two real-world asteroid deflection strategies:

1. **Kinetic Impactor** — A spacecraft crashes into the asteroid to transfer momentum.
2. **Gravity Tractor** — A spacecraft hovers nearby, using gravity over months/years to tug it slightly.

We'll model both as **small changes in velocity (Δv)** and visualize the new orbit.
""")

method = st.radio(
    "Choose deflection method:",
    ["None", "Kinetic Impactor", "Gravity Tractor"],
    horizontal=True
)

# User input for Δv parameters
col1, col2 = st.columns(2)
with col1:
    if method == "Kinetic Impactor":
        st.markdown("### ⚙️ Kinetic Impactor Parameters")
        imp_mass = st.number_input("Impactor mass (kg)", value=500.0, min_value=0.1)
        imp_vel = st.number_input("Impact velocity (km/s)", value=6.0, min_value=0.1)
        efficiency = st.slider("Momentum transfer efficiency β", 1.0, 5.0, 2.0)
        # Δv from momentum conservation: Δv = β * (m_imp / m_ast) * v_imp
        delta_v = efficiency * (imp_mass / mass) * imp_vel * 1e3  # convert to m/s
        # delta_v *= 1e3
        st.write(f"**Resulting Δv ≈ {delta_v:.6f} m/s**")

    elif method == "Gravity Tractor":
        st.markdown("### 🛰️ Gravity Tractor Parameters")
        gt_mass = st.number_input("Tractor spacecraft mass (kg)", value=2000.0, min_value=1.0)
        dist = st.number_input("Distance from asteroid center (m)", value=200.0, min_value=10.0)
        duration = st.number_input("Operation duration (days)", value=365.0, min_value=1.0)
        G_const = 6.67430e-11
        acc = G_const * gt_mass / (dist**2)  # gravitational acceleration
        delta_v = acc * duration * 86400  # seconds in a day
        # delta_v *= 1e3
        st.write(f"**Resulting Δv ≈ {delta_v:.6f} m/s**")

    else:
        delta_v = 0.0
        st.markdown("No deflection applied (baseline orbit).")

# with col2:
#     st.image("webapp/images/deflection_methods.png", caption="Deflection Concepts", width=350)

# -----------------------------
# 7️⃣ Propagate the Deflected Orbit
# -----------------------------
st.subheader("🪐 Deflected Orbit Propagation")

st.markdown("""
We apply Δv to the asteroid’s velocity vector at the start of the propagation, 
then re-compute its new trajectory using the same two-body dynamics.
""")

# Map NEO API elements to poliastro
a   = float(elements["semi_major_axis"]) * u.AU
ecc = float(elements["eccentricity"]) * u.one
inc = float(elements["inclination"]) * u.deg
raan= float(elements["ascending_node_longitude"]) * u.deg
argp= float(elements["perihelion_argument"]) * u.deg
# NEO API gives mean anomaly, but we need true anomaly at epoch
M   = float(elements.get("mean_anomaly", 0.0)) * u.deg



# Baseline orbit
# orb_base = Orbit.from_classical(
#     attractor=Sun,
#     a=elements["semi_major_axis"] * u.AU,
#     ecc=elements["eccentricity"] * u.one,
#     inc=elements["inclination"] * u.deg,
#     raan=elements["raan"] * u.deg,
#     argp=elements["argp"] * u.deg,
#     nu=elements["nu"] * u.deg,
# )
orb_base = Orbit.from_classical(Sun, a, ecc, inc, raan, argp, M)


# Apply delta_v as before
v_vec = orb_base.v.to(u.m / u.s)
v_hat = v_vec / np.linalg.norm(v_vec)
v_new = v_vec + delta_v * u.m / u.s
v_new = v_new.to(u.km / u.s)

orb_deflected = Orbit.from_vectors(Sun, orb_base.r, v_new)

# Propagate both
x_base, y_base, x_defl, y_defl = [], [], [], []
for t in np.linspace(0, prop_days, 200) * u.day:
    o_base_t = orb_base.propagate(t)
    o_defl_t = orb_deflected.propagate(t)
    x_base.append(o_base_t.r[0].to(u.km).value)
    y_base.append(o_base_t.r[1].to(u.km).value)
    x_defl.append(o_defl_t.r[0].to(u.km).value)
    y_defl.append(o_defl_t.r[1].to(u.km).value)


# Plot
fig_defl = go.Figure()
fig_defl.add_trace(go.Scatter(x=x_base, y=y_base, mode="lines", name="Original Orbit", line=dict(color="orange", width=2)))
fig_defl.add_trace(go.Scatter(x=x_defl, y=y_defl, mode="lines", name="Deflected Orbit", line=dict(color="cyan", width=2, dash="dash")))
fig_defl.add_trace(go.Scatter(x=[0], y=[0], mode="text", text=["🌍"], textfont=dict(size=20), name="Earth", hoverinfo="skip"))

fig_defl.update_layout(
    title="Orbit Comparison Before and After Deflection",
    xaxis_title="x (km)",
    yaxis_title="y (km)",
    width=700, height=700,
    legend=dict(x=0.02, y=0.98),
    xaxis=dict(scaleanchor="y", scaleratio=1)
)
st.plotly_chart(fig_defl, use_container_width=True)

st.markdown(f"""
### Summary
| Parameter | Value |
| ---------- | ------ |
| Δv Applied | {delta_v:.6f} m/s |
| Deflection Method | {method} |
| Duration (if tractor) | {duration if method == 'Gravity Tractor' else 'N/A'} days |
""")

st.caption("""
**Notes:**
- This is a *simplified perturbation model* — the Δv is applied tangentially at t=0.
- Real missions use complex guidance and long-term orbital mechanics.
- Even a few mm/s Δv can cause huge deviations over years.
""")
