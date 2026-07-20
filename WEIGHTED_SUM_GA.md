# Weighted Sum Genetic Algorithm - Implementation

## Overview

The Weighted Sum GA combines multiple objectives into a single fitness value using weighted summation, then applies standard GA operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WEIGHTED SUM GA ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    ALGORITHM-SPECIFIC COMPONENTS                    │    │
│  │                                                                     │    │
│  │  WeightedSumConfig          WeightedSumFitness                      │    │
│  │  ├── weights: [w1,w2,w3]   ├── compute_fitness()                   │    │
│  │  ├── constraint_weight      │   = w1*student + w2*prof              │    │
│  │  ├── preserve_elitism       │     + w3*(1-fairness)                 │    │
│  │  └── tournament_size        │     - penalty                         │    │
│  │                             └──────────────────────────────────────│    │
│  │                                                                     │    │
│  │  BinaryTournamentSelection   ElitistReplacement                     │    │
│  │  ├── select()                ├── create_next_generation()           │    │
│  │  └── select_pair()           └── get_elites()                       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SHARED INFRASTRUCTURE (Reused)                    │    │
│  │                                                                     │    │
│  │  Models: Student, Professor, Chromosome, Population                 │    │
│  │  Evaluation: ObjectiveEvaluator, ConstraintEvaluator                │    │
│  │  Operators: MutationOperator, CrossoverOperator                     │    │
│  │  Initialization: PopulationInitializer                              │    │
│  │  Repair: RepairOperator                                             │    │
│  │  Utils: PopulationUtils                                             │    │
│  │  Logging: OptimizationLogger                                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Algorithm Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ALGORITHM FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │ Load Data    │                                                           │
│  │ (Excel files)│                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │ Initialize   │                                                           │
│  │ Population   │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐    ┌──────────────────────────────────────────────┐       │
│  │ Evaluate     │◄───│ 1. Compute objectives (3 values)             │       │
│  │ Chromosomes  │    │ 2. Compute constraints (capacity, field)     │       │
│  └──────┬───────┘    │ 3. Compute fitness (weighted sum)            │       │
│         │            └──────────────────────────────────────────────┘       │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │ For each     │                                                           │
│  │ generation:  │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Select       │ Binary Tournament Selection                       │    │
│  │  │ Parents      │ (fitness-based)                                   │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Apply        │ Uniform Crossover                                 │    │
│  │  │ Crossover    │ (prob=0.8)                                        │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Apply        │ Random Reset + Swap Mutation                      │    │
│  │  │ Mutation     │ (prob=0.1)                                        │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Repair       │ Fix capacity violations                           │    │
│  │  │ Offspring    │                                                   │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Evaluate     │ Same as initial evaluation                        │    │
│  │  │ Offspring    │                                                   │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌──────────────┐                                                   │    │
│  │  │ Create       │ Elitist Replacement                               │    │
│  │  │ Next Gen     │ (preserve top 2)                                  │    │
│  │  └──────┬───────┘                                                   │    │
│  │         │                                                            │    │
│  └─────────┼───────────────────────────────────────────────────────────┘    │
│            │                                                                │
│            │ (repeat for max_generations)                                   │
│            │                                                                │
│            ▼                                                                │
│  ┌──────────────┐                                                           │
│  │ Return Best  │                                                           │
│  │ Solution     │                                                           │
│  └──────────────┘                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. WeightedSumConfig

**Purpose:** Configuration specific to Weighted Sum approach.

**Attributes:**
- `weights`: List of weights for [student_sat, professor_sat, fairness]
- `constraint_weight`: Weight for constraint penalty
- `preserve_elitism`: Number of best individuals to preserve
- `tournament_size`: Number of individuals in tournament selection

**Why separate from base config?**
- NSGA-II doesn't need weights (uses Pareto dominance)
- Keeps algorithm-specific settings isolated

### 2. WeightedSumFitness

**Purpose:** Computes scalar fitness by combining objectives with weights.

**Formula:**
```
fitness = w1 * student_sat + w2 * prof_sat + w3 * (1 - fairness) - penalty
```

**Why separate from ObjectiveEvaluator?**
- ObjectiveEvaluator computes raw objectives (shared)
- WeightedSumFitness combines them (algorithm-specific)
- NSGA-II will have its own fitness calculation

### 3. BinaryTournamentSelection

**Purpose:** Selects parents based on fitness.

**How it works:**
1. Sample `tournament_size` individuals
2. Return the one with highest fitness

**Why binary tournament?**
- Simple to implement
- Provides selection pressure without fitness normalization
- Works with negative fitness values
- Can be adapted for NSGA-II (Pareto rank + crowding)

### 4. ElitistReplacement

**Purpose:** Creates next generation preserving best individuals.

**How it works:**
1. Sort current population by fitness
2. Take top `preserve_count` as elites
3. Fill remaining with offspring
4. If not enough offspring, add from current population

**Why elitism?**
- Ensures best solution never degrades
- Provides convergence guarantee
- Critical for Weighted Sum (fitness can fluctuate)

## Results

### Configuration
- Population: 100
- Generations: 200
- Crossover: 0.8
- Mutation: 0.1
- Weights: [0.4, 0.4, 0.2]

### Results
```
Best Fitness: 0.579205
Student Satisfaction: 0.7472 (74.72%)
Professor Satisfaction: 0.2074 (20.74%)
Fairness: 0.0132 (very fair)
Capacity Violations: 0
Field Mismatches: 0
```

### Analysis
- All 60 students assigned to matching field professors
- All professor capacity constraints satisfied
- High student satisfaction (74.72%)
- Low professor satisfaction (20.74%) - expected since professor preferences are less prioritized
- Excellent fairness (0.0132) - quality distributed evenly

## Files Created

```
src/algorithms/
├── __init__.py
└── weighted_sum/
    ├── __init__.py
    ├── config.py          # WeightedSumConfig
    ├── fitness.py         # WeightedSumFitness
    ├── selection.py       # BinaryTournamentSelection
    ├── replacement.py     # ElitistReplacement
    └── ga.py              # WeightedSumGA (main algorithm)
```

## Ready for NSGA-II

The architecture is designed for easy NSGA-II inheritance:

1. **Inherit from WeightedSumGA** - reuse shared infrastructure
2. **Override `_compute_fitness()`** - use Pareto-based fitness
3. **Override `_select_parents()`** - use rank + crowding selection
4. **Override `_create_next_generation()`** - use non-dominated sorting

Example NSGA-II skeleton:
```python
class NSGA2(WeightedSumGA):
    def _compute_fitness(self, chromosome):
        # NSGA-II uses rank + crowding, not weighted sum
        pass
    
    def _select_parents(self, population):
        # Select based on Pareto rank + crowding distance
        pass
    
    def _create_next_generation(self, current, offspring):
        # Use non-dominated sorting + crowding
        pass
```
