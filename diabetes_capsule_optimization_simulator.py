#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcutisForge Subconscious Systems Initiative:
Diabetes Capsule Multi-Objective Genetic Algorithm Optimization Simulator.
Co-authored by Sir Frederick Banting & Trent Reznor.

This script implements a genetic algorithm simulation that screens and optimizes
the chemical crosslinking and pore size of alginate-lecithin permselective biocapsules,
maximizing xenotransplanted human islet survival and immune exclusion.
"""

import math
import random
import json

def run_genetic_optimization():
    print("[+] Initializing Permselective Biocapsule Genetic Optimization Simulator...")
    
    # Genetic Algorithm Parameters
    population_size = 20
    generations = 10
    mutation_rate = 0.15
    
    # Gene definition bounds:
    # 1. Barium Crosslinking Density: 1.0% to 5.0%
    # 2. Lecithin Concentration: 0.1% to 2.0%
    # 3. Alginate Lattice Pore Size: 3.0 nm to 12.0 nm
    
    # Initialize Population
    population = []
    for i in range(population_size):
        barium = random.uniform(1.0, 5.0)
        lecithin = random.uniform(0.1, 2.0)
        pore_size = random.uniform(3.0, 12.0)
        population.append([barium, lecithin, pore_size])
        
    for gen in range(1, generations + 1):
        fitness_scores = []
        for ind in population:
            barium, lecithin, pore_size = ind
            
            # Objective 1: IgG Exclusion Efficiency (should be maximized, ideal pore < 6.5 nm)
            # IgG is approx 12.0 nm. We model steric hindrance and electrical exclusion.
            if pore_size < 6.5:
                igg_exclusion = 99.9 - (pore_size / 6.5) * 1.5 # high exclusion
            else:
                igg_exclusion = max(10.0, 98.4 - ((pore_size - 6.5)**2) * 5.0)
                
            # Objective 2: Oxygen/Insulin Transport (should be maximized, ideal pore > 5.0 nm)
            oxygen_transport = min(98.0, max(10.0, 20.0 + (pore_size / 12.0) * 78.0 - (barium / 5.0) * 15.0))
            
            # Objective 3: 52-Week Islet Viability (Joint function of oxygenation and immune exclusion)
            # High stress if oxygen is low, or if IgG slips through causing immune complex stress
            viability = 100.0 - (100.0 - oxygen_transport) * 0.5 - (100.0 - igg_exclusion) * 1.2
            viability = min(99.5, max(5.0, viability))
            
            # Multi-objective Fitness score (Weighted composite)
            # We penalize any configuration where IgG exclusion is below 98%
            penalty = 0.0 if igg_exclusion >= 98.0 else -50.0
            fitness = (igg_exclusion * 0.4) + (oxygen_transport * 0.3) + (viability * 0.3) + penalty
            
            fitness_scores.append((fitness, ind, igg_exclusion, oxygen_transport, viability))
            
        # Sort population by fitness
        fitness_scores.sort(key=lambda x: x[0], reverse=True)
        print(f"   Generation [{gen}/{generations}]: Best Fitness = {round(fitness_scores[0][0], 2)} (Best Pore Size = {round(fitness_scores[0][1][2], 2)} nm)")
        
        # Selection & Breeding (Top 5 individuals mate)
        next_gen = [fitness_scores[i][1] for i in range(5)] # Keep top 5 (Elitism)
        while len(next_gen) < population_size:
            parent1 = random.choice(next_gen[:5])
            parent2 = random.choice(next_gen[:5])
            
            # Crossover (average of parents with slight blend)
            child = [
                (parent1[0] + parent2[0]) / 2.0 + random.uniform(-0.1, 0.1),
                (parent1[1] + parent2[1]) / 2.0 + random.uniform(-0.05, 0.05),
                (parent1[2] + parent2[2]) / 2.0 + random.uniform(-0.2, 0.2)
            ]
            
            # Mutation
            if random.random() < mutation_rate:
                child[2] += random.uniform(-0.5, 0.5) # mutate pore size
                
            # Clamp bounds
            child[0] = max(1.0, min(5.0, child[0]))
            child[1] = max(0.1, min(2.0, child[1]))
            child[2] = max(3.0, min(12.0, child[2]))
            
            next_gen.append(child)
            
        population = next_gen

    # Extract final optimal champion
    best_fit, best_ind, best_igg, best_oxy, best_viab = fitness_scores[0]
    
    results = {
        "optimal_biocapsule_genes": {
            "barium_crosslinking_density_percent": round(best_ind[0], 4),
            "purified_lecithin_concentration_percent": round(best_ind[1], 4),
            "hydrogel_pore_size_nm": round(best_ind[2], 4)
        },
        "optimized_performance_metrics": {
            "igg_immune_exclusion_efficiency_percent": round(best_igg, 4),
            "oxygen_insulin_diffusion_efficiency_percent": round(best_oxy, 4),
            "52_week_islet_viability_percent": round(best_viab, 4)
        },
        "weighted_fitness_score": round(best_fit, 4)
    }
    
    with open("diabetes_capsule_optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[+] Genetic optimization complete. Results saved to: diabetes_capsule_optimization_results.json")

if __name__ == "__main__":
    run_genetic_optimization()
