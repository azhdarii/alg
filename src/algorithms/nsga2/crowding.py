"""Crowding Distance computation for NSGA-II."""

from typing import List
from ...models.chromosome import Chromosome


class CrowdingDistance:
    """
    Crowding Distance computation for NSGA-II.

    Computes the crowding distance for chromosomes within each Pareto front.
    Crowding distance measures how isolated a solution is in objective space.
    Solutions at the boundaries (extreme points) get infinite distance.

    Purpose in NSGA-II:
    - Maintains diversity in the population
    - Prevents premature convergence to a small region
    - Used as tie-breaker when comparing solutions with same Pareto rank

    Algorithm:
    1. For each front:
       a. Initialize all distances to 0
       b. For each objective:
          - Sort solutions by that objective
          - Set boundary solutions to infinity
          - For interior solutions, distance = (next - prev) / (max - min)

    Complexity: O(M * N log N) where M = objectives, N = front size

    Design Note:
        This class is independent of Weighted Sum and can be reused
        by any multi-objective algorithm that needs diversity preservation.

    Follows Single Responsibility Principle: only handles crowding distance.
    """

    def __init__(self):
        """Initialize the crowding distance calculator."""
        pass

    def compute(self, fronts: List[List[Chromosome]]) -> None:
        """
        Compute crowding distance for all chromosomes in each front.

        This method modifies chromosomes in-place, storing the distance
        in chromosome.metadata["crowding_distance"].

        Args:
            fronts: List of fronts from non-dominated sorting
        """
        for front in fronts:
            if len(front) <= 2:
                # Boundary solutions get infinite distance
                for chrom in front:
                    chrom.metadata["crowding_distance"] = float("inf")
                continue

            self._compute_front_distance(front)

    def _compute_front_distance(self, front: List[Chromosome]) -> None:
        """
        Compute crowding distance for a single front.

        Args:
            front: List of chromosomes in the same Pareto front
        """
        n = len(front)

        # Initialize distances to 0
        for chrom in front:
            chrom.metadata["crowding_distance"] = 0.0

        # For each objective
        num_objectives = 3  # student, professor, fairness

        for obj_idx in range(num_objectives):
            # Extract objective values
            obj_values = []
            for chrom in front:
                if chrom.objectives is not None:
                    obj_values.append(chrom.objectives.to_list()[obj_idx])
                else:
                    obj_values.append(0.0)

            # Sort by objective value
            sorted_indices = sorted(range(n), key=lambda i: obj_values[i])
            sorted_values = [obj_values[i] for i in sorted_indices]

            # Boundary solutions get infinite distance
            front[sorted_indices[0]].metadata["crowding_distance"] = float("inf")
            front[sorted_indices[-1]].metadata["crowding_distance"] = float("inf")

            # Compute range
            obj_range = sorted_values[-1] - sorted_values[0]
            if obj_range == 0:
                continue  # All values are the same, skip

            # Add distance for interior solutions
            for i in range(1, n - 1):
                distance = (sorted_values[i + 1] - sorted_values[i - 1]) / obj_range
                chrom_idx = sorted_indices[i]
                front[chrom_idx].metadata["crowding_distance"] += distance

    def get_distance(self, chromosome: Chromosome) -> float:
        """
        Get the crowding distance of a chromosome.

        Args:
            chromosome: Chromosome to query

        Returns:
            Crowding distance value (higher = more isolated)
        """
        return chromosome.metadata.get("crowding_distance", 0.0)

    def __repr__(self) -> str:
        return "CrowdingDistance()"
