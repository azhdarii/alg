"""Replacement strategies for Weighted Sum GA."""

from typing import List
from ...models.chromosome import Chromosome
from ...models.population import Population


class ElitistReplacement:
    """
    Elitist Replacement Strategy.

    Preserves the best individuals from the current generation
    and combines them with new offspring to form the next generation.

    This ensures:
    1. Monotonic improvement (best solution never degrades)
    2. Diversity maintenance (elites + offspring)
    3. Convergence guarantee

    Design Note:
        Elitism is critical for Weighted Sum GA because the scalar
        fitness can fluctuate. Without elitism, good solutions may
        be lost. NSGA-II handles this differently via Pareto fronts.

    Follows Single Responsibility Principle: only handles replacement.
    """

    def __init__(self, preserve_count: int = 2):
        """
        Initialize elitist replacement.

        Args:
            preserve_count: Number of best individuals to preserve
        """
        if preserve_count < 0:
            raise ValueError("preserve_count must be non-negative")
        self.preserve_count = preserve_count

    def create_next_generation(
        self,
        current_population: Population,
        offspring: List[Chromosome],
    ) -> Population:
        """
        Create next generation using elitist replacement.

        Strategy:
        1. Sort current population by fitness
        2. Take top preserve_count individuals (elites)
        3. Fill remaining slots with offspring
        4. If offspring < remaining slots, add more from current population

        Args:
            current_population: Current generation (evaluated)
            offspring: New offspring (may not be evaluated yet)

        Returns:
            New Population of same size
        """
        target_size = current_population.size

        # Sort current population by fitness (best first)
        sorted_current = sorted(
            current_population.chromosomes,
            key=lambda c: c.fitness if c.fitness is not None else float("-inf"),
            reverse=True,
        )

        # Take elites
        elites = [
            c.deep_copy()
            for c in sorted_current[:self.preserve_count]
        ]

        # Fill remaining with offspring
        remaining_slots = target_size - len(elites)
        next_generation = elites + offspring[:remaining_slots]

        # If not enough offspring, pad with best from current population
        if len(next_generation) < target_size:
            # Add from current population (after elites)
            for c in sorted_current[self.preserve_count:]:
                if len(next_generation) >= target_size:
                    break
                next_generation.append(c.deep_copy())

        # Create new population
        new_population = Population(
            chromosomes=next_generation[:target_size],
            generation=current_population.generation + 1,
        )

        return new_population

    def get_elites(self, population: Population) -> List[Chromosome]:
        """
        Get the elite individuals from population.

        Args:
            population: Current population

        Returns:
            List of elite chromosomes (deep copies)
        """
        sorted_pop = sorted(
            population.chromosomes,
            key=lambda c: c.fitness if c.fitness is not None else float("-inf"),
            reverse=True,
        )
        return [c.deep_copy() for c in sorted_pop[:self.preserve_count]]

    def __repr__(self) -> str:
        return f"ElitistReplacement(preserve_count={self.preserve_count})"


class GenerationalReplacement:
    """
    Generational Replacement (No Elitism).

    Completely replaces the current population with offspring.
    Simpler but may lose good solutions.

    Included for comparison purposes.
    """

    def create_next_generation(
        self,
        current_population: Population,
        offspring: List[Chromosome],
    ) -> Population:
        """
        Create next generation by completely replacing current population.

        Args:
            current_population: Current generation (ignored)
            offspring: New offspring

        Returns:
            New Population from offspring only
        """
        return Population(
            chromosomes=offspring[:current_population.size],
            generation=current_population.generation + 1,
        )

    def __repr__(self) -> str:
        return "GenerationalReplacement()"
