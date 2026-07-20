"""Base class for crossover operators (Strategy Pattern)."""

from abc import ABC, abstractmethod
from typing import List, Tuple
from ...models.chromosome import Chromosome


class CrossoverOperator(ABC):
    """
    Abstract base class for crossover operators.

    This implements the Strategy Pattern, allowing different crossover
    strategies to be used interchangeably.

    All crossover operators must implement the crossover() method.
    """

    @abstractmethod
    def crossover(
        self, parent1: Chromosome, parent2: Chromosome
    ) -> Tuple[Chromosome, Chromosome]:
        """
        Apply crossover to two parents.

        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome

        Returns:
            Tuple of two offspring chromosomes
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this crossover operator."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
