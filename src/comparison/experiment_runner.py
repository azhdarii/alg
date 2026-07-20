"""Experiment runner for algorithm comparison."""

import time
import random
from typing import List, Optional, Callable
from ..config.configuration import Configuration
from ..algorithms.weighted_sum import WeightedSumGA, WeightedSumConfig
from ..algorithms.nsga2 import NSGA2, NSGA2Config
from .metrics import RunMetrics, ComparisonMetrics


class ExperimentRunner:
    """
    Runs multiple experiments for algorithm comparison.

    Executes each algorithm multiple times with different random seeds
    and collects metrics for statistical comparison.

    Design:
        - Completely independent of algorithm implementation
        - Uses factory functions to create algorithm instances
        - Collects standardized metrics from both algorithms

    Follows Single Responsibility Principle: only handles experiment execution.
    """

    def __init__(
        self,
        config: Configuration,
        num_runs: int = 30,
        base_seed: int = 1,
        verbose: bool = False,
    ):
        """
        Initialize the experiment runner.

        Args:
            config: Shared algorithm configuration
            num_runs: Number of runs per algorithm
            base_seed: Starting random seed
            verbose: Whether to print progress
        """
        self.config = config
        self.num_runs = num_runs
        self.base_seed = base_seed
        self.verbose = verbose

    def run_weighted_sum(self) -> ComparisonMetrics:
        """
        Run Weighted Sum GA multiple times.

        Returns:
            ComparisonMetrics with all run results
        """
        results = ComparisonMetrics(algorithm="Weighted Sum")

        ws_config = WeightedSumConfig(
            weights=[0.4, 0.4, 0.2],
            constraint_weight=0.01,
            preserve_elitism=2,
            tournament_size=3,
        )

        for run_id in range(self.num_runs):
            seed = self.base_seed + run_id

            if self.verbose:
                print(f"\n[Weighted Sum] Run {run_id + 1}/{self.num_runs} (seed={seed})")

            metrics = self._run_single_weighted_sum(run_id, seed, ws_config)
            results.add_run(metrics)

        return results

    def run_nsga2(self) -> ComparisonMetrics:
        """
        Run NSGA-II multiple times.

        Returns:
            ComparisonMetrics with all run results
        """
        results = ComparisonMetrics(algorithm="NSGA-II")

        nsga2_config = NSGA2Config(
            tournament_size=2,
            use_constraint_dominance=True,
        )

        for run_id in range(self.num_runs):
            seed = self.base_seed + run_id

            if self.verbose:
                print(f"\n[NSGA-II] Run {run_id + 1}/{self.num_runs} (seed={seed})")

            metrics = self._run_single_nsga2(run_id, seed, nsga2_config)
            results.add_run(metrics)

        return results

    def run_both(self) -> tuple:
        """
        Run both algorithms.

        Returns:
            Tuple of (WeightedSumMetrics, NSGA2Metrics)
        """
        print("=" * 60)
        print("RUNNING ALGORITHM COMPARISON EXPERIMENT")
        print(f"Number of runs: {self.num_runs}")
        print("=" * 60)

        ws_results = self.run_weighted_sum()
        nsga2_results = self.run_nsga2()

        return ws_results, nsga2_results

    def _run_single_weighted_sum(
        self, run_id: int, seed: int, ws_config: WeightedSumConfig
    ) -> RunMetrics:
        """Run a single Weighted Sum experiment."""
        # Create fresh config for this run
        config = self._create_config(seed)

        # Create and run algorithm
        algorithm = WeightedSumGA(config=config, ws_config=ws_config)

        start_time = time.time()
        algorithm.run()
        execution_time = time.time() - start_time

        # Extract metrics
        best = algorithm.get_best_solution()
        if best is None:
            return RunMetrics(
                algorithm="Weighted Sum",
                run_id=run_id,
                seed=seed,
                execution_time=execution_time,
            )

        return RunMetrics(
            algorithm="Weighted Sum",
            run_id=run_id,
            seed=seed,
            execution_time=execution_time,
            student_satisfaction=best.objectives.student_satisfaction,
            professor_satisfaction=best.objectives.professor_satisfaction,
            fairness=best.objectives.fairness,
            capacity_penalty=best.constraints.capacity_violation,
            field_penalty=best.constraints.field_mismatch_count,
            best_fitness=best.fitness,
        )

    def _run_single_nsga2(
        self, run_id: int, seed: int, nsga2_config: NSGA2Config
    ) -> RunMetrics:
        """Run a single NSGA-II experiment."""
        # Create fresh config for this run
        config = self._create_config(seed)

        # Create and run algorithm
        algorithm = NSGA2(config=config, nsga2_config=nsga2_config)

        start_time = time.time()
        algorithm.run()
        execution_time = time.time() - start_time

        # Extract metrics
        pareto_front = algorithm.get_pareto_front()
        objectives = algorithm.get_pareto_front_objectives()

        if not pareto_front:
            return RunMetrics(
                algorithm="NSGA-II",
                run_id=run_id,
                seed=seed,
                execution_time=execution_time,
            )

        # For NSGA-II, we report the best values across Pareto front
        # and also the full Pareto front for analysis
        best_student = max(c.objectives.student_satisfaction for c in pareto_front)
        best_professor = max(c.objectives.professor_satisfaction for c in pareto_front)
        best_fairness = min(c.objectives.fairness for c in pareto_front)

        # Find solution with best student satisfaction for constraint info
        best_solution = max(pareto_front, key=lambda c: c.objectives.student_satisfaction)

        return RunMetrics(
            algorithm="NSGA-II",
            run_id=run_id,
            seed=seed,
            execution_time=execution_time,
            student_satisfaction=best_student,
            professor_satisfaction=best_professor,
            fairness=best_fairness,
            capacity_penalty=best_solution.constraints.capacity_violation,
            field_penalty=best_solution.constraints.field_mismatch_count,
            num_pareto_solutions=len(pareto_front),
            pareto_front=objectives,
        )

    def _create_config(self, seed: int) -> Configuration:
        """Create a fresh configuration with the given seed."""
        config = Configuration()
        config.algorithm.population_size = self.config.algorithm.population_size
        config.algorithm.max_generations = self.config.algorithm.max_generations
        config.algorithm.crossover_probability = self.config.algorithm.crossover_probability
        config.algorithm.mutation_probability = self.config.algorithm.mutation_probability
        config.algorithm.random_seed = seed

        config.penalty.capacity_penalty_per_student = self.config.penalty.capacity_penalty_per_student
        config.penalty.field_mismatch_penalty = self.config.penalty.field_mismatch_penalty

        # Use same data files
        config.data.students_file = self.config.data.students_file
        config.data.professors_file = self.config.data.professors_file
        config.data.student_preferences_file = self.config.data.student_preferences_file
        config.data.professor_preferences_file = self.config.data.professor_preferences_file
        config.data.universities_file = self.config.data.universities_file
        config.data.fields_file = self.config.data.fields_file

        # Disable logging during experiments
        config.logging.log_to_console = False
        config.logging.log_interval = self.config.algorithm.max_generations

        return config

    def __repr__(self) -> str:
        return (
            f"ExperimentRunner(\n"
            f"  num_runs={self.num_runs},\n"
            f"  base_seed={self.base_seed}\n"
            f")"
        )
