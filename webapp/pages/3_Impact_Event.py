import streamlit as st
from streamlit_folium import st_folium
import folium
from global_land_mask import globe
# import requests
from pathlib import Path
import fiona
import geopandas as gpd

from shapely.geometry import Point




# page config
st.set_page_config(page_title="Impact Event",layout="wide")

# parameters for Natural Earth Data
print('1. Load geo data')
# -- data
gpkg_path = Path("data/external/ne_10m_urban_areas.gpkg")
# -- load the urban areas layer
layer=fiona.listlayers(gpkg_path)[0] # expect: 'ne_10m_urban_areas'
URBAN = gpd.read_file(gpkg_path, layer=layer).set_crs(4326)


# parameters and support functions
SEVERITY_MAX = {
    "effect1": 100,
    "effect2": 120,
    "effect3": 90,
    "effect4": 110,
    "effect5": 80,
    "effect6": 70,
    "effect7": 95,
    "combined": 100,
}
EFFECT_COLORS = {
    "effect1": "black",
    "effect2": "orange",
    "effect3": "yellow",
    "effect4": "green",
    "effect5": "blue",
    "effect6": "purple",
    "effect7": "brown",
    "combined": "red",
}

# mock effect data
effects_data = {
#    "effect1": {
#        "distance": [200000,100000, 50000, 10000, 1000],
#        "severity": [10,20, 30, 60, 90],
#        "vulnerability": [0.1,0.2, 0.3, 0.6, 0.9]
#    },
#    "effect2": {
#        "distance": [200000,100000, 50000, 10000, 1000],
#        "severity": [20,30, 40, 70, 100],
#        "vulnerability": [0.2, 0.3,0.4, 0.7, 1.0]
#    },
    # ...
    "combined": {
        "distance": [200000,100000, 50000, 10000, 1000],
        "severity": [25,33, 50, 75, 100],
        "vulnerability": [0.25,0.33, 0.5, 0.75, 1.0]
    },
}
# ======================
# --- HELPER FUNCTION ---
# ======================
def draw_effect_circles(m, center_lat, center_lon, effect_key, metric_key,
                        effects_data, severity_max, effect_colors,
                        icon_name="remove-sign"):
    """Draw concentric circles for an effect around a clicked point."""
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
        elif metric_key == "severity":
            opacity = min(1.0, sev / max_sev)
            value = sev

        tooltip_text = (
            f"<b>Distance:</b> {d} m<br>"
            f"<b>Severity:</b> {sev}<br>"
            f"<b>Vulnerability:</b> {vul}<br>"
            #f"<b>Opacity:</b> {opacity:.2f}"
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
            tooltip=tooltip_text
        ).add_to(m)

    folium.Marker(
        location=[center_lat, center_lon],
        icon=folium.Icon(icon=icon_name, color="gray"),
        popup=f"Center ({center_lat:.4f}, {center_lon:.4f})"
    ).add_to(m)

# def classify_area(lat, lon):
#     url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
#     r = requests.get(url)
#     data = r.json()
#     place_type = data.get("type", "")
#     highlevel_place_type = "Rural"
#     if place_type in ["city", "town"]:
#         highlevel_place_type = "Urban"
#     return {'highlevel_place_type':highlevel_place_type,'place_type':place_type}

def is_coordinates_urban(lat: float, lon: float) -> bool:
    pt = Point(lon, lat)
    # Speed-up: spatial index first, then exact geometry test
    cand = URBAN.sindex.query(pt, predicate="intersects")
    return len(cand) > 0 and URBAN.iloc[list(cand)].intersects(pt).any()


# ======================
# --- APP LOGIC ---
# ======================
st.title("🌍 Impact location")

# Initialize session state
if "center" not in st.session_state:
    st.session_state.center = None
if "effect_choice" not in st.session_state:
    st.session_state.effect_choice = "effect1"
if "metric_choice" not in st.session_state:
    st.session_state.metric_choice = "vulnerability"
if "reset" not in st.session_state:
    st.session_state.reset = False

# Sidebar controls
st.sidebar.header("Controls")
effect_choice = st.sidebar.selectbox("Effect", list(effects_data.keys()), key="effect_choice")
metric_choice = st.sidebar.radio("Metric", ["severity", "vulnerability"], key="metric_choice")

# Reset button
if st.sidebar.button("🔄 Reset Map"):
    st.session_state.center = None
    st.session_state.reset = True
    st.rerun()

# Base map (use last known center if any)
lat_default = 45.5017
lon_default = -73.5673
map_width = 1000
map_ratio_width_height = 7/5
zoom_start_default = 5

# ======================
# --- DISPLAY MAP ---
# ======================

if "zoom" not in st.session_state:
    st.session_state.zoom = zoom_start_default

initial_location = st.session_state.center or [lat_default, lon_default]

m = folium.Map(location=initial_location, zoom_start=st.session_state.zoom)

if st.session_state.center:
    lat, lon = st.session_state.center
    draw_effect_circles(
        m, lat, lon,
        effect_key=st.session_state.effect_choice,
        metric_key=st.session_state.metric_choice,
        effects_data=effects_data,
        severity_max=SEVERITY_MAX,
        effect_colors=EFFECT_COLORS,
        icon_name="remove-sign"
    )
    is_land = globe.is_land(lat, lon)
    is_urban = is_coordinates_urban(lat, lon)
    label_land_sea = "LAND" if is_land else "SEA"
    label_area = "URBAN" if is_urban else "RURAL"
    st.success(f"Impact On/Over :\n- Ground = {label_land_sea}\n- Area = {label_area}")


# --- USER PARAMETERS ---
# Mapping definitions
size_map = {"Small": "s", "Medium": "m", "Big": "b"}
impact_map = {"Airburst": "a", "Ground": "g"}

# Select box — user sees the keys, you store the code
size_label = st.sidebar.selectbox("Select size:", list(size_map.keys()))
impact_label = st.sidebar.radio("Impact Type:", list(impact_map.keys()))

# Get corresponding short code
size_choice = size_map[size_label]
impact_choice = impact_map[impact_label]


map_data = st_folium(m, width=map_width, height=map_width*(1/map_ratio_width_height))

# 🔹 Store zoom level
if map_data and map_data.get("zoom"):
    st.session_state.zoom = map_data["zoom"]

# 🔹 Handle click event
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    if st.session_state.center != (lat, lon):
        st.session_state.center = (lat, lon)
        st.session_state.reset = False
        st.rerun()



# --- After your existing code where you display results ---

# --- determine location type from lat/lon ---
if st.session_state.center:
    lat, lon = st.session_state.center
    is_land = globe.is_land(lat, lon)
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

    if img_path.exists():
        st.image(str(img_path), caption=f"{size_label} - {impact_label} - {label_area}")
    else:
        st.warning(f"Image not found: {img_name}")








# FYI :

# """
# | Property | Description                           | Example                           |
# | -------- | ------------------------------------- | --------------------------------- |
# | `icon`   | Icon name (Bootstrap or Font Awesome) | `"info-sign"`, `"car"`            |
# | `color`  | Marker background color               | `"blue"`, `"red"`                 |
# | `prefix` | Icon set prefix                       | `"glyphicon"` (default) or `"fa"` |

# info-sign	ℹ️
# ok-sign	✅
# remove-sign	❌
# question-sign	❓
# star	⭐
# cloud	☁️
# heart	❤️
# plus	➕
# minus	➖
# search	🔍
# home	🏠
# flag	🚩
# flash	⚡
# leaf	🍃
# globe	🌍
# warning-sign	⚠️
# """

# """
# SHAPES_TEMPLATE = {
#     "Marker": {
#         "location": [LAT, LON],
#         "popup": "Text or HTML popup",
#         "tooltip": "Hover text",
#         "icon": "folium.Icon(icon='info-sign', color='blue')",
#     },

#     "Circle": {
#         "location": [LAT, LON],
#         "radius": 500,              # meters
#         "color": "blue",            # border color
#         "weight": 2,                # border thickness
#         "opacity": 1.0,             # border opacity
#         "fill": True,
#         "fill_color": "blue",
#         "fill_opacity": 0.4,
#         "popup": "Circle info",
#         "tooltip": "Hover info",
#     },

#     "CircleMarker": {
#         "location": [LAT, LON],
#         "radius": 10,               # pixels (not meters)
#         "color": "green",
#         "weight": 2,
#         "opacity": 1.0,
#         "fill": True,
#         "fill_color": "green",
#         "fill_opacity": 0.7,
#         "popup": "Marker info",
#         "tooltip": "Hover info",
#     },

#     "Rectangle": {
#         "bounds": [[LAT1, LON1], [LAT2, LON2]],
#         "color": "orange",
#         "weight": 2,
#         "fill": True,
#         "fill_color": "orange",
#         "fill_opacity": 0.3,
#         "popup": "Rectangle info",
#         "tooltip": "Hover info",
#     },

#     "Polygon": {
#         "locations": [[LAT1, LON1], [LAT2, LON2], [LAT3, LON3]],
#         "color": "purple",
#         "weight": 3,
#         "opacity": 0.8,
#         "fill": True,
#         "fill_color": "purple",
#         "fill_opacity": 0.5,
#         "popup": "Polygon info",
#         "tooltip": "Hover info",
#     },

#     "Polyline": {
#         "locations": [[LAT1, LON1], [LAT2, LON2], [LAT3, LON3]],
#         "color": "red",
#         "weight": 4,
#         "opacity": 0.9,
#         "dash_array": "5, 10",      # dashed pattern
#         "popup": "Line info",
#         "tooltip": "Hover info",
#     }
# }
# """
