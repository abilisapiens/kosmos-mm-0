import streamlit as st
from streamlit_folium import st_folium
import folium
from global_land_mask import globe
from pathlib import Path
import fiona
import geopandas as gpd
from shapely.geometry import Point
import math
import time
import numpy as np

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Impact Event", layout="wide")


# -----------------------------
# Load geo data
# -----------------------------
gpkg_path = Path("data/external/ne_10m_urban_areas.gpkg")
layer = fiona.listlayers(gpkg_path)[0]  # 'ne_10m_urban_areas'
URBAN = gpd.read_file(gpkg_path, layer=layer).set_crs(4326)

# -----------------------------
# Parameters
# -----------------------------
SEVERITY_MAX = {"combined": 100}
EFFECT_COLORS = {"combined": "red"}

# -----------------------------
# Base effects data (for "medium" size)
# -----------------------------
effects_data_base = {
    "combined": {
        "distance": [400000, 200000, 100000, 50000, 10000, 1000],
        "severity": [0.01, 25, 33, 50, 75, 100],
        "vulnerability": [0.01, 0.25, 0.33, 0.5, 0.75, 1.0],
    }
}

# -----------------------------
# Helpers
# -----------------------------
def safe_is_land(lat, lon):
    """Safely check if coordinates are on land (no crash)."""
    try:
        if not math.isfinite(lat) or not math.isfinite(lon):
            return False
        lat = max(min(lat, 90), -90)
        lon = max(min(lon, 180), -180)
        return globe.is_land(lat, lon)
    except Exception:
        return False


def is_coordinates_urban(lat: float, lon: float) -> bool:
    """Check if coordinates are in an urban area (safe)."""
    try:
        pt = Point(lon, lat)
        cand = URBAN.sindex.query(pt, predicate="intersects")
        return len(cand) > 0 and URBAN.iloc[list(cand)].intersects(pt).any()
    except Exception:
        return False


def draw_effect_circles(
    m,
    center_lat,
    center_lon,
    effect_key,
    metric_key,
    effects_data,
    severity_max,
    effect_colors,
    icon_name="remove-sign",
):
    """Draw concentric circles for an effect."""
    effect_data = effects_data[effect_key]
    distances = effect_data["distance"]
    severities = effect_data["severity"]
    vulnerabilities = effect_data["vulnerability"]

    color = effect_colors.get(effect_key, "gray")
    max_sev = severity_max.get(effect_key, 100)

    for d, sev, vul in zip(distances, severities, vulnerabilities):
        if metric_key == "vulnerability":
            opacity = vul
            value = vul
        else:
            opacity = min(1.0, sev / max_sev)
            value = sev

        tooltip_text = (
            f"<b>Distance:</b> {d} m<br>"
            f"<b>Severity:</b> {sev}<br>"
            f"<b>Vulnerability:</b> {vul}"
        )

        folium.Circle(
            location=[center_lat, center_lon],
            radius=d,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=opacity,
            weight=2,
            popup=f"{effect_key} ({metric_key}) — {value:.2f}",
            tooltip=tooltip_text,
        ).add_to(m)

    folium.Marker(
        location=[center_lat, center_lon],
        icon=folium.Icon(icon=icon_name, color="gray"),
        popup=f"Center ({center_lat:.4f}, {center_lon:.4f})",
    ).add_to(m)


def scale_effects_by_size(base_effects: dict, size_label: str) -> dict:
    """Return scaled severity/vulnerability arrays based on meteor size."""
    scaled = {}
    for key, data in base_effects.items():
        sev = np.array(data["severity"], dtype=float)
        vul = np.array(data["vulnerability"], dtype=float)

        if size_label == "Small":
            sev /= 4
            vul /= 5
        elif size_label == "Big":
            sev *= 8
            vul *= 8

        # cap vulnerability
        vul = np.clip(vul, 0, 1)

        scaled[key] = {
            "distance": data["distance"],
            "severity": sev.tolist(),
            "vulnerability": vul.tolist(),
        }
    return scaled




# -----------------------------
# App logic
# -----------------------------
st.title("🌍 Impact location")
# --- Info header
st.markdown("""
**Choose Impact Location**  
Click on the map to select coordinates.  
- **Latitude range:** -90° → +90°  
- **Longitude range:** -180° → +180°
""")

if "center" not in st.session_state:
    st.session_state.center = None
if "effect_choice" not in st.session_state:
    st.session_state.effect_choice = "combined"
if "metric_choice" not in st.session_state:
    st.session_state.metric_choice = "vulnerability"
if "reset" not in st.session_state:
    st.session_state.reset = False

# Sidebar
st.sidebar.header("Controls")
effect_choice = st.sidebar.selectbox("Effect", ["combined"], key="effect_choice")
metric_choice = st.sidebar.radio("Metric", ["severity", "vulnerability"], key="metric_choice")

if st.sidebar.button("🔄 Reset Map"):
    st.session_state.center = None
    st.session_state.reset = True
    st.rerun()

# Sidebar parameters
size_map = {"Small": "s", "Medium": "m", "Big": "b"}
impact_map = {"Airburst": "a", "Ground": "g"}

size_label = st.sidebar.selectbox("Select size:", list(size_map.keys()))
impact_label = st.sidebar.radio("Impact Type:", list(impact_map.keys()))
size_choice = size_map[size_label]
impact_choice = impact_map[impact_label]

# Scale effects depending on size
effects_data = scale_effects_by_size(effects_data_base, size_label)

# Default map
lat_default, lon_default = 45.5017, -73.5673
map_width = 1000
map_ratio_width_height = 7 / 5
zoom_start_default = 5

if "zoom" not in st.session_state:
    st.session_state.zoom = zoom_start_default

initial_location = st.session_state.center or [lat_default, lon_default]
m = folium.Map(location=initial_location, zoom_start=st.session_state.zoom)

# Draw if user already clicked
if st.session_state.center:
    lat, lon = st.session_state.center
    draw_effect_circles(
        m,
        lat,
        lon,
        effect_key=st.session_state.effect_choice,
        metric_key=st.session_state.metric_choice,
        effects_data=effects_data,
        severity_max=SEVERITY_MAX,
        effect_colors=EFFECT_COLORS,
    )

    # Safe detection
    is_land = safe_is_land(lat, lon)
    is_urban = is_coordinates_urban(lat, lon)
    label_land_sea = "LAND" if is_land else "SEA"
    label_area = "URBAN" if is_urban else "RURAL"
    st.success(f"Impact On/Over:\n- Ground = {label_land_sea}\n- Area = {label_area}")

map_data = st_folium(m, width=map_width, height=map_width * (1 / map_ratio_width_height))
st.markdown("""📢 Fictious Impacts Circle (placeholder) 📢""")

# Handle zoom + click safely
if map_data:
    if map_data.get("zoom"):
        st.session_state.zoom = map_data["zoom"]

    if map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        # Validate
        if not math.isfinite(lat) or not math.isfinite(lon):
            st.warning("⚠️ Invalid coordinates clicked — ignoring.", icon="⚠️")
        else:
            lat_clamped = max(min(lat, 90), -90)
            lon_clamped = max(min(lon, 180), -180)

            if lat != lat_clamped or lon != lon_clamped:
                st.warning(
                    f"🧭 Coordinates adjusted to within valid range:\n"
                    f"Latitude ∈ [-90°, +90°], Longitude ∈ [-180°, +180°]",
                    icon="🧭"
                )
                time.sleep(1.5)  # allow message to show

            if st.session_state.center != (lat_clamped, lon_clamped):
                st.session_state.center = (lat_clamped, lon_clamped)
                st.session_state.reset = False
                st.rerun()

# Display image by type
if st.session_state.center:
    lat, lon = st.session_state.center
    is_land = safe_is_land(lat, lon)
    is_urban = is_coordinates_urban(lat, lon)

    if not is_land:
        location_code = "s"
        label_area = "SEA"
    elif is_urban:
        location_code = "u"
        label_area = "URBAN"
    else:
        location_code = "r"
        label_area = "RURAL"

    img_name = f"img_{size_choice}_{impact_choice}_{location_code}.png"
    img_path = Path("webapp/images") / img_name
    default_img_land = Path("webapp/images/img_impact_default_land.png")
    default_img_sea = Path("webapp/images/img_impact_default_sea.png")

    if img_path.exists():
        st.image(str(img_path), caption=f"{size_label} - {impact_label} - {label_area}")
    elif is_land:
        if default_img_land.exists():
            st.image(str(default_img_land), caption=f"Default image — {size_label} - {impact_label} - {label_area}")  
        else:
            st.warning(f"⚠️ No image found: {img_name} or default image.")
    else:
        if default_img_sea.exists():
            st.image(str(default_img_sea), caption=f"Default image — {size_label} - {impact_label} - {label_area}")  
        else:
            st.warning(f"⚠️ No image found: {img_name} or default image.")
