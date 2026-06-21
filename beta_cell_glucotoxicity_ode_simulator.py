
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import json

# Model parameters (example values, these would be experimentally derived)
params = {
    'G_basal': 5.0,     # Basal glucose level (mM)
    'I_basal': 100,     # Basal insulin level (pM)
    'k_G_prod': 0.1,    # Glucose production rate (mM/hr)
    'k_G_elim': 0.05,   # Glucose elimination rate (1/hr) - insulin independent
    'k_I_prod_beta': 0.01, # Insulin production per beta cell mass (pM/cell-mass/hr)
    'k_I_elim': 0.02,   # Insulin elimination rate (1/hr)
    'k_G_insulin_dep_elim': 0.001, # Insulin-dependent glucose elimination rate (1/pM/hr)
    'G_stress_threshold': 8.0, # Glucose threshold for ER stress (mM)
    'k_ER_stress_on': 0.1, # Rate of ER stress activation (1/hr per unit above threshold)
    'k_ER_stress_off': 0.01, # Rate of ER stress deactivation (1/hr)
    'k_UPR_on': 0.05,   # Rate of UPR activation from ER stress (1/hr)
    'k_UPR_off': 0.005, # Rate of UPR deactivation (1/hr)
    'k_chaperone_exhaustion': 0.002, # Rate of chaperone exhaustion by UPR (1/hr)
    'k_caspase_activation': 0.001, # Rate of caspase activation from ER stress (1/hr)
    'k_beta_cell_apoptosis_basal': 0.0001, # Basal beta cell apoptosis rate (1/hr)
    'k_beta_cell_apoptosis_stress': 0.005, # Stress-induced beta cell apoptosis rate (1/hr per unit caspase)
    'Max_beta_cell_mass': 100, # Initial/max beta cell mass (relative units)
    'beta_cell_regeneration': 0.0005 # Beta cell regeneration rate (1/hr)
}

# Initial conditions for the ODEs
# [Glucose, Insulin, ER_Stress, UPR, Caspase_Activation, Beta_Cell_Mass]
initial_conditions = [params['G_basal'], params['I_basal'], 0, 0, 0, params['Max_beta_cell_mass']]

# Define the ODE system
def beta_cell_model(y, t, p):
    Glucose, Insulin, ER_Stress, UPR, Caspase_Activation, Beta_Cell_Mass = y

    # 1. Glucose dynamics
    dGlucose_dt = p['k_G_prod'] - (p['k_G_elim'] * Glucose) - (p['k_G_insulin_dep_elim'] * Insulin * Glucose)

    # 2. Insulin dynamics (dependent on Beta_Cell_Mass and Glucose stimulation)
    insulin_secretion_stim = (Glucose > p['G_basal']) * (Glucose - p['G_basal']) # Glucose-stimulated secretion
    dInsulin_dt = (p['k_I_prod_beta'] * Beta_Cell_Mass * insulin_secretion_stim) - (p['k_I_elim'] * Insulin)

    # 3. ER Stress dynamics (triggered by high glucose)
    if Glucose > p['G_stress_threshold']:
        dER_Stress_dt = p['k_ER_stress_on'] * (Glucose - p['G_stress_threshold']) - (p['k_ER_stress_off'] * ER_Stress)
    else:
        dER_Stress_dt = -(p['k_ER_stress_off'] * ER_Stress)
    dER_Stress_dt = max(dER_Stress_dt, -ER_Stress) # ER Stress cannot be negative

    # 4. UPR (Unfolded Protein Response) dynamics (activated by ER Stress)
    dUPR_dt = (p['k_UPR_on'] * ER_Stress) - (p['k_UPR_off'] * UPR) - (p['k_chaperone_exhaustion'] * UPR) # UPR also contributes to exhaustion
    dUPR_dt = max(dUPR_dt, -UPR) # UPR cannot be negative

    # 5. Caspase Activation (from chronic ER Stress)
    dCaspase_Activation_dt = (p['k_caspase_activation'] * ER_Stress) # Caspase activation directly from ER Stress
    dCaspase_Activation_dt = max(dCaspase_Activation_dt, -Caspase_Activation) # Caspase cannot be negative

    # 6. Beta Cell Mass dynamics (decay due to apoptosis, regeneration)
    apoptosis_rate = p['k_beta_cell_apoptosis_basal'] + (p['k_beta_cell_apoptosis_stress'] * Caspase_Activation)
    dBeta_Cell_Mass_dt = (p['beta_cell_regeneration'] * (p['Max_beta_cell_mass'] - Beta_Cell_Mass)) - (apoptosis_rate * Beta_Cell_Mass)
    dBeta_Cell_Mass_dt = max(dBeta_Cell_Mass_dt, -Beta_Cell_Mass) # Beta Cell Mass cannot be negative

    return [dGlucose_dt, dInsulin_dt, dER_Stress_dt, dUPR_dt, dCaspase_Activation_dt, dBeta_Cell_Mass_dt]

# Time points for simulation (e.g., 2 years = 17520 hours)
t = np.linspace(0, 17520, 1000)

# Solve the ODEs
solution = odeint(beta_cell_model, initial_conditions, t, args=(params,))

# Extract results
Glucose_hist = solution[:, 0]
Insulin_hist = solution[:, 1]
ER_Stress_hist = solution[:, 2]
UPR_hist = solution[:, 3]
Caspase_Activation_hist = solution[:, 4]
Beta_Cell_Mass_hist = solution[:, 5]

# Store simulation results
simulation_results = {
    'time': t.tolist(),
    'Glucose': Glucose_hist.tolist(),
    'Insulin': Insulin_hist.tolist(),
    'ER_Stress': ER_Stress_hist.tolist(),
    'UPR': UPR_hist.tolist(),
    'Caspase_Activation': Caspase_Activation_hist.tolist(),
    'Beta_Cell_Mass': Beta_Cell_Mass_hist.tolist(),
    'parameters': params
}

# Save results to JSON
with open('research_data/diabetes/beta_cell_glucotoxicity_simulation_results.json', 'w') as f:
    json.dump(simulation_results, f, indent=4)

# Plotting (optional, for visualization)
plt.figure(figsize=(14, 10))

plt.subplot(3, 2, 1)
plt.plot(t / (24*30), Glucose_hist, label='Glucose (mM)')
plt.xlabel('Time (months)')
plt.ylabel('Glucose (mM)')
plt.title('Glucose Excursions')
plt.grid(True)

plt.subplot(3, 2, 2)
plt.plot(t / (24*30), Insulin_hist, label='Insulin (pM)')
plt.xlabel('Time (months)')
plt.ylabel('Insulin (pM)')
plt.title('Insulin Secretion')
plt.grid(True)

plt.subplot(3, 2, 3)
plt.plot(t / (24*30), ER_Stress_hist, label='ER Stress')
plt.xlabel('Time (months)')
plt.ylabel('Relative Level')
plt.title('ER Stress')
plt.grid(True)

plt.subplot(3, 2, 4)
plt.plot(t / (24*30), UPR_hist, label='UPR')
plt.xlabel('Time (months)')
plt.ylabel('Relative Level')
plt.title('Unfolded Protein Response (UPR)')
plt.grid(True)

plt.subplot(3, 2, 5)
plt.plot(t / (24*30), Caspase_Activation_hist, label='Caspase Activation')
plt.xlabel('Time (months)')
plt.ylabel('Relative Level')
plt.title('Caspase Activation')
plt.grid(True)

plt.subplot(3, 2, 6)
plt.plot(t / (24*30), Beta_Cell_Mass_hist, label='Beta Cell Mass')
plt.xlabel('Time (months)')
plt.ylabel('Relative Mass')
plt.title('Functional Beta-Cell Mass Decay')
plt.grid(True)

plt.tight_layout()
plt.savefig('research_data/diabetes/beta_cell_glucotoxicity_simulation_plot.png')
# plt.show() # Don't show in automated environment

print("Diabetes simulation complete. Results saved to 'research_data/diabetes/beta_cell_glucotoxicity_simulation_results.json'")
