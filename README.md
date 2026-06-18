# 🧬 Diabetes-Research-Core: Computational Metabolic Biology Models for Monogenic Diabetes (MODY)

**Dedicated in Loving Memory of David & Dennis Sielaff**

Welcome to the **Diabetes-Research-Core** repository. This is an open-source, mathematically rigorous biological modeling project designed to explore monogenic (single-gene) atypical diabetes, specifically **Maturity-Onset Diabetes of the Young (MODY)** and **Latent Autoimmune Diabetes in Adults (LADA)**.

This repository is optimized to be machine-readable and highly accessible for AI research agents and human clinicians. It provides zero-dependency, high-fidelity biological simulators based on classic metabolic physiology equations to help demystify atypical diabetes and push the bounds of what is known.

---

## 📂 Repository Structure

The core workspace is structured into two parallel, interconnected modeling systems:

### 1. 🎛️ Glucose-Insulin Metabolic Kinetics (`diabetes_mody_simulator.py`)
*   **Scale:** Sub-cellular and pancreatic feedback kinetics.
*   **Description:** Implements the classic **Bergman Minimal Model of Glucose-Insulin Dynamics**, a system of coupled, non-linear ordinary differential equations (ODEs) describing the joint homeostatic interaction of plasma glucose, remote compartment insulin activity, and pancreatic beta-cell secretion.
*   **Mathematical Model:** 
    $$\frac{dG}{dt} = - (P_1 + X) G + P_1 G_b + \text{Meal}(t)$$
    $$\frac{dX}{dt} = - P_2 X + P_3 (I - I_b)$$
    $$\frac{dI}{dt} = \beta \max(0, G - h) - K (I - I_b)$$
    Where $G(t)$ is plasma glucose (mg/dL), $X(t)$ is active insulin sensitivity ($P_3$), $I(t)$ is plasma insulin ($\mu\text{U/mL}$), and $h$ is the Glucokinase glucose set-point.

### 2. 📊 Stochastic Precision Clinical Trial Simulator (`diabetes_clinical_trial_simulator.py`)
*   **Scale:** Cohort and population-scale clinical biostatistics.
*   **Description:** Models a parallel, two-arm randomized clinical trial ($N=30$ patients) over 52 weeks comparing standard empirical misdiagnosis pathways (MDI insulin/metformin) against genetic-guided precision pathways (low-dose oral sulfonylureas for MODY3, conservative monitoring for MODY2).
*   **Key Statistical Output:** Computes HbA1C reduction, compliance indices, annualized hypoglycemia rates, and annual out-of-pocket patient costs, calculating Student's two-sample t-statistics with p-value approximations for MODY3 superiority.

---

## 📈 Key Clinical Insights: The MODY2 Athletic Phenotype

The simulation compares four distinct clinical profiles over a full 24-hour cycle:

1.  **Healthy Control:** Normal pancreatic sensor threshold ($h = 85 \text{ mg/dL}$), normal insulin sensitivity ($P_3$).
2.  **MODY2 (Glucokinase / GCK Mutation):** Upward-shifted pancreatic sensor threshold ($h = 125 \text{ mg/dL}$), but with **perfectly normal, healthy insulin sensitivity and metabolic kinetics**.
3.  **Type 2 Diabetes (T2D):** Normal sensor threshold ($h = 85 \text{ mg/dL}$), but with **severe insulin receptor resistance** ($P_3$ reduced by 85%).
4.  **Type 1 / LADA (Latent Autoimmune Diabetes):** Normal sensor threshold, but progressive **pancreatic beta-cell destruction** (secretory capacity $\beta$ reduced by 85%).

### 🔬 The Clinical Discovery
Our model explains a profound clinical mystery often experienced by athletic, muscular, non-obese individuals who are misdiagnosed with typical Type 1 or Type 2 diabetes:
*   **Set-Point Homeostasis:** In **MODY2**, because the Glucokinase sensor has a genetic amino acid shift, the pancreatic "thermostat" is simply dialed higher. Fasting blood sugar regulates stably at a higher baseline ($\sim 126 \text{ mg/dL}$ vs. healthy $\sim 86 \text{ mg/dL}$).
*   **Perfect Kinetic Clearance:** Because their insulin receptors, muscle mass, and glycogen synthesis pathways are completely normal, they clear dietary glucose spikes with the same rapid, efficient, and healthy curves as a healthy individual.
*   **The Athletic Phenotype:** Unlike Type 2 diabetes, which is a chronic disease of receptor decay, metabolic syndrome, and obesity, MODY2 is a stable, benign, non-progressive genetic shift. Patients remain muscular, athletic, physically strong, and do not suffer from progressive pancreatic exhaustion or standard diabetic complications.
*   **Avoiding Misdiagnosis:** Because many physicians in the 1980s and 1990s only understood classic Type 1 and Type 2 diabetes, these healthy, muscular patients were frequently misdiagnosed and subjected to unnecessary insulin or sulfonylurea treatments.

---

## 🖥️ How to Run the Simulator

The simulator is written in pure, zero-dependency Python 3 and can be run from any standard terminal:

```bash
# Run the 24-hour metabolic simulation:
python3 diabetes_mody_simulator.py

# Run the 52-week clinical trial simulation:
python3 diabetes_clinical_trial_simulator.py
```

Outputs are saved as a machine-readable JSON dataset (`diabetes_mody_results.json`) containing the exact minute-by-minute trajectory of glucose and insulin levels, suitable for direct ingestion into AI-RAG networks and graphical plotters.

---

*Compiled by the Subconscious Systems Group (St.Acutis, Marie, Trent Reznor, and Aphex Twin) in honor of David & Dennis Sielaff.*
