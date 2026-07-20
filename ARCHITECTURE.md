# Graduate Student-Supervisor Assignment Optimization System

## Architecture Documentation

This document describes the reusable infrastructure for solving the student-supervisor assignment problem using metaheuristic algorithms.

---

## Project Structure

```
project/
├── src/
│   ├── __init__.py                 # Package root
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── student.py              # Student entity
│   │   ├── professor.py            # Professor entity
│   │   ├── assignment.py           # Assignment record
│   │   ├── chromosome.py           # Solution representation
│   │   └── population.py           # Population management
│   ├── config/
│   │   ├── __init__.py
│   │   └── configuration.py        # All configuration settings
│   ├── data/
│   │   ├── __init__.py
│   │   └── excel_loader.py         # Excel data loading
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── objectives.py           # Objective functions
│   │   └── constraints.py          # Constraint evaluation
│   ├── operators/
│   │   ├── __init__.py
│   │   ├── mutation/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Abstract mutation
│   │   │   ├── random_reset.py     # Random Reset mutation
│   │   │   └── swap.py             # Swap mutation
│   │   └── crossover/
│   │       ├── __init__.py
│   │       ├── base.py             # Abstract crossover
│   │       ├── uniform.py          # Uniform crossover
│   │       └── one_point.py        # One-Point crossover
│   ├── initialization/
│   │   ├── __init__.py
│   │   └── population_initializer.py
│   ├── repair/
│   │   ├── __init__.py
│   │   └── repair_operator.py      # Solution repair
│   ├── utils/
│   │   ├── __init__.py
│   │   └── population_utils.py     # Population utilities
│   └── logging_config/
│       ├── __init__.py
│       └── logger.py               # Optimization logging
├── data/                           # Excel datasets
│   ├── Students.xlsx
│   ├── Professors.xlsx
│   ├── StudentPreferences.xlsx
│   ├── ProfessorPreferences.xlsx
│   ├── Universities.xlsx
│   └── Fields.xlsx
├── main.py                         # Demo script
├── requirements.txt
└── ARCHITECTURE.md
```

---

## UML Class Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Configuration                                                              │
│  ├── algorithm: AlgorithmConfig                                             │
│  ├── penalty: PenaltyConfig                                                 │
│  ├── data: DataConfig                                                       │
│  └── logging: LoggingConfig                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA MODELS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Student                    Professor                 Assignment            │
│  ├── student_id             ├── professor_id          ├── student_id        │
│  ├── name                   ├── name                  ├── professor_id      │
│  ├── gender                 ├── field                 ├── field_match       │
│  ├── field                  ├── academic_rank         ├── student_rank      │
│  ├── quality_score          ├── capacity              └── professor_rank    │
│  └── preference_list        └── preference_list                            │
│                                                                             │
│  Chromosome                      Population                                │
│  ├── genes: List[str]           ├── chromosomes: List[Chromosome]          │
│  ├── student_ids: List[str]     ├── generation: int                        │
│  ├── objectives: ObjectiveValues├── compute_statistics()                   │
│  ├── constraints: ConstraintValues└── get_best()                           │
│  └── fitness: float                                                       │
│                                                                             │
│  ObjectiveValues               ConstraintValues                             │
│  ├── student_satisfaction      ├── capacity_violation                      │
│  ├── professor_satisfaction    ├── field_mismatch_count                     │
│  └── fairness                  └── total_penalty                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LOADING                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  DataLoader                                                                 │
│  ├── __init__(config: DataConfig)                                           │
│  ├── load_all() -> Tuple[List[Student], List[Professor]]                   │
│  └── validate_consistency()                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVALUATION                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ObjectiveEvaluator             ConstraintEvaluator                         │
│  ├── evaluate(chromosome)       ├── evaluate(chromosome)                   │
│  │   -> ObjectiveValues         │   -> ConstraintValues                    │
│  ├── _compute_student_sat()     ├── _compute_capacity_violation()          │
│  ├── _compute_professor_sat()   ├── _compute_field_mismatch()              │
│  └── _compute_fairness()        └── is_feasible()                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPERATORS (Strategy Pattern)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  MutationOperator (ABC)           CrossoverOperator (ABC)                   │
│  ├── mutate()                     ├── crossover()                          │
│  └── get_name()                   └── get_name()                           │
│         │                                │                                  │
│         ▼                                ▼                                  │
│  ┌──────────────┐                ┌──────────────┐                          │
│  │RandomReset   │                │Uniform       │                          │
│  │Mutation      │                │Crossover     │                          │
│  └──────────────┘                └──────────────┘                          │
│  ┌──────────────┐                ┌──────────────┐                          │
│  │Swap          │                │OnePoint      │                          │
│  │Mutation      │                │Crossover     │                          │
│  └──────────────┘                └──────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     INITIALIZATION & REPAIR                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  PopulationInitializer            RepairOperator                            │
│  ├── initialize()                 ├── repair()                             │
│  ├── create_random()              ├── _repair_capacity()                   │
│  ├── create_field_biased()        └── _find_best_target()                  │
│  └── create_from_preference()                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     UTILITIES & LOGGING                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PopulationUtils                  OptimizationLogger                        │
│  ├── sort_population()            ├── start()                              │
│  ├── select_random()              ├── log_generation()                     │
│  ├── select_by_fitness()          ├── log_event()                          │
│  ├── compute_diversity()          └── finish()                             │
│  └── truncate_population()                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Class Descriptions

### 1. Data Models (`src/models/`)

#### Student
**Purpose:** Represents a graduate student entity.

**Why it exists:** Encapsulates all student data and provides methods for preference lookup.

**Key methods:**
- `get_preference_rank(professor_id)`: Get rank of professor in preference list
- `has_preference(professor_id)`: Check if professor is in preference list

---

#### Professor
**Purpose:** Represents a professor/supervisor entity.

**Why it exists:** Encapsulates all professor data and provides methods for preference lookup.

**Key methods:**
- `get_preference_rank(student_id)`: Get rank of student in preference list
- `has_preference(student_id)`: Check if student is in preference list

---

#### Assignment
**Purpose:** Immutable record of a single student-professor assignment.

**Why it exists:** Provides a clean data structure for storing final results.

---

#### Chromosome
**Purpose:** Represents a complete solution (all assignments).

**Why it exists:** Core solution representation for genetic algorithms.

**Key methods:**
- `get_assignment(student_index)`: Get professor for student
- `set_assignment(student_index, professor_id)`: Update assignment
- `deep_copy()`: Create independent copy
- `count_professor_assignments()`: Count students per professor
- `to_assignment_dict()`: Convert to dictionary
- `pretty_print()`: Human-readable output

---

#### Population
**Purpose:** Manages a collection of chromosomes.

**Why it exists:** Provides population-level operations and statistics.

**Key methods:**
- `add(chromosome)`: Add to population
- `get_best()`: Get best chromosome
- `compute_statistics()`: Calculate population metrics
- `deep_copy()`: Create independent copy

---

### 2. Configuration (`src/config/`)

#### Configuration
**Purpose:** Centralizes all system settings.

**Why it exists:** Follows Single Responsibility - configuration is separate from logic.

**Key methods:**
- `from_json(filepath)`: Load from file
- `to_json(filepath)`: Save to file
- `validate()`: Check all settings

---

### 3. Data Loading (`src/data/`)

#### DataLoader
**Purpose:** Reads Excel files and creates domain objects.

**Why it exists:** Separates data access from business logic.

**Key methods:**
- `load_all()`: Load all datasets
- `validate_consistency()`: Check data integrity

---

### 4. Evaluation (`src/evaluation/`)

#### ObjectiveEvaluator
**Purpose:** Computes objective function values.

**Why it exists:** Separates objective computation from algorithm logic.

**Key methods:**
- `evaluate(chromosome)`: Compute all objectives
- `compute_student_satisfaction_single()`: Single assignment satisfaction
- `compute_professor_satisfaction_single()`: Single assignment satisfaction

---

#### ConstraintEvaluator
**Purpose:** Computes constraint violations.

**Why it exists:** Separates constraint checking from objective computation.

**Key methods:**
- `evaluate(chromosome)`: Compute all constraint violations
- `is_feasible(chromosome)`: Check if solution is valid
- `get_violating_professors()`: Find constraint violators

---

### 5. Operators (`src/operators/`)

#### MutationOperator (ABC)
**Purpose:** Abstract base for mutation strategies.

**Why it exists:** Enables Strategy Pattern for interchangeable operators.

**Implementations:**
- `RandomResetMutation`: Replace genes randomly
- `SwapMutation`: Swap two genes

---

#### CrossoverOperator (ABC)
**Purpose:** Abstract base for crossover strategies.

**Why it exists:** Enables Strategy Pattern for interchangeable operators.

**Implementations:**
- `UniformCrossover`: Gene-by-gene selection
- `OnePointCrossover`: Single crossover point

---

### 6. Initialization (`src/initialization/`)

#### PopulationInitializer
**Purpose:** Creates initial population of chromosomes.

**Why it exists:** Separates population creation from algorithm logic.

**Key methods:**
- `initialize(population_size)`: Create full population
- `create_random()`: Single random chromosome
- `create_field_biased()`: Field-matching biased chromosome
- `create_from_preference()`: Preference-based chromosome

---

### 7. Repair (`src/repair/`)

#### RepairOperator
**Purpose:** Fixes infeasible solutions.

**Why it exists:** Maintains solution feasibility after genetic operations.

**Key methods:**
- `repair(chromosome)`: Attempt to repair
- `repair_capacity()`: Fix capacity violations
- `repair_field_mismatch()`: Improve field matching

---

### 8. Utilities (`src/utils/`)

#### Population Utilities
**Purpose:** Reusable population operations.

**Why it exists:** Common operations shared across algorithms.

**Key functions:**
- `sort_population()`: Sort by criteria
- `select_random()`: Random selection
- `compute_diversity()`: Measure genetic diversity
- `truncate_population()`: Keep best N

---

### 9. Logging (`src/logging_config/`)

#### OptimizationLogger
**Purpose:** Records optimization progress.

**Why it exists:** Separates logging from algorithm logic.

**Key methods:**
- `start()`: Begin timing
- `log_generation()`: Record generation stats
- `finish()`: Write final results

---

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)
Each class has one responsibility:
- `Student`: Student data
- `ObjectiveEvaluator`: Objective computation
- `ConstraintEvaluator`: Constraint checking
- `DataLoader`: Data loading
- `RepairOperator`: Solution repair

### 2. Open/Closed Principle (OCP)
Operators are open for extension (new implementations) but closed for modification:
```python
# Adding a new mutation is easy:
class InversionMutation(MutationOperator):
    def mutate(self, chromosome, professor_ids):
        # New implementation
        pass
```

### 3. Dependency Inversion Principle (DIP)
High-level modules depend on abstractions:
```python
class GeneticAlgorithm:
    def __init__(self, mutation: MutationOperator, crossover: CrossoverOperator):
        # Depends on abstractions, not concrete classes
        self.mutation = mutation
        self.crossover = crossover
```

### 4. Interface Segregation Principle (ISP)
Classes have focused interfaces - no bloated abstract classes.

### 5. Liskov Substitution Principle (LSP)
Any `MutationOperator` subclass can be used wherever `MutationOperator` is expected.

---

## Relationships Between Classes

```
Configuration ──uses──> DataConfig ──used by──> DataLoader
                                     │
                                     ▼
                               Student, Professor
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ObjectiveEvaluator  ConstraintEvaluator  PopulationInitializer
                    │                │                │
                    └────────┬───────┘                │
                             ▼                        ▼
                         Chromosome ◄─────────────── Population
                             │
                             ▼
                    ┌───────┴───────┐
                    ▼               ▼
            MutationOperator  CrossoverOperator
                    │               │
                    ▼               ▼
            RandomResetMutation  UniformCrossover
            SwapMutation         OnePointCrossover
                    
RepairOperator ──uses──> ConstraintEvaluator
OptimizationLogger ──logs──> Population
```

---

## What is NOT Implemented (Algorithm Layer)

The following belong to the algorithm layer and will be implemented later:

1. **Weighted Sum Fitness Calculation** - Combines objectives with weights
2. **Pareto Ranking** - NSGA-II front assignment
3. **Crowding Distance** - NSGA-II diversity preservation
4. **Tournament Selection** - Parent selection
5. **Population Replacement** - Survivor selection
6. **Algorithm Main Loop** - Generation cycle

These are intentionally excluded to keep the infrastructure reusable across both Weighted Sum GA and NSGA-II.

---

## How to Extend

### Adding a New Mutation Operator

```python
from src.operators.mutation.base import MutationOperator

class MyCustomMutation(MutationOperator):
    def mutate(self, chromosome, professor_ids):
        # Your implementation
        return mutated_chromosome
    
    def get_name(self):
        return "MyCustomMutation"
```

### Adding a New Objective

```python
# In src/evaluation/objectives.py, add:
def _compute_new_objective(self, chromosome):
    # Your computation
    return value

# Update ObjectiveValues dataclass to include new field
```

### Adding a New Constraint

```python
# In src/evaluation/constraints.py, add:
def _compute_new_constraint(self, chromosome):
    # Your computation
    return violation_value

# Update ConstraintValues dataclass to include new field
```

---

## Running the Demo

```bash
# Ensure data files exist in data/ directory
python main.py
```

---

## Next Steps

1. Implement Weighted Sum GA using this infrastructure
2. Implement NSGA-II using this infrastructure
3. Compare results
4. Tune parameters
5. Generate final report
