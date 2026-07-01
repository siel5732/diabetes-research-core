import numpy as np
from scipy.integrate import odeint
import json
import os

# Sir Frederick Banting and Aphex's Lab - Alginate Micro-Bioreactor Oxygen Diffusion
# Principal Investigators: Sir Frederick Banting
# Research Scientists: Aphex, Trent

# --- Model Parameters ---
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

Q_max_spheroid = 1e-8 # mol/cm^3/s (maximum oxygen consumption rate by spheroid, per spheroid volume)
K_m_spheroid = 0.01e-6 # mol/cm^3 (Michaelis-Menten constant, 10 nM)

# Effective mass transfer coefficients
# These coefficients relate to the diffusion rate across a "boundary layer"
# k_diff = D * (Area / Volume) / effective_thickness
k_diff_bulk_alginate = D_oxygen_alginate * SA_outer_capsule / V_alginate / (R_capsule - R_spheroid)
k_diff_alginate_spheroid = D_oxygen_alginate * SA_spheroid_interface / V_spheroid / (R_capsule - R_spheroid)

# --- ODE System Definition ---
def krogh_bioreactor_ode(y, t, C_bulk_oxygen, k_diff_bulk_alginate, k_diff_alginate_spheroid, Q_max_spheroid, K_m_spheroid):
    C_alginate, C_spheroid = y

    # dC_alginate/dt: Diffusion from bulk to alginate, diffusion from alginate to spheroid
    dC_alginate_dt = k_diff_bulk_alginate * (C_bulk_oxygen - C_alginate) - k_diff_alginate_spheroid * (C_alginate - C_spheroid)

    # dC_spheroid/dt: Diffusion from alginate to spheroid, consumption by spheroid
    consumption_rate = (Q_max_spheroid * C_spheroid) / (K_m_spheroid + C_spheroid)
    dC_spheroid_dt = k_diff_alginate_spheroid * (C_alginate - C_spheroid) - consumption_rate

    return [dC_alginate_dt, dC_spheroid_dt]

if __name__ == "__main__":
    # Initial conditions
    C_alginate_initial = 0.0e-6 # mol/cm^3
    C_spheroid_initial = 0.0e-6 # mol/cm^3
    initial_conditions = [C_alginate_initial, C_spheroid_initial]

    # Time points (e.g., 2 hours, with 1000 points)
    t_start = 0
    t_end = 2 * 3600 # 2 hours in seconds
    num_points = 1000
    time_points = np.linspace(t_start, t_end, num_points)

    # Solve the ODEs
    solution = odeint(krogh_bioreactor_ode, initial_conditions, time_points,
                      args=(C_bulk_oxygen, k_diff_bulk_alginate, k_diff_alginate_spheroid, Q_max_spheroid, K_m_spheroid))

    C_alginate_over_time = solution[:, 0].tolist()
    C_spheroid_over_time = solution[:, 1].tolist()

    # Create results payload
    simulation_results = {
        "metadata": {
            "title": "Permselective Alginate Hydrogel Micro-Bioreactors Krogh Oxygen Diffusion Simulation",
            "p_i_personas": ["Sir Frederick Banting", "Imhotep"],
            "computational_leads": ["Aphex", "Trent"],
            "timestamp": "2026-06-30"
        },
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
        "C_spheroid_mol_cm3": C_spheroid_over_time,
        "final_C_alginate": C_alginate_over_time[-1],
        "final_C_spheroid": C_spheroid_over_time[-1]
    }

    output_dir = "research_round/diabetes"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to spheroid_simulation_results
    output_path = os.path.join(output_dir, "diabetes_spheroid_simulation_results.json")
    with open(output_path, "w") as f:
        json.dump(simulation_results, f, indent=4)
        
    # Also save to diabetes_simulation_results for safety
    output_path_alt = os.path.join(output_dir, "diabetes_simulation_results.json")
    with open(output_path_alt, "w") as f:
        json.dump(simulation_results, f, indent=4)

    print(f"Diabetes Alginate Bioreactor Simulation Complete. Results saved to {output_path}")
