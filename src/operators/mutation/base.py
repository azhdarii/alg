"""Base class for mutation operators (Strategy Pattern)."""

from abc import ABC, abstractmethod
from typing import List
from ...models.chromosome import Chromosome


class MutationOperator(ABC):
    """
    Abstract base class for mutation operators.

    This implements the Strategy Pattern, allowing different mutation
    strategies to be used interchangeably.

    All mutation operators must implement the mutate() method.
    """

    @abstractmethod
    def mutate(self, chromosome: Chromosome, professor_ids: List[str]) -> Chromosome:
        """
        Apply mutation to a chromosome.

        Args:
            chromosome: The chromosome to mutate
            professor_ids: List of valid professor IDs for gene values

        Returns:
            A new mutated chromosome (original is not modified)
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this mutation operator."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
