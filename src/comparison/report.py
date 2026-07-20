"""Comparison report generation."""

import csv
import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from .metrics import ComparisonMetrics
from .statistics import StatisticalSummary, MetricStatistics
from .statistical_test import MannWhitneyResult


class ComparisonReport:
    """
    Generates comparison reports and saves results.

    Creates:
    1. CSV files with raw data
    2. Summary tables
    3. Text report

    Follows Single Responsibility Principle: only handles reporting.
    """

    def __init__(self, output_dir: str = "output/comparison"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_raw_data(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
    ) -> List[str]:
        """
        Save raw experimental data to CSV files.

        Args:
            ws_metrics: Weighted Sum metrics
            nsga2_metrics: NSGA-II metrics

        Returns:
            List of saved file paths
        """
        saved_files = []

        # Save Weighted Sum data
        ws_file = self.output_dir / "weighted_sum_raw.csv"
        self._save_metrics_csv(ws_metrics, ws_file)
        saved_files.append(str(ws_file))

        # Save NSGA-II data
        nsga2_file = self.output_dir / "nsga2_raw.csv"
        self._save_metrics_csv(nsga2_metrics, nsga2_file)
        saved_files.append(str(nsga2_file))

        return saved_files

    def _save_metrics_csv(self, metrics: ComparisonMetrics, filepath: Path) -> None:
        """Save metrics to CSV file."""
        if not metrics.runs:
            return

        fieldnames = list(metrics.runs[0].to_dict().keys())

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for run in metrics.runs:
                writer.writerow(run.to_dict())

    def save_summary(
        self,
        ws_stats: Dict[str, MetricStatistics],
        nsga2_stats: Dict[str, MetricStatistics],
    ) -> str:
        """
        Save summary table to CSV.

        Args:
            ws_stats: Statistics for Weighted Sum
            nsga2_stats: Statistics for NSGA-II

        Returns:
            Path to saved file
        """
        filepath = self.output_dir / "summary_table.csv"

        metrics = list(ws_stats.keys())

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Metric',
                'WS Median', 'WS Q1', 'WS Q3', 'WS Mean', 'WS Std',
                'NSGA-II Median', 'NSGA-II Q1', 'NSGA-II Q3', 'NSGA-II Mean', 'NSGA-II Std',
            ])

            # Data rows
            for metric in metrics:
                ws = ws_stats[metric]
                nsga2 = nsga2_stats[metric]
                writer.writerow([
                    metric,
                    f"{ws.median:.4f}", f"{ws.q1:.4f}", f"{ws.q3:.4f}",
                    f"{ws.mean:.4f}" if ws.mean else "N/A",
                    f"{ws.std:.4f}" if ws.std else "N/A",
                    f"{nsga2.median:.4f}", f"{nsga2.q1:.4f}", f"{nsga2.q3:.4f}",
                    f"{nsga2.mean:.4f}" if nsga2.mean else "N/A",
                    f"{nsga2.std:.4f}" if nsga2.std else "N/A",
                ])

        return str(filepath)

    def save_statistical_tests(
        self,
        results: List[MannWhitneyResult],
    ) -> str:
        """
        Save statistical test results.

        Args:
            results: List of Mann-Whitney test results

        Returns:
            Path to saved file
        """
        filepath = self.output_dir / "statistical_tests.csv"

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Metric', 'U Statistic', 'p-value',
                'Significant', 'Alpha',
                'WS Median', 'NSGA-II Median', 'Winner'
            ])

            # Data rows
            for result in results:
                winner = result.group1_name if result.group1_median > result.group2_median else result.group2_name
                if result.metric_name == "fairness":
                    winner = result.group1_name if result.group1_median < result.group2_median else result.group2_name

                writer.writerow([
                    result.metric_name,
                    f"{result.u_statistic:.2f}",
                    f"{result.p_value:.4f}",
                    "Yes" if result.significant else "No",
                    result.alpha,
                    f"{result.group1_median:.4f}",
                    f"{result.group2_median:.4f}",
                    winner,
                ])

        return str(filepath)

    def generate_text_report(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
        ws_stats: Dict[str, MetricStatistics],
        nsga2_stats: Dict[str, MetricStatistics],
        test_results: List[MannWhitneyResult],
    ) -> str:
        """
        Generate a comprehensive text report.

        Args:
            ws_metrics: Weighted Sum metrics
            nsga2_metrics: NSGA-II metrics
            ws_stats: Statistics for Weighted Sum
            nsga2_stats: Statistics for NSGA-II
            test_results: Statistical test results

        Returns:
            Path to saved report
        """
        filepath = self.output_dir / "comparison_report.txt"

        lines = []
        lines.append("=" * 70)
        lines.append("ALGORITHM COMPARISON REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)

        # Experiment Setup
        lines.append("\n1. EXPERIMENT SETUP")
        lines.append("-" * 70)
        lines.append(f"Number of runs: {ws_metrics.num_runs}")
        lines.append(f"Algorithms compared: Weighted Sum GA vs NSGA-II")

        # Summary Statistics
        lines.append("\n2. SUMMARY STATISTICS")
        lines.append("-" * 70)
        lines.append("\nWeighted Sum GA:")
        for metric, stat in ws_stats.items():
            lines.append(f"  {metric}:")
            lines.append(f"    Median: {stat.median:.4f}")
            lines.append(f"    Q1: {stat.q1:.4f}, Q3: {stat.q3:.4f}")
            if stat.mean:
                lines.append(f"    Mean: {stat.mean:.4f}, Std: {stat.std:.4f}")

        lines.append("\nNSGA-II:")
        for metric, stat in nsga2_stats.items():
            lines.append(f"  {metric}:")
            lines.append(f"    Median: {stat.median:.4f}")
            lines.append(f"    Q1: {stat.q1:.4f}, Q3: {stat.q3:.4f}")
            if stat.mean:
                lines.append(f"    Mean: {stat.mean:.4f}, Std: {stat.std:.4f}")

        # Statistical Tests
        lines.append("\n3. STATISTICAL TESTS (Mann-Whitney U)")
        lines.append("-" * 70)
        lines.append(f"Significance level: alpha = {test_results[0].alpha if test_results else 0.05}")
        lines.append("")

        for result in test_results:
            sig_str = "SIGNIFICANT" if result.significant else "NOT significant"
            lines.append(f"{result.metric_name}:")
            lines.append(f"  U = {result.u_statistic:.2f}")
            lines.append(f"  p = {result.p_value:.4f}")
            lines.append(f"  {sig_str}")

            if result.significant:
                if result.metric_name == "fairness":
                    winner = result.group1_name if result.group1_median < result.group2_median else result.group2_name
                else:
                    winner = result.group1_name if result.group1_median > result.group2_median else result.group2_name
                lines.append(f"  Winner: {winner}")
            lines.append("")

        # NSGA-II Specific
        lines.append("\n4. NSGA-II PARETO FRONT ANALYSIS")
        lines.append("-" * 70)
        pareto_sizes = nsga2_metrics.get_values("num_pareto_solutions")
        if pareto_sizes:
            avg_pareto = sum(pareto_sizes) / len(pareto_sizes)
            lines.append(f"Average Pareto front size: {avg_pareto:.1f}")
            lines.append(f"Min Pareto front size: {min(pareto_sizes)}")
            lines.append(f"Max Pareto front size: {max(pareto_sizes)}")

        # Conclusions
        lines.append("\n5. CONCLUSIONS")
        lines.append("-" * 70)

        significant_results = [r for r in test_results if r.significant]
        if significant_results:
            lines.append("Statistically significant differences found in:")
            for r in significant_results:
                if r.metric_name == "fairness":
                    winner = r.group1_name if r.group1_median < r.group2_median else r.group2_name
                else:
                    winner = r.group1_name if r.group1_median > r.group2_median else r.group2_name
                lines.append(f"  - {r.metric_name}: {winner} performs better")
        else:
            lines.append("No statistically significant differences found.")

        lines.append("\n" + "=" * 70)

        report_text = "\n".join(lines)

        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def save_all(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
        ws_stats: Dict[str, MetricStatistics],
        nsga2_stats: Dict[str, MetricStatistics],
        test_results: List[MannWhitneyResult],
    ) -> Dict[str, str]:
        """
        Save all reports and data.

        Returns:
            Dictionary mapping report types to file paths
        """
        saved = {}

        # Raw data
        raw_files = self.save_raw_data(ws_metrics, nsga2_metrics)
        saved["raw_data"] = raw_files

        # Summary table
        saved["summary"] = self.save_summary(ws_stats, nsga2_stats)

        # Statistical tests
        saved["tests"] = self.save_statistical_tests(test_results)

        # Text report
        saved["report"] = self.generate_text_report(
            ws_metrics, nsga2_metrics, ws_stats, nsga2_stats, test_results
        )

        return saved
