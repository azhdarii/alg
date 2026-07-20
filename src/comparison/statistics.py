"""Statistical summary for algorithm comparison."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import math


@dataclass
class MetricStatistics:
    """
    Statistics for a single metric.

    Attributes:
        metric_name: Name of the metric
        median: Median value
        q1: First quartile (25th percentile)
        q3: Third quartile (75th percentile)
        mean: Arithmetic mean (optional)
        std: Standard deviation (optional)
        min_value: Minimum value
        max_value: Maximum value
    """

    metric_name: str
    median: float
    q1: float
    q3: float
    mean: Optional[float] = None
    std: Optional[float] = None
    min_value: float = 0.0
    max_value: float = 0.0

    def __repr__(self) -> str:
        return (
            f"{self.metric_name}: "
            f"median={self.median:.4f}, "
            f"Q1={self.q1:.4f}, "
            f"Q3={self.q3:.4f}"
        )


@dataclass
class StatisticalSummary:
    """
    Statistical summary for an algorithm's metrics.

    Computes median, quartiles, and optionally mean/std
    for all collected metrics.

    Follows the recommendation from Thomas Weise's lecture:
    "Don't trust arithmetic mean or standard deviation"
    - Median and quartiles are primary
    - Mean and std are optional
    """

    def __init__(self):
        """Initialize the statistics calculator."""
        pass

    def compute(self, values: List[float], metric_name: str) -> MetricStatistics:
        """
        Compute statistics for a list of values.

        Args:
            values: List of metric values from multiple runs
            metric_name: Name of the metric

        Returns:
            MetricStatistics object
        """
        if not values:
            return MetricStatistics(
                metric_name=metric_name,
                median=0.0,
                q1=0.0,
                q3=0.0,
            )

        sorted_values = sorted(values)
        n = len(sorted_values)

        # Compute quartiles
        median = self._median(sorted_values)
        q1 = self._percentile(sorted_values, 25)
        q3 = self._percentile(sorted_values, 75)

        # Compute mean and std (optional)
        mean = sum(sorted_values) / n
        std = self._std(sorted_values, mean)

        return MetricStatistics(
            metric_name=metric_name,
            median=median,
            q1=q1,
            q3=q3,
            mean=mean,
            std=std,
            min_value=min(sorted_values),
            max_value=max(sorted_values),
        )

    def compute_all(
        self,
        values_dict: Dict[str, List[float]],
    ) -> Dict[str, MetricStatistics]:
        """
        Compute statistics for multiple metrics.

        Args:
            values_dict: Dictionary mapping metric names to value lists

        Returns:
            Dictionary mapping metric names to MetricStatistics
        """
        results = {}
        for metric_name, values in values_dict.items():
            results[metric_name] = self.compute(values, metric_name)
        return results

    def _median(self, sorted_values: List[float]) -> float:
        """Compute median of sorted list."""
        n = len(sorted_values)
        if n % 2 == 1:
            return sorted_values[n // 2]
        else:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """
        Compute percentile using linear interpolation.

        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to compute (0-100)
        """
        n = len(sorted_values)
        if n == 1:
            return sorted_values[0]

        # Compute index
        k = (percentile / 100.0) * (n - 1)
        f = math.floor(k)
        c = math.ceil(k)

        if f == c:
            return sorted_values[int(k)]

        # Linear interpolation
        d0 = sorted_values[int(f)] * (c - k)
        d1 = sorted_values[int(c)] * (k - f)
        return d0 + d1

    def _std(self, values: List[float], mean: float) -> float:
        """Compute standard deviation."""
        if len(values) < 2:
            return 0.0
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def format_summary(
        self,
        stats: Dict[str, MetricStatistics],
        include_mean: bool = False,
    ) -> str:
        """
        Format statistics as a readable string.

        Args:
            stats: Dictionary of statistics
            include_mean: Whether to include mean and std

        Returns:
            Formatted string
        """
        lines = []
        for name, stat in stats.items():
            line = f"{name}: median={stat.median:.4f}, Q1={stat.q1:.4f}, Q3={stat.q3:.4f}"
            if include_mean:
                line += f", mean={stat.mean:.4f}, std={stat.std:.4f}"
            lines.append(line)
        return "\n".join(lines)
