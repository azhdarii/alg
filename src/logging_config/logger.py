"""Logging module for optimization process."""

import csv
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from ..models.population import Population, PopulationStatistics
from ..config.configuration import LoggingConfig


class OptimizationLogger:
    """
    Logger for recording optimization progress.

    This class handles:
    - Generation-by-generation statistics logging
    - CSV output for analysis
    - Console output (optional)
    - Execution time tracking

    Follows Single Responsibility Principle: only handles logging.
    """

    def __init__(self, config: LoggingConfig):
        """
        Initialize the logger.

        Args:
            config: Logging configuration
        """
        self.config = config
        self._start_time: Optional[float] = None
        self._generation_times: List[float] = []
        self._log_data: List[Dict[str, Any]] = []

        # Ensure output directory exists
        Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        """Start the optimization timer."""
        self._start_time = time.time()
        self._generation_times = []
        self._log_data = []

    def log_generation(
        self,
        population: Population,
        generation: int,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log statistics for a generation.

        Args:
            population: Current population
            generation: Generation number
            additional_data: Optional extra data to log
        """
        stats = population.compute_statistics()
        current_time = time.time()
        elapsed = current_time - self._start_time if self._start_time else 0

        log_entry = {
            "generation": generation,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "population_size": stats.size,
            "best_fitness": round(stats.best_fitness, 6),
            "worst_fitness": round(stats.worst_fitness, 6),
            "avg_fitness": round(stats.avg_fitness, 6),
            "best_student_satisfaction": round(stats.best_student_satisfaction, 6),
            "best_professor_satisfaction": round(stats.best_professor_satisfaction, 6),
            "best_fairness": round(stats.best_fairness, 6),
            "avg_student_satisfaction": round(stats.avg_student_satisfaction, 6),
            "avg_professor_satisfaction": round(stats.avg_professor_satisfaction, 6),
            "avg_fairness": round(stats.avg_fairness, 6),
            "total_capacity_violations": round(stats.total_capacity_violations, 2),
            "total_field_mismatches": stats.total_field_mismatches,
        }

        if additional_data:
            log_entry.update(additional_data)

        self._log_data.append(log_entry)

        # Console output
        if self.config.log_to_console and generation % self.config.log_interval == 0:
            self._print_generation(generation, stats, elapsed)

        # Write to CSV periodically
        if generation % self.config.log_interval == 0:
            self._write_csv()

    def _print_generation(
        self,
        generation: int,
        stats: PopulationStatistics,
        elapsed: float,
    ) -> None:
        """Print generation stats to console."""
        print(
            f"Gen {generation:4d} | "
            f"Best: {stats.best_fitness:.4f} | "
            f"Avg: {stats.avg_fitness:.4f} | "
            f"Student: {stats.best_student_satisfaction:.4f} | "
            f"Professor: {stats.best_professor_satisfaction:.4f} | "
            f"Fairness: {stats.best_fairness:.4f} | "
            f"Time: {elapsed:.1f}s"
        )

    def _write_csv(self) -> None:
        """Write log data to CSV file."""
        if not self._log_data:
            return

        fieldnames = list(self._log_data[0].keys())

        with open(self.config.log_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._log_data)

    def log_event(self, event_type: str, message: str, **kwargs) -> None:
        """
        Log a specific event.

        Args:
            event_type: Type of event (e.g., 'crossover', 'mutation')
            message: Description of the event
            **kwargs: Additional data
        """
        elapsed = time.time() - self._start_time if self._start_time else 0
        event = {
            "event_type": event_type,
            "message": message,
            "elapsed_seconds": round(elapsed, 2),
            **kwargs,
        }

        if self.config.log_level == "DEBUG":
            print(f"[{event_type}] {message}")

    def finish(self, final_population: Population) -> None:
        """
        Finish logging and write final results.

        Args:
            final_population: Final population after optimization
        """
        total_time = time.time() - self._start_time if self._start_time else 0

        # Write final CSV
        self._write_csv()

        # Print summary
        if self.config.log_to_console:
            stats = final_population.compute_statistics()
            print("\n" + "=" * 60)
            print("OPTIMIZATION COMPLETE")
            print("=" * 60)
            print(f"Total generations: {final_population.generation}")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Best fitness: {stats.best_fitness:.6f}")
            print(f"Best student satisfaction: {stats.best_student_satisfaction:.6f}")
            print(f"Best professor satisfaction: {stats.best_professor_satisfaction:.6f}")
            print(f"Best fairness: {stats.best_fairness:.6f}")
            print(f"Final log saved to: {self.config.log_file}")
            print("=" * 60)

    def get_best_solution(self, population: Population) -> Optional[Dict[str, Any]]:
        """
        Get the best solution from the population.

        Args:
            population: Population to analyze

        Returns:
            Dictionary with best solution details, or None
        """
        best = population.get_best()
        if best is None:
            return None

        return {
            "fitness": best.fitness,
            "objectives": best.objectives.to_list() if best.objectives else None,
            "constraints": best.constraints.to_list() if best.constraints else None,
            "assignments": best.to_assignment_dict(),
        }

    def __repr__(self) -> str:
        return f"OptimizationLogger(log_file='{self.config.log_file}')"
