"""Swap Mutation operator."""

import random
from typing import List
from .base import MutationOperator
from ...models.chromosome import Chromosome


class SwapMutation(MutationOperator):
    """
    Swap Mutation operator.

    Selects two random positions and swaps their professor assignments.
    This creates milder changes compared to random reset.

    Useful as a complementary operator to Random Reset Mutation
    because:
    - Preserves the set of assigned professors
    - Creates local search behavior
    - Good for fine-tuning solutions

    Usage:
        mutation = SwapMutation(mutation_rate=0.1)
        mutated = mutation.mutate(chromosome, professor_ids)
    """

    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize Swap Mutation.

        Args:
            mutation_rate: Probability of performing a swap (0-1)
        """
        if not 0 <= mutation_rate <= 1:
            raise ValueError(f"mutation_rate must be 0-1, got {mutation_rate}")
        self.mutation_rate = mutation_rate

    def mutate(
        self, chromosome: Chromosome, professor_ids: List[str]
    ) -> Chromosome:
        """
        Apply swap mutation.

        Args:
            chromosome: The chromosome to mutate
            professor_ids: List of valid professor IDs (unused but kept
                          for interface consistency)

        Returns:
            New mutated chromosome with swapped genes
        """
        mutated = chromosome.deep_copy()

        if random.random() < self.mutation_rate and mutated.length >= 2:
            # Select two distinct random positions
            pos1, pos2 = random.sample(range(mutated.length), 2)

            # Swap the genes
            mutated.genes[pos1], mutated.genes[pos2] = (
                mutated.genes[pos2],
                mutated.genes[pos1],
            )

        return mutated

    def get_name(self) -> str:
        """Get operator name."""
        return "SwapMutation"

    def __repr__(self) -> str:
        return f"SwapMutation(rate={self.mutation_rate})"
