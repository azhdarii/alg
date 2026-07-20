"""
Main entry point for NSGA-II algorithm.

This script runs NSGA-II on the student-supervisor assignment problem
using the shared infrastructure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Configuration
from src.algorithms import NSGA2, NSGA2Config


def main():
    """Run NSGA-II on the assignment problem."""

    print("=" * 60)
    print("Student-Supervisor Assignment Optimization")
    print("NSGA-II (Non-dominated Sorting Genetic Algorithm II)")
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

    config.logging.log_file = "output/nsga2_log.csv"
    config.logging.log_interval = 10

    print(f"  Population: {config.algorithm.population_size}")
    print(f"  Generations: {config.algorithm.max_generations}")
    print(f"  Crossover: {config.algorithm.crossover_probability}")
    print(f"  Mutation: {config.algorithm.mutation_probability}")

    # 2. Create NSGA-II configuration
    nsga2_config = NSGA2Config(
        tournament_size=2,
        use_constraint_dominance=True,
    )

    print(f"\n[NSGA-II Config]")
    print(f"  Tournament size: {nsga2_config.tournament_size}")
    print(f"  Constraint dominance: {nsga2_config.use_constraint_dominance}")

    # 3. Create and run algorithm
    print("\n[Running] Starting NSGA-II...")
    algorithm = NSGA2(config=config, nsga2_config=nsga2_config)
    final_population = algorithm.run()

    # 4. Get results
    pareto_front = algorithm.get_pareto_front()
    objectives = algorithm.get_pareto_front_objectives()
    stats = algorithm.get_statistics()

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"\nPareto Front Size: {stats['pareto_front_size']}")
    print(f"Objectives: {stats['objectives']}")

    print("\nPareto Front Solutions:")
    for i, obj in enumerate(objectives[:10]):  # Show first 10
        print(
            f"  {i+1:2d}. Student: {obj['student_satisfaction']:.4f} | "
            f"Professor: {obj['professor_satisfaction']:.4f} | "
            f"Fairness: {obj['fairness']:.4f} | "
            f"Rank: {obj['rank']}"
        )

    if len(objectives) > 10:
        print(f"  ... and {len(objectives) - 10} more solutions")

    print("=" * 60)

    # 5. Save configuration
    config.to_json("output/nsga2_config.json")
    print("\n[Config] Saved to output/nsga2_config.json")
    print("[Log] Saved to output/nsga2_log.csv")


if __name__ == "__main__":
    main()
