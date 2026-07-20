"""Uniform Crossover operator."""

import random
from typing import List, Tuple
from .base import CrossoverOperator
from ...models.chromosome import Chromosome


class UniformCrossover(CrossoverOperator):
    """
    Uniform Crossover operator.

    For each gene position, randomly select which parent contributes
    the gene to each offspring. This is the preferred crossover for
    the assignment problem because:

    - Each student's assignment is largely independent
    - Creates more diversity than single-point crossover
    - Compatible with integer vector representation

    Note: PMX and Order Crossover are NOT suitable here because they
    assume each value appears only once (like TSP), but in our problem
    multiple students can be assigned to the same professor.

    Usage:
        crossover = UniformCrossover(crossover_rate=0.8)
        child1, child2 = crossover.crossover(parent1, parent2)
    """

    def __init__(self, crossover_rate: float = 0.8):
        """
        Initialize Uniform Crossover.

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
        Apply uniform crossover.

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
        child1_genes: List[str] = []
        child2_genes: List[str] = []

        for i in range(length):
            if random.random() < 0.5:
                # Child1 gets from parent1, child2 gets from parent2
                child1_genes.append(parent1.genes[i])
                child2_genes.append(parent2.genes[i])
            else:
                # Child1 gets from parent2, child2 gets from parent1
                child1_genes.append(parent2.genes[i])
                child2_genes.append(parent1.genes[i])

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
        return "UniformCrossover"

    def __repr__(self) -> str:
        return f"UniformCrossover(rate={self.crossover_rate})"
