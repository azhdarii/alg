"""
Main script for algorithm comparison.

Runs both Weighted Sum GA and NSGA-II multiple times,
collects metrics, performs statistical tests, and generates
a comprehensive comparison report.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Configuration
from src.comparison import (
    ExperimentRunner,
    StatisticalSummary,
    ComparisonVisualizer,
    MannWhitneyTest,
    ComparisonReport,
)


def main():
    """Run the algorithm comparison experiment."""

    print("=" * 70)
    print("ALGORITHM COMPARISON EXPERIMENT")
    print("Weighted Sum GA vs NSGA-II")
    print("=" * 70)

    # 1. Configuration
    print("\n[1/6] Setting up configuration...")
    config = Configuration()

    # Algorithm parameters (shared)
    config.algorithm.population_size = 100
    config.algorithm.max_generations = 200
    config.algorithm.crossover_probability = 0.8
    config.algorithm.mutation_probability = 0.1

    # Data files
    config.data.students_file = "Students.xlsx"
    config.data.professors_file = "Professors.xlsx"
    config.data.student_preferences_file = "StudentPreferences.xlsx"
    config.data.professor_preferences_file = "ProfessorPreferences.xlsx"
    config.data.universities_file = "Universities.xlsx"
    config.data.fields_file = "Fields.xlsx"

    # Experiment settings
    num_runs = 30
    base_seed = 1

    print(f"  Population size: {config.algorithm.population_size}")
    print(f"  Max generations: {config.algorithm.max_generations}")
    print(f"  Number of runs: {num_runs}")

    # 2. Run experiments
    print("\n[2/6] Running experiments...")
    runner = ExperimentRunner(
        config=config,
        num_runs=num_runs,
        base_seed=base_seed,
        verbose=True,
    )

    ws_metrics, nsga2_metrics = runner.run_both()

    print(f"\n  Weighted Sum: {ws_metrics.num_runs} runs completed")
    print(f"  NSGA-II: {nsga2_metrics.num_runs} runs completed")

    # 3. Compute statistics
    print("\n[3/6] Computing statistics...")
    stats_calc = StatisticalSummary()

    metrics_to_analyze = [
        "student_satisfaction",
        "professor_satisfaction",
        "fairness",
        "execution_time",
        "capacity_penalty",
        "field_penalty",
    ]

    ws_values = {m: ws_metrics.get_values(m) for m in metrics_to_analyze}
    nsga2_values = {m: nsga2_metrics.get_values(m) for m in metrics_to_analyze}

    ws_stats = stats_calc.compute_all(ws_values)
    nsga2_stats = stats_calc.compute_all(nsga2_values)

    print("\nWeighted Sum Statistics:")
    print(stats_calc.format_summary(ws_stats, include_mean=True))

    print("\nNSGA-II Statistics:")
    print(stats_calc.format_summary(nsga2_stats, include_mean=True))

    # 4. Statistical tests
    print("\n[4/6] Performing statistical tests...")
    test = MannWhitneyTest(alpha=0.05)

    # Test common metrics
    test_metrics = [
        "student_satisfaction",
        "professor_satisfaction",
        "fairness",
        "execution_time",
    ]

    test_results = test.compare_all_metrics(
        ws_values, nsga2_values,
        group1_name="Weighted Sum",
        group2_name="NSGA-II",
    )

    print("\nMann-Whitney U Test Results:")
    for result in test_results:
        sig_str = "SIGNIFICANT" if result.significant else "NOT significant"
        print(f"  {result.metric_name}: U={result.u_statistic:.2f}, p={result.p_value:.4f} [{sig_str}]")

    # 5. Generate visualizations
    print("\n[5/6] Generating visualizations...")
    visualizer = ComparisonVisualizer(output_dir="output/comparison")

    # Box plots
    box_files = visualizer.create_box_plots(ws_metrics, nsga2_metrics)
    print(f"  Box plots saved: {len(box_files)} files")

    # Pareto front
    pareto_file = visualizer.create_pareto_front_plot(nsga2_metrics, ws_metrics)
    if pareto_file:
        print(f"  Pareto front plot saved: {pareto_file}")

    # Bar chart
    bar_file = visualizer.create_comparison_bar_chart(
        ws_metrics, nsga2_metrics, ws_stats, nsga2_stats
    )
    if bar_file:
        print(f"  Bar chart saved: {bar_file}")

    # Execution time
    time_file = visualizer.create_execution_time_comparison(ws_metrics, nsga2_metrics)
    if time_file:
        print(f"  Execution time plot saved: {time_file}")

    # 6. Generate reports
    print("\n[6/6] Generating reports...")
    report = ComparisonReport(output_dir="output/comparison")

    saved_files = report.save_all(
        ws_metrics, nsga2_metrics,
        ws_stats, nsga2_stats,
        test_results,
    )

    print("\n  Saved files:")
    print(f"    Raw data: {saved_files['raw_data']}")
    print(f"    Summary: {saved_files['summary']}")
    print(f"    Statistical tests: {saved_files['tests']}")
    print(f"    Report: {saved_files['report']}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)

    # Print key findings
    print("\nKEY FINDINGS:")
    significant_results = [r for r in test_results if r.significant]
    if significant_results:
        print("Statistically significant differences found in:")
        for r in significant_results:
            if r.metric_name == "fairness":
                winner = r.group1_name if r.group1_median < r.group2_median else r.group2_name
            else:
                winner = r.group1_name if r.group1_median > r.group2_median else r.group2_name
            print(f"  - {r.metric_name}: {winner} (p={r.p_value:.4f})")
    else:
        print("No statistically significant differences found.")

    print(f"\nAll results saved to: output/comparison/")
    print("=" * 70)


if __name__ == "__main__":
    main()
