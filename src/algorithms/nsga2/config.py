"""Configuration for NSGA-II algorithm."""

from dataclasses import dataclass


@dataclass
class NSGA2Config:
    """
    Configuration specific to NSGA-II algorithm.

    NSGA-II does NOT use weights for objectives (unlike Weighted Sum).
    Instead, it uses Pareto dominance and crowding distance.

    Attributes:
        tournament_size: Number of individuals in tournament selection
        preserve_elitism: Not used in NSGA-II (handled by merging)
        use_constraint_dominance: Whether to use constraint-domination principle
    """

    # Tournament selection size (binary = 2)
    tournament_size: int = 2

    # NSGA-II doesn't use traditional elitism - it merges parent + offspring
    # This parameter is kept for interface compatibility but not used
    preserve_elitism: int = 0

    # Constraint domination principle:
    # If both solutions are infeasible, the one with less violation wins
    # If one is feasible and one infeasible, feasible wins
    use_constraint_dominance: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")

    def __repr__(self) -> str:
        return (
            f"NSGA2Config(\n"
            f"  tournament_size={self.tournament_size},\n"
            f"  use_constraint_dominance={self.use_constraint_dominance}\n"
            f")"
        )
