"""Selection operators for Weighted Sum GA."""

import random
from typing import List
from ...models.chromosome import Chromosome
from ...models.population import Population


class BinaryTournamentSelection:
    """
    Binary Tournament Selection based on fitness.

    Selects two random individuals and returns the one with higher fitness.
    This is the standard selection operator for Weighted Sum GA.

    Why Binary Tournament:
    - Simple to implement
    - Provides selection pressure without requiring fitness normalization
    - Works well with both positive and negative fitness values
    - Can be easily adapted for NSGA-II (using Pareto rank + crowding)

    Design Note:
        This class is kept separate from the algorithm to allow
        easy replacement with other selection methods.

    Follows Single Responsibility Principle: only handles selection.
    """

    def __init__(self, tournament_size: int = 3):
        """
        Initialize tournament selection.

        Args:
            tournament_size: Number of individuals in each tournament
                           (default 2 for binary tournament)
        """
        if tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")
        self.tournament_size = tournament_size

    def select(self, population: Population) -> Chromosome:
        """
        Select one individual using tournament selection.

        Args:
            population: Population to select from

        Returns:
            Selected chromosome (deep copy)
        """
        # Sample tournament_size individuals
        tournament = random.sample(population.chromosomes, self.tournament_size)

        # Select the one with highest fitness
        best = max(tournament, key=lambda c: c.fitness if c.fitness is not None else float("-inf"))

        return best.deep_copy()

    def select_pair(self, population: Population) -> tuple:
        """
        Select two parents using tournament selection.

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
        Select multiple individuals using tournament selection.

        Args:
            population: Population to select from
            count: Number of individuals to select

        Returns:
            List of selected chromosomes
        """
        return [self.select(population) for _ in range(count)]

    def __repr__(self) -> str:
        return f"BinaryTournamentSelection(tournament_size={self.tournament_size})"


class RouletteWheelSelection:
    """
    Roulette Wheel (Fitness-Proportionate) Selection.

    Alternative selection method where probability of selection
    is proportional to fitness. Included for completeness but
    Binary Tournament is preferred for Weighted Sum.

    Note: Requires all fitness values to be positive.
    """

    def select(self, population: Population) -> Chromosome:
        """
        Select one individual using roulette wheel selection.

        Args:
            population: Population to select from

        Returns:
            Selected chromosome
        """
        # Get fitness values
        fitnesses = []
        for c in population:
            if c.fitness is not None and c.fitness > 0:
                fitnesses.append(c.fitness)
            else:
                fitnesses.append(0.0)

        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            # Fallback to random selection
            return random.choice(population.chromosomes).deep_copy()

        # Compute selection probabilities
        probabilities = [f / total_fitness for f in fitnesses]

        # Select using cumulative probabilities
        r = random.random()
        cumulative = 0.0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return population[i].deep_copy()

        # Fallback (should not happen)
        return population[-1].deep_copy()

    def __repr__(self) -> str:
        return "RouletteWheelSelection()"
