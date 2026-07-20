"""Mann-Whitney U Test for algorithm comparison."""

from dataclasses import dataclass
from typing import List
import math


@dataclass
class MannWhitneyResult:
    """
    Result of Mann-Whitney U Test.

    Attributes:
        metric_name: Name of the metric compared
        u_statistic: Computed U statistic
        p_value: Approximate p-value
        significant: Whether difference is significant at alpha
        alpha: Significance level used
        group1_median: Median of first group
        group2_median: Median of second group
        group1_name: Name of first algorithm
        group2_name: Name of second algorithm
    """

    metric_name: str
    u_statistic: float
    p_value: float
    significant: bool
    alpha: float
    group1_median: float
    group2_median: float
    group1_name: str
    group2_name: str

    def __repr__(self) -> str:
        sig_str = "YES" if self.significant else "NO"
        return (
            f"{self.metric_name}: U={self.u_statistic:.2f}, "
            f"p={self.p_value:.4f}, significant={sig_str} "
            f"(alpha={self.alpha})"
        )


class MannWhitneyTest:
    """
    Mann-Whitney U Test implementation.

    A non-parametric statistical test for comparing two independent
    samples. Does not assume normal distribution.

    This is the standard test recommended for comparing metaheuristic
    algorithms (as per Thomas Weise's lecture).

    Reference:
        Mann, H. B., & Whitney, D. R. (1947).
        "On a test of whether one of two random variables is
        stochastically larger than the other."
        The Annals of Mathematical Statistics, 18(1), 50-60.

    Follows Single Responsibility Principle: only handles statistical testing.
    """

    def __init__(self, alpha: float = 0.05):
        """
        Initialize the Mann-Whitney U Test.

        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
        # Critical z-values for common alpha levels
        self._z_table = {
            0.01: 2.575,
            0.05: 1.96,
            0.10: 1.645,
        }

    def test(
        self,
        group1: List[float],
        group2: List[float],
        metric_name: str,
        group1_name: str = "Algorithm A",
        group2_name: str = "Algorithm B",
    ) -> MannWhitneyResult:
        """
        Perform Mann-Whitney U Test.

        Args:
            group1: Values from first algorithm
            group2: Values from second algorithm
            metric_name: Name of the metric
            group1_name: Name of first algorithm
            group2_name: Name of second algorithm

        Returns:
            MannWhitneyResult with test results
        """
        n1 = len(group1)
        n2 = len(group2)

        # Combine and rank
        combined = [(v, 1) for v in group1] + [(v, 2) for v in group2]
        combined.sort(key=lambda x: x[0])

        # Assign ranks
        ranks = self._assign_ranks(combined)

        # Compute rank sums
        r1 = sum(ranks[i] for i in range(n1))
        r2 = sum(ranks[i] for i in range(n1, n1 + n2))

        # Compute U statistics
        u1 = r1 - n1 * (n1 + 1) / 2
        u2 = r2 - n2 * (n2 + 1) / 2

        # U is the smaller of the two
        u = min(u1, u2)

        # Compute approximate p-value using normal approximation
        mu = n1 * n2 / 2
        sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

        if sigma == 0:
            p_value = 1.0
        else:
            z = (u - mu) / sigma
            p_value = 2 * self._normal_cdf(z)  # Two-tailed test

        # Determine significance
        significant = p_value < self.alpha

        # Compute medians
        group1_median = sorted(group1)[len(group1) // 2]
        group2_median = sorted(group2)[len(group2) // 2]

        return MannWhitneyResult(
            metric_name=metric_name,
            u_statistic=u,
            p_value=p_value,
            significant=significant,
            alpha=self.alpha,
            group1_median=group1_median,
            group2_median=group2_median,
            group1_name=group1_name,
            group2_name=group2_name,
        )

    def _assign_ranks(self, combined: List[tuple]) -> List[float]:
        """
        Assign ranks to combined values, handling ties.

        Args:
            combined: List of (value, group_id) tuples

        Returns:
            List of ranks
        """
        n = len(combined)
        ranks = [0.0] * n
        i = 0

        while i < n:
            j = i
            # Find all ties
            while j < n and combined[j][0] == combined[i][0]:
                j += 1

            # Average rank for ties
            avg_rank = (i + j + 1) / 2.0  # Ranks are 1-based
            for k in range(i, j):
                ranks[k] = avg_rank

            i = j

        return ranks

    def _normal_cdf(self, x: float) -> float:
        """
        Approximate the cumulative distribution function
        of the standard normal distribution.

        Uses the error function approximation.
        """
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def compare_all_metrics(
        self,
        group1_values: dict,
        group2_values: dict,
        group1_name: str = "Algorithm A",
        group2_name: str = "Algorithm B",
    ) -> List[MannWhitneyResult]:
        """
        Compare multiple metrics between two algorithms.

        Args:
            group1_values: Dict mapping metric names to value lists (algorithm 1)
            group2_values: Dict mapping metric names to value lists (algorithm 2)
            group1_name: Name of first algorithm
            group2_name: Name of second algorithm

        Returns:
            List of MannWhitneyResult for each metric
        """
        results = []
        for metric_name in group1_values:
            if metric_name in group2_values:
                result = self.test(
                    group1_values[metric_name],
                    group2_values[metric_name],
                    metric_name,
                    group1_name,
                    group2_name,
                )
                results.append(result)
        return results
