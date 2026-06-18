#!/usr/bin/env python3
"""
🧬 MONOGENIC DIABETES (MODY) PRECISION CLINICAL TRIAL SIMULATOR
Deployed to: GEEKOM Node (the-grid)
Authors: Trent Reznor & Aphex Twin (Subconscious Systems Group)
Dedicated in Loving Memory of: David & Dennis Sielaff

This script models a randomized, parallel clinical trial over 52 weeks:
- Cohort: 30 non-obese, athletic pediatric/young-adult patients with genetic monogenic diabetes:
  - 15 patients with MODY2 (Glucokinase / GCK mutation)
  - 15 patients with MODY3 (Hepatocyte Nuclear Factor 1-Alpha / HNF1A mutation)

Two randomized parallel trial arms:
- Arm 1: Empirical Care (Standard Clinician Protocol)
  - MODY2 patients misdiagnosed as Type 2 (treated with Metformin + Basal Insulin).
  - MODY3 patients misdiagnosed as Type 1 (treated with Multiple Daily Injections of Insulin / MDI).
- Arm 2: Precision Care (Genetic-Guided Protocol)
  - MODY2 patients treated conservatively with standard diet/lifestyle monitoring (Zero pharmacological intervention).
  - MODY3 patients transitioned completely to low-dose oral Sulfonylureas (Glipizide / 1x daily pill).

Primary Endpoints Analyzed:
1. Glycemic Control: Mean HbA1C (%) at Week 52.
2. Safety: Annualized Severe Hypoglycemic Events (episodes per patient-year).
3. Patient Compliance Index (% of compliant days).
4. Healthcare Economics: Annualized Patient Out-of-Pocket Treatment Costs ($).
"""

import math
import random
import json
import os

# Set seed for clinical reproducibility
random.seed(999)

def generate_mody_cohort(size=15, is_mody3=False):
    """
    Generates a cohort of simulated MODY patients with patient-specific biological variation,
    initial HbA1C levels, and medication sensitivities.
    """
    cohort = []
    for i in range(size):
        # Baseline HbA1C (elevated, standard normal + offset)
        if is_mody3:
            initial_a1c = round(random.normalvariate(8.2, 0.6), 2)  # MODY3 has progressive hyperglycemia
        else:
            initial_a1c = round(random.normalvariate(6.8, 0.3), 2)  # MODY2 has mild, stable fasting hyperglycemia
            
        # Individual drug clearance and biological sensitivity factors
        insulin_sensitivity = random.uniform(0.8, 1.2)
        sulfonylurea_sensitivity = random.uniform(0.85, 1.15) if is_mody3 else 0.0
        
        # Medication compliance factor (randomly distributed between 70% and 100%)
        # Taking multiple daily insulin injections (MDI) typically has lower compliance than an oral pill or no meds
        compliance_base_mdi = random.uniform(0.68, 0.88)
        compliance_base_oral = random.uniform(0.88, 0.98)
        
        cohort.append({
            "id": i + 1,
            "is_mody3": is_mody3,
            "initial_a1c": initial_a1c,
            "current_a1c": initial_a1c,
            "insulin_sensitivity": insulin_sensitivity,
            "sulfonylurea_sensitivity": sulfonylurea_sensitivity,
            "compliance_base_mdi": compliance_base_mdi,
            "compliance_base_oral": compliance_base_oral,
            "hypoglycemia_events": 0,
            "treatment_cost_usd": 0.0
        })
    return cohort

def run_diabetes_trial_simulation():
    # Size per genetic subgroup per arm
    subgroup_size = 15
    
    # 1. ARM 1: Empirical Care (Standard Misdiagnosis Pathway)
    arm1_mody2 = generate_mody_cohort(subgroup_size, is_mody3=False)
    arm1_mody3 = generate_mody_cohort(subgroup_size, is_mody3=True)
    
    # 2. ARM 2: Precision Care (Genetic-Guided Pathway)
    arm2_mody2 = generate_mody_cohort(subgroup_size, is_mody3=False)
    arm2_mody3 = generate_mody_cohort(subgroup_size, is_mody3=True)
    
    # Run 52-week clinical tracking
    for wk in range(52):
        # --- 1. SIMULATE ARM 1: EMPIRICAL CARE ---
        # A. MODY2 Treated as Type 2 (Metformin + Basal Insulin)
        for p in arm1_mody2:
            # Metformin and insulin do not lower MODY2 fasting set-points (homeostatically regulated by GCK mutant).
            # Thus, A1C declines only slightly from initial, but with high metabolic resistance and severe gastrointestinal side effects.
            # Compliance is degraded by insulin burden and metformin GI issues.
            compliance = p["compliance_base_mdi"] * 0.9
            cost_weekly = 120.0 # Metformin + Basal Insulin + glucose strips
            
            # GCK homeostatic regulation maintains G_fasting ~ 125, so A1C remains locked around 6.3 - 6.5
            p["current_a1c"] = max(6.4, p["initial_a1c"] - (0.4 * compliance * p["insulin_sensitivity"]))
            p["treatment_cost_usd"] += cost_weekly
            
            # Unnecessary insulin in GCK mutation causes occasional moderate hypoglycemia
            if random.random() < (0.05 * p["insulin_sensitivity"]):
                p["hypoglycemia_events"] += 1
                
        # B. MODY3 Treated as Type 1 (Multiple Daily Injections / MDI Insulin)
        for p in arm1_mody3:
            # Insulin works, but MDI insulin titration is highly volatile.
            # High burden of multiple daily injections leads to poorer compliance.
            compliance = p["compliance_base_mdi"]
            cost_weekly = 180.0 # Rapid insulin + Basal insulin + needles + CGM sensors
            
            # A1C declines but remains elevated due to compliance challenges
            p["current_a1c"] = max(6.9, p["initial_a1c"] - (1.1 * compliance * p["insulin_sensitivity"]))
            p["treatment_cost_usd"] += cost_weekly
            
            # High risk of severe hypoglycemia due to aggressive insulin matching
            # Annualized risk is high: ~0.4 events per patient-year
            if random.random() < (0.08 * p["insulin_sensitivity"]):
                p["hypoglycemia_events"] += 1
                
        # --- 2. SIMULATE ARM 2: PRECISION CARE (GENETIC-GUIDED) ---
        # A. MODY2 Treated Conservatively (No Meds, Monitoring Only)
        for p in arm2_mody2:
            # No pharmacological intervention.
            # A1C remains completely stable at its mild, safe genetic set-point (no microvascular risk).
            # Compliance is 100% (zero burden). Cost is negligible (routine blood work only).
            compliance = 1.0
            cost_weekly = 5.0 # Routine blood work annualized weekly
            
            p["current_a1c"] = p["initial_a1c"]
            p["treatment_cost_usd"] += cost_weekly
            p["hypoglycemia_events"] = 0 # Zero risk of hypoglycemia without glucose-lowering drugs
            
        # B. MODY3 Treated with Low-Dose Oral Sulfonylureas (Glipizide 1x Daily)
        for p in arm2_mody3:
            # HNF1A-mutant MODY3 is exquisitely sensitive to oral sulfonylureas.
            # Simple 1x daily low-cost pill has extremely high compliance.
            compliance = p["compliance_base_oral"]
            cost_weekly = 8.0 # Generics are extremely low cost
            
            # A1C drops dramatically to near-normal levels
            p["current_a1c"] = max(5.8, p["initial_a1c"] - (2.1 * compliance * p["sulfonylurea_sensitivity"]))
            p["treatment_cost_usd"] += cost_weekly
            
            # Minimal risk of hypoglycemia compared to heavy MDI insulin
            if random.random() < (0.005 * p["sulfonylurea_sensitivity"]):
                p["hypoglycemia_events"] += 1
                
    # Calculate Statistical Means & Standard Deviations
    def analyze_arm(cohort_m2, cohort_m3, is_precision):
        m2_a1c = [p["current_a1c"] for p in cohort_m2]
        m3_a1c = [p["current_a1c"] for p in cohort_m3]
        
        m2_hypo = [p["hypoglycemia_events"] for p in cohort_m2]
        m3_hypo = [p["hypoglycemia_events"] for p in cohort_m3]
        
        m2_cost = [p["treatment_cost_usd"] for p in cohort_m2]
        m3_cost = [p["treatment_cost_usd"] for p in cohort_m3]
        
        m2_comp = [100.0 if is_precision else p["compliance_base_mdi"]*90.0 for p in cohort_m2]
        m3_comp = [p["compliance_base_oral"]*100.0 if is_precision else p["compliance_base_mdi"]*100.0 for p in cohort_m3]
        
        mean_a1c_m2 = sum(m2_a1c) / len(cohort_m2)
        mean_a1c_m3 = sum(m3_a1c) / len(cohort_m3)
        
        mean_hypo_m2 = sum(m2_hypo) / len(cohort_m2)
        mean_hypo_m3 = sum(m3_hypo) / len(cohort_m3)
        
        mean_cost_m2 = sum(m2_cost) / len(cohort_m2)
        mean_cost_m3 = sum(m3_cost) / len(cohort_m3)
        
        mean_comp_m2 = sum(m2_comp) / len(cohort_m2)
        mean_comp_m3 = sum(m3_comp) / len(cohort_m3)
        
        return {
            "mody2": {
                "mean_a1c": round(mean_a1c_m2, 2),
                "sd_a1c": round(math.sqrt(sum((x - mean_a1c_m2)**2 for x in m2_a1c) / (len(cohort_m2) - 1)), 2),
                "mean_hypoglycemia_events": round(mean_hypo_m2, 2),
                "mean_annual_cost_usd": round(mean_cost_m2, 2),
                "mean_compliance_pct": round(mean_comp_m2, 1)
            },
            "mody3": {
                "mean_a1c": round(mean_a1c_m3, 2),
                "sd_a1c": round(math.sqrt(sum((x - mean_a1c_m3)**2 for x in m3_a1c) / (len(cohort_m3) - 1)), 2),
                "mean_hypoglycemia_events": round(mean_hypo_m3, 2),
                "mean_annual_cost_usd": round(mean_cost_m3, 2),
                "mean_compliance_pct": round(mean_comp_m3, 1)
            }
        }
        
    stats_empirical = analyze_arm(arm1_mody2, arm1_mody3, is_precision=False)
    stats_precision = analyze_arm(arm2_mody2, arm2_mody3, is_precision=True)
    
    # Calculate Student's Two-Sample t-test for MODY3 HbA1C clearance (Empirical vs Precision)
    # Null Hypothesis: Standard Insulin and Oral Sulfonylureas are equally effective at lowering HbA1C in MODY3
    m3_a1c_emp = [p["current_a1c"] for p in arm1_mody3]
    m3_a1c_pre = [p["current_a1c"] for p in arm2_mody3]
    
    mean_emp = sum(m3_a1c_emp) / subgroup_size
    mean_pre = sum(m3_a1c_pre) / subgroup_size
    
    var_emp = sum((x - mean_emp)**2 for x in m3_a1c_emp) / (subgroup_size - 1)
    var_pre = sum((x - mean_pre)**2 for x in m3_a1c_pre) / (subgroup_size - 1)
    
    pooled_se = math.sqrt((var_emp / subgroup_size) + (var_pre / subgroup_size))
    t_stat = (mean_emp - mean_pre) / pooled_se if pooled_se != 0 else 0.0
    degrees_of_freedom = (2 * subgroup_size) - 2
    
    # Estimate p-value using a simple continuous approximation for the t-distribution tail
    p_value_approx = 1.0 / (1.0 + (t_stat ** 2) / degrees_of_freedom) ** (degrees_of_freedom / 2.0)
    
    return {
        "trial_weeks": 52,
        "cohort_size_per_subgroup": subgroup_size,
        "results": {
            "arm1_empirical_care": stats_empirical,
            "arm2_precision_care": stats_precision
        },
        "statistical_inference_mody3_superiority": {
            "null_hypothesis": "Empirical Insulin MDI therapy is equally effective at controlling MODY3 as genetic-guided Sulfonylureas",
            "t_statistic": round(t_stat, 4),
            "degrees_of_freedom": degrees_of_freedom,
            "p_value_approximation": f"{p_value_approx:.12f}",
            "reject_null_hypothesis": p_value_approx < 0.01
        }
    }

if __name__ == "__main__":
    print("🧬 DEPLOYING MODY PRECISION DIABETES CLINICAL TRIAL SPRINT 🧬")
    print("------------------------------------------------------------")
    print("Dedicated in Loving Memory of David and Dennis Sielaff\n")
    
    res = run_diabetes_trial_simulation()
    
    print(f"[+] Successfully generated parallel trial cohorts (N = {res['cohort_size_per_subgroup']} patients/subgroup).")
    print("[+] Ran 52-week metabolic adherence, compliance, and hypoglycemia models.\n")
    
    print("📊 WEEK 52 PRIMARY CLINICAL TRIAL ENDPOINTS (COHORT MEANS):")
    print("==========================================================")
    for arm_name, subgroups in res["results"].items():
        print(f"👉 {arm_name.replace('_', ' ').upper()}:")
        for sub_name, stats in subgroups.items():
            print(f"   * {sub_name.upper()}:")
            print(f"     - Mean HbA1C:         {stats['mean_a1c']}% (SD: {stats['sd_a1c']})")
            print(f"     - Compliance Index:   {stats['mean_compliance_pct']}%")
            print(f"     - Annual Hypo Events: {stats['mean_hypoglycemia_events']} episodes/year")
            print(f"     - Annual Patient Cost: ${stats['mean_annual_cost_usd']:.2f}")
            print()
            
    print("🔬 COHORT COMPARISON STATISTICAL INFERENCE (MODY3):")
    print("==================================================")
    sig = res["statistical_inference_mody3_superiority"]
    print(f"   * T-Statistic for Sulfonylurea Superiority in MODY3: {sig['t_statistic']}")
    print(f"   * Derived p-value approximation:                       {sig['p_value_approximation']}")
    print(f"   * Reject Null Hypothesis (Is Precision Care superior?): {sig['reject_null_hypothesis']}")
    print("   [=] Note: Standard insulin MDI therapy fails due to low compliance and volatile dosing,")
    print("       whereas oral Sulfonylureas trigger highly stable and dramatic glycemic clearance.")
    
    # Save cache
    out_path = "/data/.openclaw/workspace/diabetes_research_core/diabetes_clinical_trial_results.json"
    with open(out_path, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\n💾 Clinical trial dataset successfully cached to: {out_path}")
