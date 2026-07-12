import numpy as np
from scipy.integrate import solve_ivp
import json
import os

def islet_ode_system(t, y, params):
    I, V, A, G, N = y
    
    # Extract parameters
    r_I = params['r_I']
    K_I = params['K_I']
    h_V = params['h_V']
    d_I0 = params['d_I0']
    eta_V = params['eta_V']
    kappa_im = params['kappa_im']
    
    r_V = params['r_V']
    K_V = params['K_V']
    h_A = params['h_A']
    theta_V = params['theta_V']
    d_V = params['d_V']
    
    sigma_A = params['sigma_A']
    h_O2 = params['h_O2']
    d_A = params['d_A']
    chi_A = params['chi_A']
    
    P_G = params['P_G']
    d_G = params['d_G']
    lambda_G = params['lambda_G']
    
    psi_N = params['psi_N']
    h_G = params['h_G']
    d_N = params['d_N']
    
    # ODEs
    # 1. Islet Cell Density
    # Protective effect of vessels: death rate decreases with V
    death_rate_I = d_I0 / (1.0 + eta_V * V)
    dIdt = r_I * I * (1.0 - I / K_I) * (V / (h_V + V)) - death_rate_I * I - kappa_im * I
    
    # 2. Vascular Density
    dVdt = r_V * V * (1.0 - V / K_V) * (A / (h_A + A)) + theta_V * A - d_V * V
    
    # 3. Angiogenic Factors (VEGF)
    # Hypoxic stimulation of VEGF is high when vascularization is low
    hypoxia_stim = h_O2 / (h_O2 + V)
    dAdt = sigma_A * I * hypoxia_stim - d_A * A - chi_A * V * (A / (h_A + A))
    
    # 4. Systemic Glucose
    dGdt = P_G - d_G * G - lambda_G * N * G
    
    # 5. Systemic Insulin
    # GSIS is modeled by a Hill function; vascular coupling represents islet perfusion
    gsis = (G ** 2) / (h_G ** 2 + G ** 2)
    dNdt = psi_N * I * gsis * (V / K_V) - d_N * N
    
    return [dIdt, dVdt, dAdt, dGdt, dNdt]

# Set up parameters
params = {
    'r_I': 0.015,       # Islet cell self-renewal / regeneration rate (day^-1)
    'K_I': 1.2,         # Islet cell density capacity (millions of cells)
    'h_V': 0.1,         # Half-saturation constant for vascular-dependent growth
    'd_I0': 0.06,       # Hypoxic death rate (day^-1) when avascular (V = 0)
    'eta_V': 25.0,      # Vascular protection coefficient against hypoxia-induced apoptosis
    'kappa_im': 0.005,  # Graft-rejection / baseline immune-mediated death rate (day^-1)
    
    'r_V': 0.15,        # Angiogenic vessel growth rate (day^-1)
    'K_V': 1.0,         # Maximum vessel carrying capacity (normalized density)
    'h_A': 0.15,        # Half-saturation constant of VEGF for angiogenesis
    'theta_V': 0.05,    # De novo EPC recruitment rate per unit VEGF (day^-1)
    'd_V': 0.01,        # Capillary vessel regression/pruning rate (day^-1)
    
    'sigma_A': 0.4,     # Maximal VEGF secretion rate by islet cells under hypoxia (day^-1)
    'h_O2': 0.25,       # Oxygen / vascularization half-saturation constant for HIF-1alpha activation
    'd_A': 0.35,        # VEGF degradation/clearance rate (day^-1)
    'chi_A': 0.1,       # VEGF receptor binding / endothelial cellular uptake rate
    
    'P_G': 250.0,       # Endogenous glucose production rate (mg/dL / day)
    'd_G': 0.5,         # Insulin-independent glucose clearance rate (day^-1)
    'lambda_G': 0.2,    # Insulin-dependent glucose disposal efficiency ((muIU/mL)^-1 day^-1)
    
    'psi_N': 340.0,     # Max insulin secretion rate per million islet cells (muIU/mL / day)
    'h_G': 120.0,       # Glucose threshold concentration for insulin release (mg/dL)
    'd_N': 8.0          # Systemic insulin degradation rate (day^-1)
}

# Initial conditions: transplanted islets in a diabetic host
I0 = 1.0     # Transplanted islet load (1.0 million cells)
V0 = 0.02    # Minimal baseline host vascularization at graft site (2% density)
A0 = 0.05    # Minimal initial VEGF in tissue
G0 = 360.0   # Severe diabetic hyperglycemia (360 mg/dL)
N0 = 0.5     # Low baseline insulin in type 1 diabetes (0.5 muIU/mL)

y0 = [I0, V0, A0, G0, N0]
t_span = (0.0, 180.0)  # Simulate 180 days (6 months)
t_eval = np.linspace(0.0, 180.0, 181)  # Daily evaluation

sol = solve_ivp(islet_ode_system, t_span, y0, args=(params,), t_eval=t_eval, method='Radau')

# Check results and print time course every 10 days for a more detailed look
print("Success:", sol.success)
print(f"{'Day':<5} | {'Islets':<8} | {'Vessels':<8} | {'VEGF':<8} | {'Glucose':<8} | {'Insulin':<8}")
print("-" * 60)
for idx in range(0, 181, 10):
    t = sol.t[idx]
    I = sol.y[0][idx]
    V = sol.y[1][idx]
    A = sol.y[2][idx]
    G = sol.y[3][idx]
    N = sol.y[4][idx]
    print(f"{t:<5.1f} | {I:<8.4f} | {V:<8.4f} | {A:<8.4f} | {G:<8.2f} | {N:<8.3f}")

print("\nFinal State:")
print("Islet final:", sol.y[0][-1])
print("Vessels final:", sol.y[1][-1])
print("VEGF final:", sol.y[2][-1])
print("Glucose final:", sol.y[3][-1])
print("Insulin final:", sol.y[4][-1])

# Save the simulation results to JSON
results_dir = "research_data/diabetes"
os.makedirs(results_dir, exist_ok=True)
json_path = os.path.join(results_dir, "diabetes_simulation_data.json")

data_to_save = {
    "metadata": {
        "model_name": "Stem-Cell-Derived Islet Cell Xenotransplant Neovascularization & Angiogenesis Coupling Simulator",
        "description": "High-fidelity ordinary differential equation (ODE) simulator tracking stem-cell islet graft survival, neovascularization, VEGF signaling, systemic glucose clearance, and glucose-stimulated insulin secretion (GSIS) coupled with graft perfusion.",
        "authors": ["Aphex", "Dr. Marie Curie", "Sir Frederick Banting"],
        "date": "2026-06-22",
        "time_units": "days",
        "state_variable_units": {
            "islet_cell_count": "millions of cells (or normalized index, initial=1.0 million)",
            "vascular_density": "normalized capillary density (0.0 to 1.0)",
            "vegf_concentration": "arbitrary concentration units (ng/mL)",
            "glucose_level": "systemic blood glucose (mg/dL)",
            "insulin_production": "systemic insulin concentration (muIU/mL)"
        }
    },
    "parameters": params,
    "initial_conditions": {
        "islet_cell_count": I0,
        "vascular_density": V0,
        "vegf_concentration": A0,
        "glucose_level": G0,
        "insulin_production": N0
    },
    "simulation_results": {
        "time_points": list(sol.t),
        "islet_cell_count": list(sol.y[0]),
        "vascular_density": list(sol.y[1]),
        "vegf_concentration": list(sol.y[2]),
        "glucose_level": list(sol.y[3]),
        "insulin_production": list(sol.y[4])
    }
}

with open(json_path, 'w') as f:
    json.dump(data_to_save, f, indent=4)

print(f"\nSuccessfully wrote simulation results to {json_path}")

# Generate professional multi-panel plot
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Panel 1: Islet Survival and Vascularization
ax1_twin = axs[0].twinx()
p1, = axs[0].plot(sol.t, sol.y[0], 'b-', linewidth=2.5, label='Islet Cell Count (I)')
p2, = ax1_twin.plot(sol.t, sol.y[1], 'r--', linewidth=2.5, label='Vascular Density (V)')
axs[0].set_ylabel('Islet Count (Millions)', color='b', fontsize=12)
ax1_twin.set_ylabel('Vascular Density (Normalized)', color='r', fontsize=12)
axs[0].tick_params(axis='y', labelcolor='b')
ax1_twin.tick_params(axis='y', labelcolor='r')
axs[0].set_title('A: Graft Survival and Neovascularization Dynamics', fontsize=14, fontweight='bold', loc='left')
axs[0].grid(True, linestyle=':', alpha=0.6)
lines1 = [p1, p2]
axs[0].legend(lines1, [l.get_label() for l in lines1], loc='upper right', frameon=True)

# Panel 2: VEGF Concentration (Angiogenic Signaling)
axs[1].plot(sol.t, sol.y[2], 'g-', linewidth=2.5, label='VEGF (A)')
axs[1].set_ylabel('VEGF Conc. (ng/mL)', fontsize=12)
axs[1].set_title('B: VEGF-driven Angiogenic Signaling', fontsize=14, fontweight='bold', loc='left')
axs[1].grid(True, linestyle=':', alpha=0.6)
axs[1].legend(loc='upper right', frameon=True)

# Panel 3: Glucose and Insulin Dynamics
ax3_twin = axs[2].twinx()
p3, = axs[2].plot(sol.t, sol.y[3], 'purple', linestyle='-', linewidth=2.5, label='Blood Glucose (G)')
p4, = ax3_twin.plot(sol.t, sol.y[4], 'orange', linestyle='-.', linewidth=2.5, label='Systemic Insulin (N)')
axs[2].set_ylabel('Blood Glucose (mg/dL)', color='purple', fontsize=12)
ax3_twin.set_ylabel('Insulin Conc. ($\mu$IU/mL)', color='orange', fontsize=12)
axs[2].tick_params(axis='y', labelcolor='purple')
ax3_twin.tick_params(axis='y', labelcolor='orange')
axs[2].set_xlabel('Time (Days)', fontsize=12)
axs[2].set_title('C: Metabolic Recovery & Glycemic Homeostasis', fontsize=14, fontweight='bold', loc='left')
axs[2].grid(True, linestyle=':', alpha=0.6)
lines3 = [p3, p4]
axs[2].legend(lines3, [l.get_label() for l in lines3], loc='upper right', frameon=True)

plt.tight_layout()
plot_path = os.path.join(results_dir, "islet_simulation_plot.png")
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"Successfully generated and saved simulation plots to {plot_path}")
