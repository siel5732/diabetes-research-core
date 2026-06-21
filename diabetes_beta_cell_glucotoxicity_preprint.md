# Pancreatic Beta-Cell Mass Long-Term Decay and Apoptosis under Glucotoxic ER Stress: A Coupled ODE Model

**In Honor of Cynthia Sielaff**

## Abstract

Chronic hyperglycemia, a hallmark of type 2 diabetes (T2D), induces glucotoxicity in pancreatic beta-cells, leading to endoplasmic reticulum (ER) stress, impaired insulin secretion, and ultimately beta-cell apoptosis and mass decay. This preprint presents a coupled system of ordinary differential equations (ODEs) designed to model the long-term physiological and cellular dynamics of beta-cell mass under chronic glucotoxic ER stress. The model integrates glucose excursions, insulin secretion capacity as a function of functional beta-cell mass, and glucose-dependent beta-cell apoptosis kinetics mediated by ER stress (Unfolded Protein Response, chaperone exhaustion, caspase activation). Simulations track these critical variables over months to years, providing a framework to understand disease progression, evaluate functional beta-cell mass preservation metrics, and explore the efficacy of various therapeutic interventions aimed at mitigating glucotoxicity and preserving beta-cell function.

## 1. Introduction

Type 2 Diabetes is characterized by insulin resistance and progressive beta-cell dysfunction. A key driver of beta-cell failure is chronic exposure to elevated glucose levels, termed glucotoxicity. Glucotoxicity leads to a cascade of cellular events, including increased oxidative stress, mitochondrial dysfunction, and critically, endoplasmic reticulum (ER) stress. Prolonged ER stress activates the Unfolded Protein Response (UPR), which initially serves a protective role but, if unresolved, can lead to chaperone exhaustion and activation of pro-apoptotic pathways, such as the caspase cascade. This ultimately results in reduced functional beta-cell mass, exacerbating hyperglycemia in a vicious cycle. Understanding these long-term dynamics is crucial for developing therapies that can truly modify disease progression.

## 2. Model Formulation

Our model describes the interplay between systemic glucose and insulin levels, and the intracellular events within beta-cells leading to their demise. It consists of six coupled ODEs:

### 2.1 Glucose Dynamics ($G$)
Systemic glucose concentration is influenced by basal production, insulin-independent elimination, and insulin-dependent uptake.

$\frac{dG}{dt} = k_{G_{prod}} - k_{G_{elim}} \cdot G - k_{G_{insulin\_dep\_elim}} \cdot I \cdot G$

Where:
- $G$: Glucose concentration.
- $k_{G_{prod}}$: Basal glucose production rate.
- $k_{G_{elim}}$: Insulin-independent glucose elimination rate constant.
- $k_{G_{insulin\_dep\_elim}}$: Insulin-dependent glucose elimination rate constant.
- $I$: Insulin concentration.

### 2.2 Insulin Dynamics ($I$)
Insulin secretion is proportional to the functional beta-cell mass ($B$) and is stimulated by glucose levels above a basal threshold. Insulin is also cleared from circulation.

$\frac{dI}{dt} = k_{I_{prod\_beta}} \cdot B \cdot (G - G_{basal}) \cdot H(G - G_{basal}) - k_{I_{elim}} \cdot I$

Where:
- $k_{I_{prod\_beta}}$: Insulin production rate constant per unit beta-cell mass.
- $B$: Functional Beta-Cell Mass.
- $G_{basal}$: Basal glucose level.
- $H()$: Heaviside step function (insulin secretion only when G > G_basal).
- $k_{I_{elim}}$: Insulin elimination rate constant.

### 2.3 ER Stress (ER_Stress)
ER stress is activated by chronic hyperglycemia (glucose levels above a threshold) and deactivates when glucose levels normalize.

$\frac{dER_{Stress}}{dt} = k_{ER_{stress\_on}} \cdot (G - G_{stress\_threshold}) \cdot H(G - G_{stress\_threshold}) - k_{ER_{stress\_off}} \cdot ER_{Stress}$

Where:
- $ER_{Stress}$: Level of ER stress.
- $G_{stress\_threshold}$: Glucose threshold for ER stress activation.
- $k_{ER_{stress\_on}}$: ER stress activation rate constant.
- $k_{ER_{stress\_off}}$: ER stress deactivation rate constant.

### 2.4 Unfolded Protein Response (UPR)
UPR is a protective response activated by ER stress, but chronic UPR can lead to chaperone exhaustion.

$\frac{dUPR}{dt} = k_{UPR_{on}} \cdot ER_{Stress} - k_{UPR_{off}} \cdot UPR - k_{chaperone\_exhaustion} \cdot UPR$

Where:
- $UPR$: Level of Unfolded Protein Response.
- $k_{UPR_{on}}$: UPR activation rate constant.
- $k_{UPR_{off}}$: UPR deactivation rate constant.
- $k_{chaperone\_exhaustion}$: Rate constant for chaperone exhaustion by UPR.

### 2.5 Caspase Activation (Caspase_Activation)
Sustained ER stress and chaperone exhaustion can lead to the activation of caspases, initiating apoptotic pathways.

$\frac{dCaspase_{Activation}}{dt} = k_{caspase\_activation} \cdot ER_{Stress}$

Where:
- $Caspase_{Activation}$: Level of Caspase Activation.
- $k_{caspase\_activation}$: Caspase activation rate constant from ER stress.

### 2.6 Functional Beta-Cell Mass (B)
Beta-cell mass decays due to apoptosis, which is exacerbated by caspase activation, and can regenerate at a basal rate towards a maximum capacity.

$\frac{dB}{dt} = k_{beta\_cell\_regeneration} \cdot (B_{max} - B) - (k_{beta\_cell\_apoptosis\_basal} + k_{beta\_cell\_apoptosis\_stress} \cdot Caspase_{Activation}) \cdot B$

Where:
- $B_{max}$: Maximum beta-cell mass.
- $k_{beta\_cell\_regeneration}$: Beta-cell regeneration rate constant.
- $k_{beta\_cell\_apoptosis\_basal}$: Basal beta-cell apoptosis rate constant.
- $k_{beta\_cell\_apoptosis\_stress}$: Stress-induced beta-cell apoptosis rate constant.

## 3. Simulation, Functional Mass Preservation, and Therapeutic Interventions

The ODE system was numerically solved over a period of months to years. Simulations illustrate the progressive decline in beta-cell mass under sustained hyperglycemia. Key insights gained:
- Chronic hyperglycemia drives ER stress, leading to UPR activation and subsequent caspase activation.
- Caspase activation significantly accelerates beta-cell apoptosis, leading to a reduction in functional beta-cell mass.
- Decreased beta-cell mass impairs insulin secretion, further exacerbating hyperglycemia, thus forming a feed-forward loop characteristic of T2D progression.

**Functional Mass Preservation Metrics:** The model allows for quantification of parameters such as:
- **Time to 50% Beta-Cell Mass Loss:** A critical indicator of disease progression.
- **Integrated Insulin Secretion Capacity:** Reflects the cumulative ability of beta-cells to secrete insulin over time.
- **Area Under the Curve (AUC) of ER Stress/Caspase Activation:** Quantifies the cumulative stress experienced by beta-cells.

**Therapeutic Interventions:** The model can be used to simulate the effects of various interventions:
- **Glucose-lowering therapies:** Reducing `G` directly can mitigate ER stress.
- **ER stress inhibitors/chaperone activators:** Modulating `k_ER_stress_on` or `k_chaperone_exhaustion` to protect cells.
- **Anti-apoptotic agents:** Reducing `k_beta_cell_apoptosis_stress` to prevent beta-cell loss.
- **Beta-cell regenerative therapies:** Increasing `k_{beta\_cell\_regeneration}` to restore mass.

These simulations provide a mechanistic understanding of T2D progression and can guide the development and optimization of multi-target therapeutic strategies aimed at preserving functional beta-cell mass and achieving long-term glycemic control.

## 4. Conclusion

This coupled ODE model provides a comprehensive framework for simulating the long-term impact of glucotoxicity and ER stress on pancreatic beta-cell mass and function. By integrating physiological and cellular mechanisms, it offers valuable insights into T2D pathogenesis and serves as a powerful tool for predicting the efficacy of various therapeutic interventions. Further refinement with experimental data will enhance its predictive power and clinical utility in the fight against diabetes.
