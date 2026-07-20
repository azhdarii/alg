"""Fitness calculation for Weighted Sum approach."""

from typing import List
from ...models.chromosome import Chromosome, ObjectiveValues, ConstraintValues
from .config import WeightedSumConfig


class WeightedSumFitness:
    """
    Computes fitness by combining objectives with weights.

    This is the core differentiator of the Weighted Sum approach:
    multiple objectives are scalarized into a single fitness value.

    Fitness Formula:
        fitness = w1 * student_sat + w2 * prof_sat + w3 * (1 - fairness)
                  - constraint_penalty

    Where:
        - student_sat, prof_sat are normalized to [0, 1] (higher is better)
        - fairness is normalized to [0, 1] where 0 = most fair (inverted)
        - constraint_penalty is weighted by constraint_weight

    Design Note:
        This class is intentionally NOT part of the shared infrastructure.
        NSGA-II will have its own fitness calculation (Pareto-based).

    Follows Single Responsibility Principle: only handles fitness computation.
    """

    def __init__(self, config: WeightedSumConfig):
        """
        Initialize the fitness calculator.

        Args:
            config: Weighted Sum configuration with weights
        """
        self.config = config

    def compute_fitness(self, chromosome: Chromosome) -> float:
        """
        Compute scalar fitness value for a chromosome.

        Args:
            chromosome: Chromosome with objectives and constraints already computed

        Returns:
            Scalar fitness value (higher is better)

        Raises:
            ValueError: If chromosome has not been evaluated
        """
        if not chromosome.is_evaluated():
            raise ValueError(
                "Chromosome must be evaluated before computing fitness. "
                "Call objective_evaluator.evaluate() and constraint_evaluator.evaluate() first."
            )

        objectives = chromosome.objectives
        constraints = chromosome.constraints

        # Compute weighted objective components
        student_component = self.config.weight_student * objectives.student_satisfaction
        professor_component = self.config.weight_professor * objectives.professor_satisfaction

        # Fairness is inverted: lower variance = higher fitness
        fairness_component = self.config.weight_fairness * (1.0 - objectives.fairness)

        # Combine objectives
        objective_fitness = student_component + professor_component + fairness_component

        # Subtract constraint penalty
        penalty = constraints.total_penalty * self.config.constraint_weight

        return objective_fitness - penalty

    def compute_fitness_batch(self, chromosomes: List[Chromosome]) -> List[float]:
        """
        Compute fitness for a list of chromosomes.

        Args:
            chromosomes: List of evaluated chromosomes

        Returns:
            List of fitness values in same order
        """
        return [self.compute_fitness(c) for c in chromosomes]

    def compute_population_fitness(self, population) -> None:
        """
        Compute and assign fitness to all chromosomes in population.

        This is a convenience method that updates fitness in-place.

        Args:
            population: Population with evaluated chromosomes
        """
        for chromosome in population:
            if chromosome.is_evaluated() and chromosome.fitness is None:
                chromosome.fitness = self.compute_fitness(chromosome)

    def get_fitness_components(self, chromosome: Chromosome) -> dict:
        """
        Get detailed breakdown of fitness calculation.

        Useful for debugging and analysis.

        Args:
            chromosome: Evaluated chromosome

        Returns:
            Dictionary with fitness components
        """
        objectives = chromosome.objectives
        constraints = chromosome.constraints

        student_component = self.config.weight_student * objectives.student_satisfaction
        professor_component = self.config.weight_professor * objectives.professor_satisfaction
        fairness_component = self.config.weight_fairness * (1.0 - objectives.fairness)
        penalty = constraints.total_penalty * self.config.constraint_weight

        return {
            "student_component": student_component,
            "professor_component": professor_component,
            "fairness_component": fairness_component,
            "objective_sum": student_component + professor_component + fairness_component,
            "penalty": penalty,
            "total_fitness": chromosome.fitness,
        }

    def __repr__(self) -> str:
        return (
            f"WeightedSumFitness(\n"
            f"  weights={self.config.weights},\n"
            f"  constraint_weight={self.config.constraint_weight}\n"
            f")"
        )
