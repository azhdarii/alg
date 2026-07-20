"""Population data model."""

from dataclasses import dataclass, field
from typing import List, Optional, Iterator
from .chromosome import Chromosome


@dataclass
class PopulationStatistics:
    """
    Statistics for a population.

    Attributes:
        generation: Current generation number
        size: Population size
        best_fitness: Best fitness value
        worst_fitness: Worst fitness value
        avg_fitness: Average fitness value
        best_student_satisfaction: Best student satisfaction
        best_professor_satisfaction: Best professor satisfaction
        best_fairness: Best fairness value
        avg_student_satisfaction: Average student satisfaction
        avg_professor_satisfaction: Average professor satisfaction
        avg_fairness: Average fairness value
        total_capacity_violations: Total capacity violations
        total_field_mismatches: Total field mismatches
    """

    generation: int = 0
    size: int = 0
    best_fitness: float = 0.0
    worst_fitness: float = 0.0
    avg_fitness: float = 0.0
    best_student_satisfaction: float = 0.0
    best_professor_satisfaction: float = 0.0
    best_fairness: float = 0.0
    avg_student_satisfaction: float = 0.0
    avg_professor_satisfaction: float = 0.0
    avg_fairness: float = 0.0
    total_capacity_violations: float = 0.0
    total_field_mismatches: int = 0

    def __repr__(self) -> str:
        return (
            f"PopStats(gen={self.generation}, size={self.size}, "
            f"best_fit={self.best_fitness:.4f}, avg_fit={self.avg_fitness:.4f})"
        )


@dataclass
class Population:
    """
    Represents a population of chromosomes.

    A population is a collection of candidate solutions that evolve
    over generations in the genetic algorithm.

    Attributes:
        chromosomes: List of Chromosome objects
        generation: Current generation number
        statistics: Population statistics (computed on demand)
    """

    chromosomes: List[Chromosome] = field(default_factory=list)
    generation: int = 0
    statistics: Optional[PopulationStatistics] = None

    @property
    def size(self) -> int:
        """Number of chromosomes in the population."""
        return len(self.chromosomes)

    def add(self, chromosome: Chromosome) -> None:
        """Add a chromosome to the population."""
        self.chromosomes.append(chromosome)

    def get(self, index: int) -> Chromosome:
        """Get chromosome at given index."""
        return self.chromosomes[index]

    def remove(self, index: int) -> Chromosome:
        """Remove and return chromosome at given index."""
        return self.chromosomes.pop(index)

    def clear(self) -> None:
        """Remove all chromosomes from the population."""
        self.chromosomes.clear()
        self.statistics = None

    def sort_by_fitness(self, descending: bool = True) -> None:
        """
        Sort chromosomes by fitness value.

        Args:
            descending: If True, best fitness first
        """
        self.chromosomes.sort(
            key=lambda c: c.fitness if c.fitness is not None else float("-inf"),
            reverse=descending,
        )

    def get_best(self) -> Optional[Chromosome]:
        """Get the chromosome with best fitness."""
        if not self.chromosomes:
            return None
        evaluated = [c for c in self.chromosomes if c.fitness is not None]
        if not evaluated:
            return None
        return max(evaluated, key=lambda c: c.fitness)

    def get_worst(self) -> Optional[Chromosome]:
        """Get the chromosome with worst fitness."""
        if not self.chromosomes:
            return None
        evaluated = [c for c in self.chromosomes if c.fitness is not None]
        if not evaluated:
            return None
        return min(evaluated, key=lambda c: c.fitness)

    def compute_statistics(self) -> PopulationStatistics:
        """
        Compute and cache population statistics.

        Returns:
            PopulationStatistics object
        """
        if not self.chromosomes:
            self.statistics = PopulationStatistics(
                generation=self.generation, size=0
            )
            return self.statistics

        evaluated = [c for c in self.chromosomes if c.is_evaluated()]
        if not evaluated:
            self.statistics = PopulationStatistics(
                generation=self.generation, size=self.size
            )
            return self.statistics

        fitnesses = [c.fitness for c in evaluated if c.fitness is not None]
        student_sats = [
            c.objectives.student_satisfaction
            for c in evaluated
            if c.objectives
        ]
        prof_sats = [
            c.objectives.professor_satisfaction
            for c in evaluated
            if c.objectives
        ]
        fairness_vals = [c.objectives.fairness for c in evaluated if c.objectives]
        cap_violations = [
            c.constraints.capacity_violation
            for c in evaluated
            if c.constraints
        ]
        field_mismatches = [
            c.constraints.field_mismatch_count
            for c in evaluated
            if c.constraints
        ]

        self.statistics = PopulationStatistics(
            generation=self.generation,
            size=self.size,
            best_fitness=max(fitnesses) if fitnesses else 0.0,
            worst_fitness=min(fitnesses) if fitnesses else 0.0,
            avg_fitness=sum(fitnesses) / len(fitnesses) if fitnesses else 0.0,
            best_student_satisfaction=max(student_sats) if student_sats else 0.0,
            best_professor_satisfaction=max(prof_sats) if prof_sats else 0.0,
            best_fairness=max(fairness_vals) if fairness_vals else 0.0,
            avg_student_satisfaction=(
                sum(student_sats) / len(student_sats) if student_sats else 0.0
            ),
            avg_professor_satisfaction=(
                sum(prof_sats) / len(prof_sats) if prof_sats else 0.0
            ),
            avg_fairness=(
                sum(fairness_vals) / len(fairness_vals) if fairness_vals else 0.0
            ),
            total_capacity_violations=sum(cap_violations),
            total_field_mismatches=sum(field_mismatches),
        )
        return self.statistics

    def deep_copy(self) -> "Population":
        """
        Create a deep copy of the population.

        Returns:
            New Population with copied chromosomes
        """
        return Population(
            chromosomes=[c.deep_copy() for c in self.chromosomes],
            generation=self.generation,
        )

    def __iter__(self) -> Iterator[Chromosome]:
        """Iterate over chromosomes."""
        return iter(self.chromosomes)

    def __len__(self) -> int:
        """Number of chromosomes."""
        return len(self.chromosomes)

    def __getitem__(self, index: int) -> Chromosome:
        """Get chromosome by index."""
        return self.chromosomes[index]

    def __repr__(self) -> str:
        return (
            f"Population(generation={self.generation}, "
            f"size={self.size})"
        )
