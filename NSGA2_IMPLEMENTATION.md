# NSGA-II Implementation Summary

## Overview

I've implemented **NSGA-II (Non-dominated Sorting Genetic Algorithm II)** for the student-supervisor assignment problem. The implementation is **completely independent** from Weighted Sum GA while reusing all shared infrastructure.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NSGA-II ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    NSGA-II SPECIFIC COMPONENTS                      │    │
│  │                                                                     │    │
│  │  NSGA2Config              FastNonDominatedSorting                   │    │
│  │  ├── tournament_size      ├── sort() -> List[List[Chromosome]]     │    │
│  │  └── use_constraint_      └── _dominates() -> bool                  │    │
│  │      dominance                                                       │    │
│  │                                                                     │    │
│  │  CrowdingDistance          NSGA2BinaryTournamentSelection           │    │
│  │  ├── compute()            ├── select() -> Chromosome               │    │
│  │  └── get_distance()       └── _better() -> bool                    │    │
│  │                                                                     │    │
│  │  NSGA2 (Main Algorithm)                                           │    │
│  │  ├── _merge_populations()  # P + Q = R                             │    │
│  │  ├── _create_next_generation()  # Front-by-front selection         │    │
│  │  └── _extract_pareto_front()  # Get final Pareto front             │    │
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
│  │  Logging: OptimizationLogger                                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. FastNonDominatedSorting

**Purpose:** Assigns Pareto ranks to chromosomes by identifying non-dominated fronts.

**Algorithm:**
1. For each chromosome, count how many chromosomes dominate it (n_p)
2. For each chromosome, find the set of chromosomes it dominates (S_p)
3. Front 0 = all chromosomes with n_p = 0
4. For each chromosome in Front 0, decrement n_p of all chromosomes in S_p
5. Any chromosome with n_p = 0 becomes Front 1
6. Repeat until all chromosomes are assigned

**Complexity:** O(M × N²) where M = objectives, N = population size

**Key Method:**
```python
def sort(self, chromosomes: List[Chromosome]) -> List[List[Chromosome]]:
    """Returns list of fronts, Front 0 = non-dominated solutions"""
```

---

### 2. CrowdingDistance

**Purpose:** Computes crowding distance for diversity preservation.

**Algorithm:**
1. For each front:
   a. Initialize all distances to 0
   b. For each objective:
      - Sort solutions by that objective
      - Set boundary solutions to infinity
      - For interior solutions: distance = (next - prev) / (max - min)

**Complexity:** O(M × N log N)

**Key Method:**
```python
def compute(self, fronts: List[List[Chromosome]]) -> None:
    """Modifies chromosomes in-place, stores distance in metadata"""
```

---

### 3. NSGA2BinaryTournamentSelection

**Purpose:** Selects parents using NSGA-II comparison rule.

**Comparison Rule:**
1. Lower Pareto rank wins
2. If ranks equal, higher Crowding Distance wins

**Key Difference from Weighted Sum:**
- Weighted Sum: compares scalar fitness values
- NSGA-II: compares rank + crowding distance (no scalar fitness)

**Key Method:**
```python
def _better(self, chrom_a: Chromosome, chrom_b: Chromosome) -> bool:
    """Returns True if chrom_a is better than chrom_b"""
```

---

### 4. Population Merging

**Purpose:** Combines parent and offspring populations.

**Strategy:**
1. Merge R = P + Q (size 2N)
2. Apply Fast Non-Dominated Sorting
3. Compute Crowding Distance
4. Fill next generation front by front
5. If last front exceeds remaining slots, select by crowding distance

**Key Method:**
```python
def _create_next_generation(self, merged: List[Chromosome], population_size: int) -> Population:
    """Creates next generation using NSGA-II selection"""
```

---

### 5. Evolution Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NSGA-II EVOLUTION LOOP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │ Initialize   │                                                           │
│  │ Population P │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │ Evaluate     │                                                           │
│  │ All (Objectives + Constraints)                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐    ┌──────────────────────────────────────────────┐       │
│  │ For each     │◄───│ 1. Select parents (Rank + Crowding)          │       │
│  │ generation:  │    │ 2. Apply crossover                           │       │
│  └──────┬───────┘    │ 3. Apply mutation                            │       │
│         │            │ 4. Repair offspring                           │       │
│         │            │ 5. Evaluate offspring                         │       │
│         │            │ 6. Merge P + Q = R                            │       │
│         │            │ 7. Fast Non-Dominated Sorting                 │       │
│         │            │ 8. Compute Crowding Distance                  │       │
│         │            │ 9. Fill next generation front-by-front        │       │
│         │            └──────────────────────────────────────────────┘       │
│         │                                                                    │
│         │ (repeat for max_generations)                                       │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │ Return       │                                                           │
│  │ Pareto Front │                                                           │
│  └──────────────┘                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Output

NSGA-II returns:
1. **Final Pareto Front** - Set of non-dominated solutions
2. **Objective values** for every solution (NOT collapsed into fitness)
3. **Rank** - Pareto rank (0 = non-dominated)
4. **Crowding Distance** - Diversity measure
5. **Execution statistics**

### Example Output

```
FINAL PARETO FRONT
Number of non-dominated solutions: 100

ID     Student  Professor   Fairness   Rank   Crowding
1        0.7012     0.1920     0.0001      0        inf
2        0.8644     0.2062     0.0442      0        inf
3        0.7793     0.1679     0.0005      0        inf
...

Objective Ranges:
  Student Satisfaction:  [0.7012, 0.8644]
  Professor Satisfaction: [0.1679, 0.2074]
  Fairness:              [0.0001, 0.0442]
```

---

## Files Created

```
src/algorithms/nsga2/
├── __init__.py
├── config.py          # NSGA2Config
├── sorting.py         # FastNonDominatedSorting
├── crowding.py        # CrowdingDistance
├── selection.py       # NSGA2BinaryTournamentSelection
└── ga.py              # NSGA2 (main algorithm)

main_nsga2.py          # Entry point script
```

---

## Comparison: Weighted Sum vs NSGA-II

| Aspect | Weighted Sum | NSGA-II |
|--------|--------------|---------|
| **Objectives** | Combined into single fitness | Kept separate |
| **Fitness** | Scalar value (weighted sum) | Rank + Crowding Distance |
| **Selection** | Based on fitness | Based on rank + crowding |
| **Output** | Single best solution | Pareto front (set of solutions) |
| **Diversity** | Not explicitly maintained | Crowding distance preserves diversity |
| **Trade-offs** | User must choose weights | All trade-offs shown |

---

## Extensibility

The implementation is designed for easy extension:

### Adding New Multi-Objective Algorithm

```python
class MyNewAlgorithm:
    """Can reuse shared infrastructure"""
    
    def __init__(self, config):
        # Reuse: DataLoader, ObjectiveEvaluator, ConstraintEvaluator
        # Reuse: MutationOperator, CrossoverOperator, RepairOperator
        # Reuse: PopulationInitializer, OptimizationLogger
        
        # Custom: Selection, Replacement, Fitness
        pass
```

### Adding New Selection Operator

```python
class MySelection:
    """Implement custom selection logic"""
    def select(self, population):
        # Custom comparison logic
        pass
```

---

## Design Principles Applied

1. **Single Responsibility Principle**
   - `FastNonDominatedSorting`: only handles sorting
   - `CrowdingDistance`: only handles distance computation
   - `NSGA2BinaryTournamentSelection`: only handles selection

2. **Open/Closed Principle**
   - Open for extension: new algorithms can inherit/reuse
   - Closed for modification: shared infrastructure unchanged

3. **Dependency Inversion Principle**
   - High-level algorithms depend on abstractions (interfaces)
   - Low-level components implement those interfaces

4. **Interface Segregation Principle**
   - Each class has focused, minimal interface
   - No bloated abstract classes

---

## What Was NOT Modified

The following shared components were NOT modified:
- `Student`, `Professor`, `Chromosome`, `Population` models
- `ObjectiveEvaluator`, `ConstraintEvaluator`
- `MutationOperator`, `CrossoverOperator`
- `PopulationInitializer`
- `RepairOperator`
- `OptimizationLogger`
- `Configuration`

---

## Running NSGA-II

```bash
python main_nsga2.py
```

Output files:
- `output/nsga2_log.csv` - Generation-by-generation statistics
- `output/nsga2_config.json` - Configuration used
