"""One-Point Crossover operator."""

import random
from typing import List, Tuple
from .base import CrossoverOperator
from ...models.chromosome import Chromosome


class OnePointCrossover(CrossoverOperator):
    """
    One-Point Crossover operator.

    Selects a random crossover point and exchanges genes after that
    point between two parents.

    While Uniform Crossover is preferred for this problem,
    One-Point Crossover is included as an alternative because:
    - Simple to understand and implement
    - Creates different diversity patterns
    - May work well with certain problem structures

    Usage:
        crossover = OnePointCrossover(crossover_rate=0.8)
        child1, child2 = crossover.crossover(parent1, parent2)
    """

    def __init__(self, crossover_rate: float = 0.8):
        """
        Initialize One-Point Crossover.

        Args:
            crossover_rate: Probability of crossover occurring (0-1)
        """
        if not 0 <= crossover_rate <= 1:
            raise ValueError(f"crossover_rate must be 0-1, got {crossover_rate}")
        self.crossover_rate = crossover_rate

    def crossover(
        self, parent1: Chromosome, parent2: Chromosome
    ) -> Tuple[Chromosome, Chromosome]:
        """
        Apply one-point crossover.

        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome

        Returns:
            Tuple of two offspring chromosomes
        """
        if random.random() > self.crossover_rate:
            # No crossover, return copies of parents
            return parent1.deep_copy(), parent2.deep_copy()

        if parent1.length != parent2.length:
            raise ValueError(
                f"Parents must have same length: "
                f"{parent1.length} != {parent2.length}"
            )

        length = parent1.length
        if length < 2:
            return parent1.deep_copy(), parent2.deep_copy()

        # Select crossover point (1 to length-1)
        crossover_point = random.randint(1, length - 1)

        # Create offspring
        child1_genes: List[str] = (
            parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        )
        child2_genes: List[str] = (
            parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        )

        child1 = Chromosome(
            genes=child1_genes,
            student_ids=parent1.student_ids.copy(),
        )
        child2 = Chromosome(
            genes=child2_genes,
            student_ids=parent2.student_ids.copy(),
        )

        return child1, child2

    def get_name(self) -> str:
        """Get operator name."""
        return "OnePointCrossover"

    def __repr__(self) -> str:
        return f"OnePointCrossover(rate={self.crossover_rate})"
