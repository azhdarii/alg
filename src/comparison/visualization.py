"""Visualization for algorithm comparison."""

import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .metrics import ComparisonMetrics


class ComparisonVisualizer:
    """
    Generates visualization plots for algorithm comparison.

    Creates publication-quality figures suitable for a master's thesis.

    Generated plots:
    1. Box plots for each metric
    2. Pareto front scatter plot (NSGA-II)
    3. Convergence curves
    4. Comparison bar charts

    Follows Single Responsibility Principle: only handles visualization.
    """

    def __init__(self, output_dir: str = "output/comparison"):
        """
        Initialize the visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if MATPLOTLIB_AVAILABLE:
            # Set style for academic papers
            plt.style.use('seaborn-v0_8-whitegrid')
            plt.rcParams.update({
                'font.size': 12,
                'axes.labelsize': 14,
                'axes.titlesize': 14,
                'xtick.labelsize': 11,
                'ytick.labelsize': 11,
                'legend.fontsize': 11,
                'figure.figsize': (10, 6),
                'figure.dpi': 150,
            })

    def create_box_plots(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
        metrics: List[str] = None,
    ) -> List[str]:
        """
        Create box plots comparing metrics.

        Args:
            ws_metrics: Weighted Sum metrics
            nsga2_metrics: NSGA-II metrics
            metrics: List of metric names to plot

        Returns:
            List of saved file paths
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Skipping box plots.")
            return []

        if metrics is None:
            metrics = [
                "student_satisfaction",
                "professor_satisfaction",
                "fairness",
                "execution_time",
            ]

        saved_files = []

        for metric in metrics:
            ws_values = ws_metrics.get_values(metric)
            nsga2_values = nsga2_metrics.get_values(metric)

            fig, ax = plt.subplots(figsize=(8, 6))

            # Create box plot
            bp = ax.boxplot(
                [ws_values, nsga2_values],
                labels=["Weighted Sum", "NSGA-II"],
                patch_artist=True,
                widths=0.6,
            )

            # Color the boxes
            colors = ['#3498db', '#e74c3c']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # Add individual points
            for i, (values, color) in enumerate(zip([ws_values, nsga2_values], colors)):
                x = [i + 1] * len(values)
                ax.scatter(x, values, alpha=0.5, color=color, s=30, zorder=5)

            # Labels
            ax.set_ylabel(self._format_metric_name(metric))
            ax.set_title(f"Comparison: {self._format_metric_name(metric)}")

            # Grid
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save
            filename = f"boxplot_{metric}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

            saved_files.append(str(filepath))

        return saved_files

    def create_pareto_front_plot(
        self,
        nsga2_metrics: ComparisonMetrics,
        ws_metrics: Optional[ComparisonMetrics] = None,
    ) -> Optional[str]:
        """
        Create scatter plot of Pareto front.

        Args:
            nsga2_metrics: NSGA-II metrics with Pareto fronts
            ws_metrics: Optional Weighted Sum metrics to overlay

        Returns:
            Path to saved file, or None if no data
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Skipping Pareto plot.")
            return None

        # Collect all Pareto front points from all runs
        all_student = []
        all_professor = []
        all_fairness = []

        for run in nsga2_metrics.runs:
            for point in run.pareto_front:
                all_student.append(point["student_satisfaction"])
                all_professor.append(point["professor_satisfaction"])
                all_fairness.append(point["fairness"])

        if not all_student:
            return None

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Student vs Professor Satisfaction
        ax1 = axes[0]
        scatter1 = ax1.scatter(
            all_student, all_professor,
            c=all_fairness, cmap='viridis',
            alpha=0.6, s=50, edgecolors='black', linewidth=0.5,
        )
        plt.colorbar(scatter1, ax=ax1, label='Fairness (lower=better)')
        ax1.set_xlabel('Student Satisfaction')
        ax1.set_ylabel('Professor Satisfaction')
        ax1.set_title('NSGA-II Pareto Front')
        ax1.grid(True, alpha=0.3)

        # Overlay Weighted Sum solution if provided
        if ws_metrics and ws_metrics.runs:
            ws_student = [run.student_satisfaction for run in ws_metrics.runs]
            ws_professor = [run.professor_satisfaction for run in ws_metrics.runs]
            ax1.scatter(ws_student, ws_professor, c='red', marker='*', s=200,
                       label='Weighted Sum', zorder=10)
            ax1.legend()

        # Plot 2: Student vs Fairness
        ax2 = axes[1]
        scatter2 = ax2.scatter(
            all_student, all_fairness,
            c=all_professor, cmap='plasma',
            alpha=0.6, s=50, edgecolors='black', linewidth=0.5,
        )
        plt.colorbar(scatter2, ax=ax2, label='Professor Satisfaction')
        ax2.set_xlabel('Student Satisfaction')
        ax2.set_ylabel('Fairness (lower=better)')
        ax2.set_title('NSGA-II: Student Satisfaction vs Fairness')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        filepath = self.output_dir / "pareto_front.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return str(filepath)

    def create_comparison_bar_chart(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
        stats_ws: Dict,
        stats_nsga2: Dict,
    ) -> str:
        """
        Create bar chart comparing medians.

        Args:
            ws_metrics: Weighted Sum metrics
            nsga2_metrics: NSGA-II metrics
            stats_ws: Statistics for Weighted Sum
            stats_nsga2: Statistics for NSGA-II

        Returns:
            Path to saved file
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Skipping bar chart.")
            return ""

        metrics = ["student_satisfaction", "professor_satisfaction", "fairness"]
        labels = ["Student Sat.", "Professor Sat.", "Fairness"]

        ws_medians = [stats_ws[m].median for m in metrics]
        nsga2_medians = [stats_nsga2[m].median for m in metrics]

        # For fairness, lower is better, so we invert for visualization
        # Actually, let's keep it as-is for accuracy

        x = range(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        bars1 = ax.bar([i - width/2 for i in x], ws_medians, width,
                       label='Weighted Sum', color='#3498db', alpha=0.8)
        bars2 = ax.bar([i + width/2 for i in x], nsga2_medians, width,
                       label='NSGA-II', color='#e74c3c', alpha=0.8)

        # Add error bars (IQR)
        ws_q1 = [stats_ws[m].q1 for m in metrics]
        ws_q3 = [stats_ws[m].q3 for m in metrics]
        nsga2_q1 = [stats_nsga2[m].q1 for m in metrics]
        nsga2_q3 = [stats_nsga2[m].q3 for m in metrics]

        ws_errors = [[m - q1 for m, q1 in zip(ws_medians, ws_q1)],
                     [q3 - m for m, q3 in zip(ws_medians, ws_q3)]]
        nsga2_errors = [[m - q1 for m, q1 in zip(nsga2_medians, nsga2_q1)],
                        [q3 - m for m, q3 in zip(nsga2_medians, nsga2_q3)]]

        ax.errorbar([i - width/2 for i in x], ws_medians, ws_errors,
                    fmt='none', color='black', capsize=5)
        ax.errorbar([i + width/2 for i in x], nsga2_medians, nsga2_errors,
                    fmt='none', color='black', capsize=5)

        ax.set_xlabel('Metric')
        ax.set_ylabel('Value')
        ax.set_title('Algorithm Comparison (Median with IQR)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        # Save
        filepath = self.output_dir / "comparison_bar_chart.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return str(filepath)

    def create_execution_time_comparison(
        self,
        ws_metrics: ComparisonMetrics,
        nsga2_metrics: ComparisonMetrics,
    ) -> str:
        """
        Create execution time comparison plot.

        Args:
            ws_metrics: Weighted Sum metrics
            nsga2_metrics: NSGA-II metrics

        Returns:
            Path to saved file
        """
        if not MATPLOTLIB_AVAILABLE:
            return ""

        ws_times = ws_metrics.get_values("execution_time")
        nsga2_times = nsga2_metrics.get_values("execution_time")

        fig, ax = plt.subplots(figsize=(8, 6))

        bp = ax.boxplot(
            [ws_times, nsga2_times],
            labels=["Weighted Sum", "NSGA-II"],
            patch_artist=True,
            widths=0.6,
        )

        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Execution Time (seconds)')
        ax.set_title('Execution Time Comparison')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        filepath = self.output_dir / "execution_time.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return str(filepath)

    def _format_metric_name(self, metric: str) -> str:
        """Format metric name for display."""
        return metric.replace("_", " ").title()
