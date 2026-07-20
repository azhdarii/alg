"""
Main entry point for the Weighted Sum Genetic Algorithm.

This script runs the Weighted Sum GA on the student-supervisor
assignment problem using the shared infrastructure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Configuration
from src.algorithms import WeightedSumGA, WeightedSumConfig


def main():
    """Run the Weighted Sum Genetic Algorithm."""

    print("=" * 60)
    print("Student-Supervisor Assignment Optimization")
    print("Weighted Sum Genetic Algorithm")
    print("=" * 60)

    # 1. Load configuration
    print("\n[Config] Loading configuration...")
    config = Configuration()

    # Customize configuration for this run
    config.algorithm.population_size = 100
    config.algorithm.max_generations = 200
    config.algorithm.crossover_probability = 0.8
    config.algorithm.mutation_probability = 0.1
    config.algorithm.random_seed = 42

    config.penalty.capacity_penalty_per_student = 10.0
    config.penalty.field_mismatch_penalty = 5.0

    # Data files are in the project root directory
    config.data.students_file = "Students.xlsx"
    config.data.professors_file = "Professors.xlsx"
    config.data.student_preferences_file = "StudentPreferences.xlsx"
    config.data.professor_preferences_file = "ProfessorPreferences.xlsx"
    config.data.universities_file = "Universities.xlsx"
    config.data.fields_file = "Fields.xlsx"

    config.logging.log_file = "output/weighted_sum_log.csv"
    config.logging.log_interval = 10

    print(f"  Population: {config.algorithm.population_size}")
    print(f"  Generations: {config.algorithm.max_generations}")
    print(f"  Crossover: {config.algorithm.crossover_probability}")
    print(f"  Mutation: {config.algorithm.mutation_probability}")

    # 2. Create Weighted Sum configuration
    ws_config = WeightedSumConfig(
        weights=[0.4, 0.4, 0.2],  # [student, professor, fairness]
        constraint_weight=0.01,
        preserve_elitism=2,
        tournament_size=3,
    )

    print(f"\n[WS Config]")
    print(f"  Weights: {ws_config.weights}")
    print(f"  Constraint weight: {ws_config.constraint_weight}")
    print(f"  Elitism: {ws_config.preserve_elitism}")

    # 3. Create and run algorithm
    print("\n[Running] Starting Weighted Sum GA...")
    ga = WeightedSumGA(config=config, ws_config=ws_config)
    final_population = ga.run()

    # 4. Get results
    best = ga.get_best_solution()
    if best:
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Best Fitness: {best.fitness:.6f}")
        print(f"Student Satisfaction: {best.objectives.student_satisfaction:.4f}")
        print(f"Professor Satisfaction: {best.objectives.professor_satisfaction:.4f}")
        print(f"Fairness: {best.objectives.fairness:.4f}")
        print(f"Capacity Violations: {best.constraints.capacity_violation:.2f}")
        print(f"Field Mismatches: {best.constraints.field_mismatch_count}")
        print("=" * 60)

    # 5. Save configuration
    config.to_json("output/weighted_sum_config.json")
    print("\n[Config] Saved to output/weighted_sum_config.json")
    print("[Log] Saved to output/weighted_sum_log.csv")


if __name__ == "__main__":
    main()
