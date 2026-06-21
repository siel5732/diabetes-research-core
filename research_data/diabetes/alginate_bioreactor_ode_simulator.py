
import numpy as np
from scipy.integrate import odeint
import json

# --- Model Parameters ---
# Geometry (approximate)
R_capsule = 0.05  # cm (500 um)
R_spheroid = 0.02  # cm (200 um)

# Effective volumes and surface areas for transport
V_alginate = (4/3) * np.pi * (R_capsule**3 - R_spheroid**3) # Volume of alginate shell
V_spheroid = (4/3) * np.pi * R_spheroid**3 # Volume of spheroid

SA_outer_capsule = 4 * np.pi * R_capsule**2 # Outer surface area of capsule
SA_spheroid_interface = 4 * np.pi * R_spheroid**2 # Interface surface area between alginate and spheroid

# Oxygen diffusion and consumption parameters
D_oxygen_alginate = 2e-6  # cm^2/s (typical for hydrogels, adjusted for effective transport)
C_bulk_oxygen = 0.25e-6  # mol/cm^3 (e.g., 250 uM in medium at 21% O2)

# Michaelis-Menten kinetics for beta-cell spheroid oxygen consumption
# Q_max_spheroid: Maximum oxygen consumption rate per unit volume of spheroid (mol/cm^3/s)
# Assume typical consumption of ~10 fmol/cell/hr for beta cells, and 1000 cells/spheroid
# 10 fmol/cell/hr = 10e-15 mol/cell/hr = 10e-15 mol/cell / 3600 s = 2.77e-18 mol/cell/s
# If 1000 cells/spheroid, total spheroid consumption = 2.77e-15 mol/s
# Spheroid volume ~ (4/3)*pi*(0.02)^3 = 3.35e-5 cm^3
# Q_max_spheroid = (2.77e-15 mol/s) / (3.35e-5 cm^3) = 8.26e-11 mol/cm^3/s (this is Vmax for the entire spheroid)
# Let's use a more reasonable Q_max per unit volume that reflects typical values in literature for *tissue* consumption,
# or adjust the cell density implicitly. A typical consumption rate for dense cell cultures is ~1-10 nmol O2 / 10^6 cells / hour.
# 10 nmol / 10^6 cells / hr = 10e-9 mol / 10^6 cells / 3600 s = 2.77e-18 mol/cell/s.
# If we assume a spheroid has, say, 10^3 cells, then total consumption is 2.77e-15 mol/s.
# The volume of a spheroid of R=0.02 cm is 3.35e-5 cm^3.
# So Vmax_per_volume_spheroid = (2.77e-15 mol/s) / (3.35e-5 cm^3) ~ 8.26e-11 mol/cm^3/s. This seems low.
# Let's adjust Q_max_spheroid to a more typical tissue consumption rate, e.g., 1e-8 mol/cm^3/s.
Q_max_spheroid = 1e-8 # mol/cm^3/s

K_m_spheroid = 0.01e-6 # mol/cm^3 (low Km for high affinity, e.g., 10 nM)

# Effective mass transfer coefficients
# These coefficients relate to the diffusion rate across a "boundary layer"
# k_diff = D * (Area / Volume) / effective_thickness
# For bulk-alginate transfer (C_bulk -> C_alginate)
# Using V_alginate as the volume for C_alginate
k_diff_bulk_alginate = D_oxygen_alginate * SA_outer_capsule / V_alginate / (R_capsule - R_spheroid)

# For alginate-spheroid transfer (C_alginate -> C_spheroid)
# Using V_spheroid as the volume for C_spheroid
k_diff_alginate_spheroid = D_oxygen_alginate * SA_spheroid_interface / V_spheroid / (R_capsule - R_spheroid)


# --- ODE System Definition ---
def krogh_bioreactor_ode(y, t, C_bulk_oxygen, k_diff_bulk_alginate, k_diff_alginate_spheroid, Q_max_spheroid, K_m_spheroid):
    C_alginate, C_spheroid = y

    # dC_alginate/dt: Diffusion from bulk to alginate, diffusion from alginate to spheroid
    # The (C_alginate - C_spheroid) term models flux from alginate to spheroid.
    # The term is positive when C_alginate > C_spheroid, causing C_alginate to decrease and C_spheroid to increase.
    dC_alginate_dt = k_diff_bulk_alginate * (C_bulk_oxygen - C_alginate) - k_diff_alginate_spheroid * (C_alginate - C_spheroid)

    # dC_spheroid/dt: Diffusion from alginate to spheroid, consumption by spheroid
    # The (C_alginate - C_spheroid) term models flux from alginate to spheroid.
    # The consumption term is always negative for positive consumption rate.
    consumption_rate = (Q_max_spheroid * C_spheroid) / (K_m_spheroid + C_spheroid)
    dC_spheroid_dt = k_diff_alginate_spheroid * (C_alginate - C_spheroid) - consumption_rate

    return [dC_alginate_dt, dC_spheroid_dt]

# --- Simulation Setup ---
# Initial conditions
C_alginate_initial = 0.0e-6 # mol/cm^3
C_spheroid_initial = 0.0e-6 # mol/cm^3
initial_conditions = [C_alginate_initial, C_spheroid_initial]

# Time points (e.g., 2 hours, with 1000 points)
t_start = 0
t_end = 2 * 3600 # 2 hours in seconds
num_points = 1000
time_points = np.linspace(t_start, t_end, num_points)

# --- Run Simulation ---
solution = odeint(krogh_bioreactor_ode, initial_conditions, time_points,
                  args=(C_bulk_oxygen, k_diff_bulk_alginate, k_diff_alginate_spheroid, Q_max_spheroid, K_m_spheroid))

# Extract results
C_alginate_over_time = solution[:, 0].tolist()
C_spheroid_over_time = solution[:, 1].tolist()

# --- Save Results ---
simulation_results = {
    "parameters": {
        "R_capsule_cm": R_capsule,
        "R_spheroid_cm": R_spheroid,
        "V_alginate_cm3": V_alginate,
        "V_spheroid_cm3": V_spheroid,
        "SA_outer_capsule_cm2": SA_outer_capsule,
        "SA_spheroid_interface_cm2": SA_spheroid_interface,
        "D_oxygen_alginate_cm2_s": D_oxygen_alginate,
        "C_bulk_oxygen_mol_cm3": C_bulk_oxygen,
        "Q_max_spheroid_mol_cm3_s": Q_max_spheroid,
        "K_m_spheroid_mol_cm3": K_m_spheroid,
        "k_diff_bulk_alginate": k_diff_bulk_alginate,
        "k_diff_alginate_spheroid": k_diff_alginate_spheroid
    },
    "time_seconds": time_points.tolist(),
    "C_alginate_mol_cm3": C_alginate_over_time,
    "C_spheroid_mol_cm3": C_spheroid_over_time
}

print(json.dumps(simulation_results, indent=4))
