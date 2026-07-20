"""Metrics collection for algorithm comparison."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json


@dataclass
class RunMetrics:
    """
    Metrics collected from a single algorithm run.

    Stores all relevant data for one execution of an algorithm.

    Attributes:
        algorithm: Algorithm name ('Weighted Sum' or 'NSGA-II')
        run_id: Run number (0-based)
        seed: Random seed used
        execution_time: Time in seconds

        # Objective values (best solution)
        student_satisfaction: Student satisfaction score
        professor_satisfaction: Professor satisfaction score
        fairness: Fairness measure (lower is better)

        # Constraint violations
        capacity_penalty: Total capacity penalty
        field_penalty: Total field mismatch penalty

        # Algorithm-specific
        best_fitness: Best fitness value (Weighted Sum only)
        num_pareto_solutions: Number of non-dominated solutions (NSGA-II only)
        pareto_front: List of Pareto front solutions (NSGA-II only)

        # Convergence history
        fitness_history: Best fitness per generation
        student_sat_history: Best student satisfaction per generation
    """

    algorithm: str
    run_id: int
    seed: int
    execution_time: float

    # Objective values
    student_satisfaction: float = 0.0
    professor_satisfaction: float = 0.0
    fairness: float = 0.0

    # Constraint violations
    capacity_penalty: float = 0.0
    field_penalty: float = 0.0

    # Algorithm-specific
    best_fitness: Optional[float] = None
    num_pareto_solutions: int = 0
    pareto_front: List[Dict[str, float]] = field(default_factory=list)

    # Convergence history
    fitness_history: List[float] = field(default_factory=list)
    student_sat_history: List[float] = field(default_factory=list)
    professor_sat_history: List[float] = field(default_factory=list)
    fairness_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "algorithm": self.algorithm,
            "run_id": self.run_id,
            "seed": self.seed,
            "execution_time": self.execution_time,
            "student_satisfaction": self.student_satisfaction,
            "professor_satisfaction": self.professor_satisfaction,
            "fairness": self.fairness,
            "capacity_penalty": self.capacity_penalty,
            "field_penalty": self.field_penalty,
            "best_fitness": self.best_fitness,
            "num_pareto_solutions": self.num_pareto_solutions,
        }

    def __repr__(self) -> str:
        return (
            f"RunMetrics(algo={self.algorithm}, run={self.run_id}, "
            f"student={self.student_satisfaction:.4f}, "
            f"professor={self.professor_satisfaction:.4f}, "
            f"fairness={self.fairness:.4f})"
        )


@dataclass
class ComparisonMetrics:
    """
    Aggregated metrics from multiple runs of an algorithm.

    Collects all run results and provides access to the data
    for statistical analysis.

    Attributes:
        algorithm: Algorithm name
        runs: List of RunMetrics from each run
    """

    algorithm: str
    runs: List[RunMetrics] = field(default_factory=list)

    def add_run(self, metrics: RunMetrics) -> None:
        """Add a run's metrics."""
        self.runs.append(metrics)

    @property
    def num_runs(self) -> int:
        """Number of runs collected."""
        return len(self.runs)

    def get_values(self, metric_name: str) -> List[float]:
        """
        Get values for a specific metric across all runs.

        Args:
            metric_name: Name of the metric attribute

        Returns:
            List of values
        """
        return [getattr(run, metric_name) for run in self.runs]

    def get_summary_dict(self) -> Dict[str, Any]:
        """Get summary as dictionary."""
        return {
            "algorithm": self.algorithm,
            "num_runs": self.num_runs,
            "metrics": {
                "student_satisfaction": self.get_values("student_satisfaction"),
                "professor_satisfaction": self.get_values("professor_satisfaction"),
                "fairness": self.get_values("fairness"),
                "execution_time": self.get_values("execution_time"),
                "capacity_penalty": self.get_values("capacity_penalty"),
                "field_penalty": self.get_values("field_penalty"),
            },
        }

    def __repr__(self) -> str:
        return (
            f"ComparisonMetrics(algo={self.algorithm}, "
            f"runs={self.num_runs})"
        )
