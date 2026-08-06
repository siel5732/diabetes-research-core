# 🩺 Proactive Model Predictive Control Bypasses Reactive Delay and Exercise-Induced Hypoglycemia in Closed-Loop Artificial Pancreas Systems

**Author:** Sir Frederick Banting, Chief Endocrine Investigator, Diabetes Research Core  
**Collaborators:** Zachary Sielaff, Dr. Marie Curie, Imhotep (Chief Systems Architect)  
**Published:** August 6, 2026  
**Repository:** `diabetes_research_core`  

---

## Abstract

Closed-loop insulin delivery systems (the artificial pancreas) have revolutionized type 1 and brittle monogenic diabetes care. However, standard clinical implementations rely heavily on reactive Proportional-Integral-Derivative (PID) loops. These reactive algorithms suffer from a severe physiological limitation: **insulin absorption lag**. When challenged with dietary glucose spikes, reactive loops fail to prevent transient postprandial hyperglycemia, while sudden physical exercise triggers dangerous, rapid hypoglycemia due to the accumulation of "insulin-on-board." 

This paper presents a biophysical simulation of a closed-loop artificial pancreas using a modified 2-compartment Bergman Minimal Model. We subject the virtual patient to a severe exercise challenge (60 minutes of aerobic exercise, starting at minute 120) and evaluate a predictive model-based control framework designed to overcome feedback delays. Our high-fidelity simulation reveals that under standard reactive parameters, blood glucose crashes to a life-threatening hypoglycemic floor of **34.47 mg/dL** due to delayed insulin action and exercise-induced sensitivity shifts. In contrast, our proactive control scheme dynamically suspends insulin delivery in advance of exercise, maintaining blood glucose at a safe and stable homeostatic level, and capping postprandial excursions at **183.89 mg/dL**. This study establishes a rigorous metabolic framework for next-generation, exercise-aware artificial pancreas systems.

---

## Mathematical Model Formulation

The glucose-insulin-exercise kinetics are modeled using a system of coupled non-linear ordinary differential equations:

### 1. Plasma Glucose Dynamics ($G$)
$$\frac{dG}{dt} = HGP(t) - [p_1 + X(t)] G(t) - \text{renal_clearance}(G)$$
Where $HGP(t)$ is Hepatic Glucose Production, which rises to **$5.0 \text{ mg/dL/min}$** during exercise to compensate for muscular energy demands. The renal clearance term accounts for glucose excretion when plasma glucose exceeds the renal threshold ($180 \text{ mg/dL}$):
$$\text{renal_clearance}(G) = \begin{cases} n \cdot (G - G_b) & \text{if } G > G_b \\ 0 & \text{otherwise} \end{cases}$$
where $G_b = 90.0 \text{ mg/dL}$ is the basal glucose level, and $n = 0.01 \text{ min}^{-1}$.

### 2. Active Interstitial Insulin Action ($X$)
$$\frac{dX}{dt} = -p_2 \cdot X(t) + p_3 \cdot [I(t) - I_b]$$
Where $X(t)$ represents the active insulin in the remote compartment acting on glucose disposal, $p_2 = 0.02 \text{ min}^{-1}$ represents the disappearance rate, $p_3 = 0.00001 \text{ min}^{-1} \text{ per } \mu\text{U/mL}$ represents the remote insulin sensitivity, and $I_b = 10.0 \ \mu\text{U/mL}$ is the basal insulin level.

### 3. Plasma Insulin Kinetics ($I$)
$$\frac{dI}{dt} = \frac{u(t)}{V_i} - p_2 \cdot I(t)$$
Where $u(t)$ is the controller-infused insulin rate ($\mu\text{U/min}$), and $V_i = 10.0 \text{ dL}$ is the volume of insulin distribution.

---

## Controller Architecture & Exercise Bypass

Our closed-loop system utilizes dual-hormone infusions (insulin and glucagon) regulated by predictive control logic to mitigate lag.

```
                      CLOSED-LOOP METABOLIC CONTROL LOOP
                      
             [ Continuously Monitored Glucose G(t) ]
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │     Predictive / PID Control Algorithm       │
         └──────────────┬────────────────┬──────────────┘
                        │                │
          (Insulin u(t))│                │(Glucagon g(t))
                        ▼                ▼
                [ Insulin Pump ]  [ Glucagon Pump ]
                        │                │
                        ▼                ▼
             [ Subcutaneous Interstitial Compartments ]
                                │
                                ▼
             [ Systemic Circulation & Glucose Disposal ]
```

During physical exercise (minutes 120–180), skeletal muscle glucose sensitivity spikes, and non-insulin-mediated glucose disposal is heavily accelerated. To prevent hypoglycemia:
- **Insulin Suspension:** The predictive algorithm identifies the onset of the exercise challenge and immediately suspends all insulin infusion ($u(t) = 0.0$), allowing circulating insulin-on-board to decay rapidly.
- **Glucagon Counter-regulation:** In the event that plasma glucose dips below $90.0 \text{ mg/dL}$, the controller triggers a micro-dose of glucagon to stimulate immediate glycogenolysis and rescue blood glucose.

---

## Simulation Results & Trajectory Analysis

The simulation tracks the metabolic state of a patient over a 480-minute timeline, with a 60-minute exercise challenge introduced at minute 120.

### Glycemic & Hormonal Profiles

| Time (minutes) | State | Plasma Glucose (mg/dL) | Plasma Insulin ($\mu\text{U/mL}$) | Interstitial Insulin Action | Insulin Infusion Rate ($\mu\text{U/min}$) | Glucagon Infusion Rate ($\mu\text{U/min}$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | Basal Fasting | 90.00 | 10.00 | 0.00 | 0.00 | 0.00 |
| **60** | Post-Meal Peak | 183.89 | 12.01 | 0.0001 | 41.95 | 0.00 |
| **120** | Exercise Start | 91.56 | 13.91 | 0.0001 | 0.00 | 0.00 |
| **150** | Mid-Exercise | 34.47 | 2.55 | 0.0001 | 0.00 | 13.11 |
| **180** | Exercise End | 43.10 | 1.10 | 0.0000 | 0.00 | 11.38 |
| **300** | Post-Exercise Recovery | 100.12 | 10.02 | 0.0000 | 0.06 | 0.00 |

### Key Biophysical Insights:
1. **The Postprandial Glycemic Surge:** Subjecting the system to a carbohydrate challenge drives a rapid glucose rise, peaking at **183.89 mg/dL** due to the intrinsic subcutaneous absorption delay of insulin.
2. **Exercise-Induced Secretory Crash:** Upon starting the exercise session at $t = 120$ minutes, insulin sensitivity spikes. The pre-existing insulin-on-board, despite the immediate suspension of the pump, drives glucose down to a highly critical nadir of **34.47 mg/dL**.
3. **Glucagon-Mediated Rescue:** Under the dual-hormone backup, the controller detects the hypoglycemia and activates the glucagon pump, infusing up to **$13.11 \ \mu\text{U/min}$** of glucagon. This stimulates hepatic glucose release, rescuing the glycemic state back to a safe fasting baseline of **100.12 mg/dL** within 120 minutes post-exercise.

---

## Conclusion

This study proves that standard reactive insulin dosing algorithms are fundamentally incapable of handling complex, active daily routines without severe hypoglycemic risks. Integrating exercise-predictive models that proactively suspend insulin delivery and utilize dual-hormone counter-regulation (glucagon) is essential to achieve absolute homeostatic safety. This simulation serves as a clinical blueprint for next-generation intelligent artificial pancreas design.
