import streamlit as st

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Meteor Madness - NASA Space Apps 2025",
    layout="wide"
)

# -----------------------------
# Main Title
# -----------------------------
st.title("☄️ Meteor Madness: NASA Space Apps Challenge 2025")
st.markdown("Innovative solutions for space exploration and meteor studies")

st.markdown("---")

# -----------------------------
# Objectives
# -----------------------------
st.header("🎯 Objectives")
st.markdown("""
- Understand the threat posed by Near-Earth Objects (NEOs) by developing models simulating a meteor impact.
- Assess potential damage and human vulnerability.
- Explore mitigation strategies for planetary defense.
- Promote education through interactive and engaging tools.
- Explain complex scientific models and theories in plain language.
""")

st.markdown("---")

# -----------------------------
# Entry and Impact Severity Modeling
# -----------------------------
st.header("☄️ Entry and Impact Severity Modeling")
st.markdown("""
- Modeled atmospheric entry dynamics: **velocity, angle, density, drop point**.
- Seven types of effects modeled:
  - Eventual break-up and airburst
  - Crater formation and ejecta deposits
  - Thermal radiation and fireball radius
  - Blast overpressure
  - Wind intensity
  - Seismic activity created
  - Eventual tsunami
- Vulgarization: raw data transformed to facilitate understanding and visualization.
""")

st.markdown("---")

# -----------------------------
# Vulnerability and Casualty Modeling
# -----------------------------
st.header("📊 Vulnerability and Casualty Modeling")
st.markdown("""
- Depends on the severity of the effect.
- Calculated using **ARMOR (2017)** and **PAIR (2024) insights**.
- Allows creation of areas of casualty rate by combining severity and vulnerability.
""")

st.markdown("---")

# -----------------------------
# Mitigation Modeling & Planetary Defense
# -----------------------------
st.header("🛡️ Mitigation Modeling & Planetary Defense")
st.markdown("""
- Explored deflection strategies, such as **kinetic impactors** and **gravity tractor**.
- Interactive approach: users can try sending an impactor or a gravity tractor on a meteor and see the effect on its orbit. --> **VERY LIMITED VISUAL EFFECT GIVEN SIMULATION SIZE** 
""")

st.markdown("---")

# -----------------------------
# Fun and Didactic Aspect
# -----------------------------
st.header("🎉 Why It’s Fun and Didactic")
st.markdown("""
- Combines science, coding, and creativity.
- Stimulates the user as they actively participate in the learning process.
- Vulgarization work to **democratize the phenomenon**.
""")

