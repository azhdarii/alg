"""Random Reset Mutation operator."""

import random
from typing import List
from .base import MutationOperator
from ...models.chromosome import Chromosome


class RandomResetMutation(MutationOperator):
    """
    Random Reset Mutation operator.

    For each gene with probability p, replace the professor ID
    with a randomly selected one from the valid professor list.

    This is the primary mutation operator for the assignment problem
    because:
    - Simple to implement
    - Creates diversity
    - Compatible with integer vector representation
    - Common in assignment problems

    Usage:
        mutation = RandomResetMutation(mutation_rate=0.1)
        mutated = mutation.mutate(chromosome, professor_ids)
    """

    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize Random Reset Mutation.

        Args:
            mutation_rate: Probability of mutating each gene (0-1)
        """
        if not 0 <= mutation_rate <= 1:
            raise ValueError(f"mutation_rate must be 0-1, got {mutation_rate}")
        self.mutation_rate = mutation_rate

    def mutate(
        self, chromosome: Chromosome, professor_ids: List[str]
    ) -> Chromosome:
        """
        Apply random reset mutation.

        Args:
            chromosome: The chromosome to mutate
            professor_ids: List of valid professor IDs

        Returns:
            New mutated chromosome
        """
        mutated = chromosome.deep_copy()

        for i in range(mutated.length):
            if random.random() < self.mutation_rate:
                # Select a random professor (could be same as current)
                new_prof = random.choice(professor_ids)
                mutated.genes[i] = new_prof

        return mutated

    def get_name(self) -> str:
        """Get operator name."""
        return "RandomResetMutation"

    def __repr__(self) -> str:
        return f"RandomResetMutation(rate={self.mutation_rate})"
