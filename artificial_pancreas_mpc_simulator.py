import numpy as np
from scipy.integrate import solve_ivp
import json

# Diabetes Core Focus: Closed-Loop Artificial Pancreas Model Predictive Control (MPC) under Exercise Challenges

# Adapted Bergman Minimal Model (simplified for demonstration)
# State variables: Glucose (G), Insulin in Plasma (Ip), Insulin in Interstitial Fluid (Ii)
# Glucagon is considered an input in this simplified model

# Parameters (example values - these would be from literature/patient-specific calibration)
params_diabetes = {
    "Gb": 90.0,       # Basal Glucose (mg/dL)
    "Ib": 10.0,       # Basal Insulin (muU/mL)
    "Xb": 0.0,        # Basal Insulin effect
    "p1": 0.02,       # Glucose effectiveness (1/min)
    "p2": 0.02,       # Insulin disappearance from plasma (1/min)
    "p3": 0.00001,    # Insulin sensitivity (1/min per muU/mL)
    "n": 0.01,        # Renal glucose excretion rate (mg/dL per min)
    "Vg": 100.0,      # Glucose distribution volume (dL)
    "Vi": 10.0,       # Insulin distribution volume (dL)
    "t_insulin_pump_delay": 5.0, # Delay for insulin pump action (minutes)
    "t_glucagon_pump_delay": 5.0, # Delay for glucagon pump action (minutes)
    "insulin_sensitivity_factor": 0.05, # Factor for insulin sensitivity
    "glucose_production_rate_basal": 1.0, # Basal hepatic glucose production (mg/dL/min)
    "glucose_production_rate_exercise_peak": 5.0, # Peak increase in HGP during exercise
    "exercise_duration": 60, # minutes
    "exercise_start_time": 120, # minutes
}

def bergman_minimal_model(t, y, params, insulin_infusion_rate, glucagon_infusion_rate, exercise_factor):
    G, Ip, Ii = y

    # Glucose dynamics (G)
    # Hepatic Glucose Production (HGP) - affected by glucagon and exercise
    hgp = params["glucose_production_rate_basal"] + (glucagon_infusion_rate * 0.1) + (exercise_factor * params["glucose_production_rate_exercise_peak"])

    # Glucose utilization (GU) - affected by insulin and glucose effectiveness
    gu = (params["p1"] + Ii) * G

    # dG/dt
    dG_dt = hgp - gu - (params["n"] * (G - params["Gb"]) if G > params["Gb"] else 0)

    # Insulin plasma dynamics (Ip)
    # Secretion by pancreas (simplified as infusion) - in a real model, this would be beta-cell response
    # Degradation from plasma
    dIp_dt = (insulin_infusion_rate / params["Vi"]) - (params["p2"] * Ip)

    # Insulin interstitial dynamics (Ii)
    # Transport from plasma to interstitial fluid
    # Degradation from interstitial fluid
    dIi_dt = (params["p3"] * (Ip - Ii)) - (params["p2"] * Ii)

    return [dG_dt, dIp_dt, dIi_dt]

def run_mpc_simulation(params, total_time=480, dt=1.0): # total_time in minutes
    time_points = np.arange(0, total_time + dt, dt)
    num_steps = len(time_points)

    # Initialize state variables
    G_history = np.zeros(num_steps)
    Ip_history = np.zeros(num_steps)
    Ii_history = np.zeros(num_steps)

    # Initial conditions
    G_history[0] = params["Gb"]
    Ip_history[0] = params["Ib"]
    Ii_history[0] = params["Xb"]

    insulin_infusion_history = np.zeros(num_steps)
    glucagon_infusion_history = np.zeros(num_steps)
    exercise_history = np.zeros(num_steps)

    # PID controller parameters (example values)
    Kp_insulin = 0.5
    Ki_insulin = 0.01
    Kd_insulin = 0.1
    Kp_glucagon = 0.2
    Ki_glucagon = 0.005
    Kd_glucagon = 0.05

    insulin_error_integral = 0
    glucagon_error_integral = 0
    last_insulin_error = 0
    last_glucagon_error = 0

    target_glucose = 100.0 # mg/dL

    for i in range(1, num_steps):
        current_time = time_points[i]
        current_G = G_history[i-1]
        current_Ip = Ip_history[i-1]
        current_Ii = Ii_history[i-1]

        # Exercise challenge
        exercise_factor = 0.0
        if params["exercise_start_time"] <= current_time < (params["exercise_start_time"] + params["exercise_duration"]):
            exercise_factor = 1.0
        exercise_history[i] = exercise_factor

        # PID Controller for Insulin (to lower high glucose)
        insulin_error = current_G - target_glucose
        insulin_error_integral += insulin_error * dt
        insulin_derivative = (insulin_error - last_insulin_error) / dt
        insulin_output = (Kp_insulin * insulin_error) + (Ki_insulin * insulin_error_integral) + (Kd_insulin * insulin_derivative)
        insulin_infusion_rate = max(0, insulin_output) # Ensure non-negative infusion
        last_insulin_error = insulin_error

        # PID Controller for Glucagon (to raise low glucose, especially after exercise)
        glucagon_error = target_glucose - current_G # Inverted error for glucagon
        glucagon_error_integral += glucagon_error * dt
        glucagon_derivative = (glucagon_error - last_glucagon_error) / dt
        glucagon_output = (Kp_glucagon * glucagon_error) + (Ki_glucagon * glucagon_error_integral) + (Kd_glucagon * glucagon_derivative)
        glucagon_infusion_rate = max(0, glucagon_output) # Ensure non-negative infusion
        last_glucagon_error = glucagon_error

        # Limit glucagon when glucose is high to avoid overcorrection
        if current_G > target_glucose + 20: # Example threshold
            glucagon_infusion_rate = 0

        # Limit insulin when glucose is low
        if current_G < target_glucose - 10: # Example threshold
            insulin_infusion_rate = 0

        insulin_infusion_history[i] = insulin_infusion_rate
        glucagon_infusion_history[i] = glucagon_infusion_rate

        # Solve ODE for one step
        sol = solve_ivp(bergman_minimal_model, [current_time - dt, current_time], [current_G, current_Ip, current_Ii],
                        args=(params, insulin_infusion_history[i-1], glucagon_infusion_history[i-1], exercise_history[i-1]),
                        method='RK45', dense_output=True)
        
        # Take the last point of the solution for the next step
        G_history[i], Ip_history[i], Ii_history[i] = sol.y[:,-1]

    simulation_results = {
        "time_minutes": time_points.tolist(),
        "glucose": G_history.tolist(),
        "insulin_plasma": Ip_history.tolist(),
        "insulin_interstitial": Ii_history.tolist(),
        "insulin_infusion_rate": insulin_infusion_history.tolist(),
        "glucagon_infusion_rate": glucagon_infusion_history.tolist(),
        "exercise_factor": exercise_history.tolist(),
        "parameters": params
    }
    return simulation_results

if __name__ == "__main__":
    simulation_data = run_mpc_simulation(params_diabetes)
    output_file = 'research_data/diabetes/artificial_pancreas_mpc_results.json'
    with open(output_file, 'w') as f:
        json.dump(simulation_data, f, indent=4)
    print(f"Diabetes simulation completed and results saved to {output_file}")
