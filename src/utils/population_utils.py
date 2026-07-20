"""Population utility functions."""

import random
from typing import List, Optional, Callable
from ..models.chromosome import Chromosome
from ..models.population import Population


def sort_population(
    population: Population, key: Callable[[Chromosome], float], descending: bool = True
) -> Population:
    """
    Sort a population by a key function.

    Args:
        population: Population to sort
        key: Function to extract sort key from chromosome
        descending: If True, sort best first

    Returns:
        New sorted population
    """
    sorted_pop = population.deep_copy()
    sorted_pop.chromosomes.sort(key=key, reverse=descending)
    return sorted_pop


def copy_population(population: Population) -> Population:
    """
    Create a deep copy of a population.

    Args:
        population: Population to copy

    Returns:
        New population with copied chromosomes
    """
    return population.deep_copy()


def select_random(population: Population, count: int) -> List[Chromosome]:
    """
    Select random chromosomes from population.

    Args:
        population: Population to select from
        count: Number of chromosomes to select

    Returns:
        List of selected chromosomes
    """
    if count >= len(population):
        return [c.deep_copy() for c in population]
    selected = random.sample(population.chromosomes, count)
    return [c.deep_copy() for c in selected]


def select_by_fitness(
    population: Population, count: int, proportional: bool = True
) -> List[Chromosome]:
    """
    Select chromosomes based on fitness.

    Args:
        population: Population to select from
        count: Number of chromosomes to select
        proportional: If True, use fitness-proportionate selection

    Returns:
        List of selected chromosomes
    """
    evaluated = [c for c in population if c.fitness is not None]
    if not evaluated:
        return select_random(population, count)

    if proportional:
        # Fitness-proportionate selection
        total_fitness = sum(c.fitness for c in evaluated)
        if total_fitness == 0:
            return select_random(population, count)

        probabilities = [c.fitness / total_fitness for c in evaluated]
        indices = range(len(evaluated))
        selected_indices = random.choices(indices, weights=probabilities, k=count)
        return [evaluated[i].deep_copy() for i in selected_indices]
    else:
        # Just select best
        sorted_eval = sorted(evaluated, key=lambda c: c.fitness, reverse=True)
        return [c.deep_copy() for c in sorted_eval[:count]]


def get_population_statistics(population: Population) -> dict:
    """
    Compute basic population statistics.

    Args:
        population: Population to analyze

    Returns:
        Dictionary with statistics
    """
    if not population:
        return {"size": 0}

    fitnesses = [c.fitness for c in population if c.fitness is not None]
    evaluated = [c for c in population if c.is_evaluated()]

    stats = {
        "size": population.size,
        "evaluated": len(evaluated),
        "unevaluated": population.size - len(evaluated),
    }

    if fitnesses:
        stats["best_fitness"] = max(fitnesses)
        stats["worst_fitness"] = min(fitnesses)
        stats["avg_fitness"] = sum(fitnesses) / len(fitnesses)
        stats["fitness_std"] = (
            sum((f - stats["avg_fitness"]) ** 2 for f in fitnesses) / len(fitnesses)
        ) ** 0.5
    else:
        stats["best_fitness"] = None
        stats["worst_fitness"] = None
        stats["avg_fitness"] = None
        stats["fitness_std"] = None

    return stats


def merge_populations(*populations: Population) -> Population:
    """
    Merge multiple populations into one.

    Args:
        *populations: Populations to merge

    Returns:
        New merged population
    """
    merged = Population()
    for pop in populations:
        for chromosome in pop:
            merged.add(chromosome.deep_copy())
    return merged


def truncate_population(population: Population, size: int) -> Population:
    """
    Truncate population to specified size (keeping best).

    Args:
        population: Population to truncate
        size: Target size

    Returns:
        Truncated population
    """
    if population.size <= size:
        return population.deep_copy()

    # Sort by fitness (best first)
    sorted_pop = sort_population(
        population,
        key=lambda c: c.fitness if c.fitness is not None else float("-inf"),
        descending=True,
    )

    truncated = Population(generation=population.generation)
    for i in range(size):
        truncated.add(sorted_pop[i].deep_copy())
    return truncated


def compute_diversity(population: Population) -> float:
    """
    Compute genetic diversity of population.

    Measured as average Hamming distance between all pairs of chromosomes.

    Args:
        population: Population to analyze

    Returns:
        Diversity value (0-1, higher is more diverse)
    """
    if population.size < 2:
        return 0.0

    total_distance = 0
    count = 0

    for i in range(population.size):
        for j in range(i + 1, population.size):
            chrom_i = population[i]
            chrom_j = population[j]

            # Hamming distance (normalized)
            mismatches = sum(
                1 for a, b in zip(chrom_i.genes, chrom_j.genes) if a != b
            )
            total_distance += mismatches / chrom_i.length
            count += 1

    return total_distance / count if count > 0 else 0.0


def __repr__() -> str:
    return "PopulationUtils()"
