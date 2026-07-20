# Algorithm Comparison Framework

## Overview

A lightweight, reusable framework for comparing Weighted Sum GA and NSGA-II algorithms. Designed for master's thesis with focus on simplicity and reproducibility.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ALGORITHM COMPARISON FRAMEWORK                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    COMPARISON MODULES                                │    │
│  │                                                                     │    │
│  │  ExperimentRunner        StatisticalSummary                         │    │
│  │  ├── run_weighted_sum()  ├── compute()                             │    │
│  │  ├── run_nsga2()         ├── compute_all()                         │    │
│  │  └── run_both()          └── format_summary()                      │    │
│  │                                                                     │    │
│  │  MannWhitneyTest         ComparisonVisualizer                       │    │
│  │  ├── test()              ├── create_box_plots()                    │    │
│  │  └── compare_all_        ├── create_pareto_front_plot()            │    │
│  │      metrics()           ├── create_comparison_bar_chart()         │    │
│  │                         └── create_execution_time_comparison()     │    │
│  │                                                                     │    │
│  │  ComparisonReport        RunMetrics / ComparisonMetrics            │    │
│  │  ├── save_raw_data()     ├── to_dict()                             │    │
│  │  ├── save_summary()      ├── get_values()                          │    │
│  │  ├── save_statistical_   └── add_run()                             │    │
│  │  │   tests()                                                     │    │
│  │  └── generate_text_                                                │    │
│  │      report()                                                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    REUSED INFRASTRUCTURE                             │    │
│  │                                                                     │    │
│  │  WeightedSumGA             NSGA2                                    │    │
│  │  ├── run()                 ├── run()                                │    │
│  │  └── get_best_solution()   └── get_pareto_front()                  │    │
│  │                                                                     │    │
│  │  Configuration             DataLoader                               │    │
│  │  ObjectiveEvaluator        ConstraintEvaluator                     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Files Created

```
src/comparison/
├── __init__.py
├── metrics.py              # RunMetrics, ComparisonMetrics
├── experiment_runner.py    # ExperimentRunner
├── statistics.py           # StatisticalSummary
├── statistical_test.py     # MannWhitneyTest
├── visualization.py        # ComparisonVisualizer
└── report.py               # ComparisonReport

main_comparison.py          # Entry point
```

---

## Components

### 1. RunMetrics

Stores metrics from a single algorithm run.

**Attributes:**
- Algorithm name, run ID, seed
- Execution time
- Student/Professor satisfaction, Fairness
- Capacity/Field penalties
- Best fitness (Weighted Sum)
- Pareto front (NSGA-II)

### 2. ComparisonMetrics

Aggregates metrics from multiple runs.

**Methods:**
- `add_run(metrics)`: Add a run's results
- `get_values(metric_name)`: Get values across all runs

### 3. ExperimentRunner

Runs both algorithms multiple times.

**Methods:**
- `run_weighted_sum()`: Run Weighted Sum GA N times
- `run_nsga2()`: Run NSGA-II N times
- `run_both()`: Run both algorithms

**Design:**
- Uses fresh Configuration for each run
- Disables logging during experiments
- Collects standardized metrics

### 4. StatisticalSummary

Computes descriptive statistics.

**Statistics:**
- Median (primary)
- Q1, Q3 (quartiles)
- Mean, Std (optional)

**Note:** As recommended by Thomas Weise:
> "Don't trust arithmetic mean or standard deviation"

### 5. MannWhitneyTest

Non-parametric statistical test.

**Method:**
- `test(group1, group2, metric_name)`: Compare two groups
- `compare_all_metrics(...)`: Compare multiple metrics

**Output:**
- U statistic
- p-value
- Significance (α = 0.05)

### 6. ComparisonVisualizer

Generates publication-quality plots.

**Plots:**
- Box plots for each metric
- Pareto front scatter plot
- Comparison bar chart
- Execution time comparison

### 7. ComparisonReport

Generates comprehensive reports.

**Outputs:**
- CSV files with raw data
- Summary table CSV
- Statistical tests CSV
- Text report

---

## Usage

### Quick Start

```python
from src.config import Configuration
from src.comparison import ExperimentRunner, StatisticalSummary, MannWhitneyTest

# Configure
config = Configuration()
config.algorithm.population_size = 100
config.algorithm.max_generations = 200

# Run experiments
runner = ExperimentRunner(config, num_runs=30)
ws_metrics, nsga2_metrics = runner.run_both()

# Compute statistics
stats = StatisticalSummary()
ws_stats = stats.compute_all({m: ws_metrics.get_values(m) for m in metrics})

# Statistical test
test = MannWhitneyTest(alpha=0.05)
results = test.compare_all_metrics(ws_values, nsga2_values)
```

### Full Experiment

```bash
python main_comparison.py
```

---

## Metrics Collected

### Common Metrics
| Metric | Description |
|--------|-------------|
| student_satisfaction | Best student satisfaction score |
| professor_satisfaction | Best professor satisfaction score |
| fairness | Fairness measure (lower is better) |
| capacity_penalty | Total capacity violations |
| field_penalty | Total field mismatches |
| execution_time | Time in seconds |

### Weighted Sum Specific
| Metric | Description |
|--------|-------------|
| best_fitness | Best scalar fitness value |

### NSGA-II Specific
| Metric | Description |
|--------|-------------|
| num_pareto_solutions | Number of non-dominated solutions |
| pareto_front | Full Pareto front data |

---

## Output Files

```
output/comparison/
├── weighted_sum_raw.csv           # Raw Weighted Sum data
├── nsga2_raw.csv                  # Raw NSGA-II data
├── summary_table.csv              # Statistics summary
├── statistical_tests.csv          # Mann-Whitney results
├── comparison_report.txt          # Full text report
├── boxplot_student_satisfaction.png
├── boxplot_professor_satisfaction.png
├── boxplot_fairness.png
├── boxplot_execution_time.png
├── pareto_front.png
├── comparison_bar_chart.png
└── execution_time.png
```

---

## Design Principles

1. **Independence**: Framework is completely independent of algorithms
2. **Simplicity**: No overengineering, practical for thesis
3. **Reproducibility**: Same seeds produce same results
4. **Extensibility**: Easy to add new metrics
5. **Statistical Rigor**: Follows recommended practices

---

## Statistical Methodology

Based on Thomas Weise's recommendations:

1. **Run 30 times** with different seeds
2. **Report median + quartiles** (not just mean)
3. **Use Mann-Whitney U Test** for significance
4. **Plot progress curves** and box plots
5. **Compare both quality AND speed**

---

## Extension Points

### Adding New Metric

1. Add attribute to `RunMetrics`
2. Add to `metrics_to_analyze` list in `main_comparison.py`
3. Include in visualization if needed

### Adding New Algorithm

1. Add `run_new_algorithm()` to `ExperimentRunner`
2. Collect metrics in `RunMetrics`
3. Include in comparison

### Adding New Test

1. Implement test method in new class
2. Add to `main_comparison.py`
3. Include in report generation
