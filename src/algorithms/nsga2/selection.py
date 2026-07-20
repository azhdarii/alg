"""Selection operators for NSGA-II."""

import random
from typing import List
from ...models.chromosome import Chromosome
from ...models.population import Population


class NSGA2BinaryTournamentSelection:
    """
    Binary Tournament Selection for NSGA-II.

    Selects individuals based on:
    1. Lower Pareto rank wins
    2. If ranks are equal, higher Crowding Distance wins

    This is the standard selection operator for NSGA-II.
    It does NOT use scalar fitness values like Weighted Sum.

    Design Note:
        This class is separate from WeightedSumGA's BinaryTournamentSelection
        because the comparison logic is fundamentally different.

    Follows Single Responsibility Principle: only handles NSGA-II selection.
    """

    def __init__(self, tournament_size: int = 2):
        """
        Initialize NSGA-II binary tournament selection.

        Args:
            tournament_size: Number of individuals in each tournament
                           (default 2 for binary tournament)
        """
        if tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")
        self.tournament_size = tournament_size

    def select(self, population: Population) -> Chromosome:
        """
        Select one individual using NSGA-II binary tournament.

        Comparison rule:
        - Lower rank wins
        - If ranks equal, higher crowding distance wins

        Args:
            population: Population to select from

        Returns:
            Selected chromosome (deep copy)
        """
        # Sample tournament individuals
        tournament = random.sample(population.chromosomes, self.tournament_size)

        # Select the best using NSGA-II comparison
        best = tournament[0]
        for i in range(1, len(tournament)):
            if self._better(tournament[i], best):
                best = tournament[i]

        return best.deep_copy()

    def _better(self, chrom_a: Chromosome, chrom_b: Chromosome) -> bool:
        """
        Compare two chromosomes using NSGA-II criteria.

        Args:
            chrom_a: First chromosome
            chrom_b: Second chromosome

        Returns:
            True if chrom_a is better than chrom_b
        """
        rank_a = chrom_a.metadata.get("rank", float("inf"))
        rank_b = chrom_b.metadata.get("rank", float("inf"))

        # Lower rank is better
        if rank_a < rank_b:
            return True
        elif rank_a > rank_b:
            return False

        # Same rank: higher crowding distance is better
        dist_a = chrom_a.metadata.get("crowding_distance", 0.0)
        dist_b = chrom_b.metadata.get("crowding_distance", 0.0)

        return dist_a > dist_b

    def select_pair(self, population: Population) -> tuple:
        """
        Select two parents using NSGA-II binary tournament.

        Ensures the two parents are different individuals.

        Args:
            population: Population to select from

        Returns:
            Tuple of two selected chromosomes
        """
        parent1 = self.select(population)

        # Select parent2, ensuring it's different from parent1
        max_attempts = 10
        for _ in range(max_attempts):
            parent2 = self.select(population)
            if parent2.genes != parent1.genes:
                break

        return parent1, parent2

    def select_batch(self, population: Population, count: int) -> List[Chromosome]:
        """
        Select multiple individuals using NSGA-II binary tournament.

        Args:
            population: Population to select from
            count: Number of individuals to select

        Returns:
            List of selected chromosomes
        """
        return [self.select(population) for _ in range(count)]

    def __repr__(self) -> str:
        return f"NSGA2BinaryTournamentSelection(tournament_size={self.tournament_size})"
