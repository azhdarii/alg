"""Configuration for Weighted Sum Genetic Algorithm."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WeightedSumConfig:
    """
    Configuration specific to Weighted Sum approach.

    This extends the base algorithm configuration with weight
    parameters for combining multiple objectives into a single
    fitness value.

    Attributes:
        weights: List of weights for [student_sat, professor_sat, fairness]
        constraint_weight: Weight for constraint penalty in fitness
        normalize_objectives: Whether to normalize objectives to [0, 1]
        preserve_elitism: Number of best individuals to preserve
        tournament_size: Number of individuals in tournament selection
    """

    # Weights for objective combination
    # Must sum to 1.0 for proper normalization
    weights: List[float] = None

    # Weight for constraint penalty (higher = harder constraints)
    constraint_weight: float = 0.01

    # Whether to normalize objectives before combining
    normalize_objectives: bool = True

    # Elitism: number of best individuals to carry over unchanged
    preserve_elitism: int = 2

    # Tournament selection size
    tournament_size: int = 3

    def __post_init__(self) -> None:
        """Set default weights if not provided."""
        if self.weights is None:
            self.weights = [0.4, 0.4, 0.2]  # [student, professor, fairness]

        if len(self.weights) != 3:
            raise ValueError("weights must have exactly 3 elements")

        if abs(sum(self.weights) - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1.0, got {sum(self.weights)}")

        if any(w < 0 for w in self.weights):
            raise ValueError("All weights must be non-negative")

        if self.preserve_elitism < 0:
            raise ValueError("preserve_elitism must be non-negative")

        if self.tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")

    @property
    def weight_student(self) -> float:
        """Weight for student satisfaction."""
        return self.weights[0]

    @property
    def weight_professor(self) -> float:
        """Weight for professor satisfaction."""
        return self.weights[1]

    @property
    def weight_fairness(self) -> float:
        """Weight for fairness (inverted: lower variance = higher fitness)."""
        return self.weights[2]

    def __repr__(self) -> str:
        return (
            f"WeightedSumConfig(\n"
            f"  weights={self.weights},\n"
            f"  constraint_weight={self.constraint_weight},\n"
            f"  preserve_elitism={self.preserve_elitism},\n"
            f"  tournament_size={self.tournament_size}\n"
            f")"
        )
