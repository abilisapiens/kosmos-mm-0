"""Impact‑effects calculations – kinetic energy, crater, seismic, tsunami."""
import numpy as np

def compute_impact(mass: float, density: float, velocity: float, angle: float):
    # 1️⃣ kinetic energy
    v_ms = velocity * 1e3
    energy = 0.5 * mass * v_ms ** 2

    # 2️⃣ crater diameter (Collins et al. 2005)
    crater_diam = 1.8 * (energy / 1e15) ** 0.22  # km

    # 3️⃣ seismic magnitude (Melosh 1989)
    seismic_mw = (2.0 / 3.0) * np.log10(energy / 1e7) - 2.9

    # 4️⃣ tsunami run‑up (Ward 2002) – distance fixed at 10 km for demo
    tsunami_height = 0.14 * (energy / 1e15) ** 0.3  # km

    return {
        "energy": energy,
        "crater_diam": crater_diam,
        "seismic_mw": seismic_mw,
        "tsunami_height": tsunami_height,
    }
