"""Chromosome (solution) representation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import copy


@dataclass
class ObjectiveValues:
    """
    Stores objective function values separately.

    Attributes:
        student_satisfaction: Student satisfaction score (higher is better)
        professor_satisfaction: Professor satisfaction score (higher is better)
        fairness: Fairness measure (lower variance is better)
    """

    student_satisfaction: float = 0.0
    professor_satisfaction: float = 0.0
    fairness: float = 0.0

    def to_list(self) -> List[float]:
        """Convert to list for algorithm processing."""
        return [self.student_satisfaction, self.professor_satisfaction, self.fairness]

    def __repr__(self) -> str:
        return (
            f"Objectives(student={self.student_satisfaction:.2f}, "
            f"professor={self.professor_satisfaction:.2f}, "
            f"fairness={self.fairness:.2f})"
        )


@dataclass
class ConstraintValues:
    """
    Stores constraint violation values separately.

    Attributes:
        capacity_violation: Total capacity violation penalty
        field_mismatch_count: Number of field mismatches
        total_penalty: Sum of all constraint penalties
    """

    capacity_violation: float = 0.0
    field_mismatch_count: int = 0
    total_penalty: float = 0.0

    def to_list(self) -> List[float]:
        """Convert to list for algorithm processing."""
        return [self.capacity_violation, float(self.field_mismatch_count)]

    def __repr__(self) -> str:
        return (
            f"Constraints(capacity_viol={self.capacity_violation:.2f}, "
            f"field_mismatch={self.field_mismatch_count}, "
            f"total_penalty={self.total_penalty:.2f})"
        )


@dataclass
class Chromosome:
    """
    Represents a complete solution (assignment of all students to professors).

    The chromosome uses Integer Vector representation where each gene
    represents the professor ID assigned to the corresponding student.

    Attributes:
        genes: List of professor IDs (index = student position)
        student_ids: List of student IDs in order
        objectives: Computed objective values (None if not evaluated)
        constraints: Computed constraint violations (None if not evaluated)
        fitness: Aggregated fitness value (None if not computed)
        metadata: Additional algorithm-specific data
    """

    genes: List[str]
    student_ids: List[str]
    objectives: Optional[ObjectiveValues] = None
    constraints: Optional[ConstraintValues] = None
    fitness: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate chromosome after initialization."""
        if len(self.genes) != len(self.student_ids):
            raise ValueError(
                f"Genes length ({len(self.genes)}) must match "
                f"student_ids length ({len(self.student_ids)})"
            )

    @property
    def length(self) -> int:
        """Number of genes (students) in this chromosome."""
        return len(self.genes)

    def get_assignment(self, student_index: int) -> str:
        """
        Get the professor assigned to a student.

        Args:
            student_index: Index of the student

        Returns:
            Professor ID
        """
        return self.genes[student_index]

    def set_assignment(self, student_index: int, professor_id: str) -> None:
        """
        Set the professor assigned to a student.

        Args:
            student_index: Index of the student
            professor_id: Professor to assign
        """
        self.genes[student_index] = professor_id
        # Reset evaluation cache when solution changes
        self.objectives = None
        self.constraints = None
        self.fitness = None

    def get_student_id(self, index: int) -> str:
        """Get student ID at given index."""
        return self.student_ids[index]

    def get_student_index(self, student_id: str) -> int:
        """
        Get the index of a student in this chromosome.

        Args:
            student_id: Student to find

        Returns:
            Index of the student, or -1 if not found
        """
        if student_id in self.student_ids:
            return self.student_ids.index(student_id)
        return -1

    def deep_copy(self) -> "Chromosome":
        """
        Create a deep copy of this chromosome.

        Returns:
            New Chromosome with copied data
        """
        return Chromosome(
            genes=self.genes.copy(),
            student_ids=self.student_ids.copy(),
            objectives=copy.deepcopy(self.objectives),
            constraints=copy.deepcopy(self.constraints),
            fitness=self.fitness,
            metadata=self.metadata.copy(),
        )

    def copy_genes(self) -> List[str]:
        """Create a copy of the genes list."""
        return self.genes.copy()

    def is_evaluated(self) -> bool:
        """Check if this chromosome has been evaluated."""
        return self.objectives is not None and self.constraints is not None

    def to_assignment_dict(self) -> Dict[str, str]:
        """
        Convert to dictionary mapping student_id -> professor_id.

        Returns:
            Dictionary of assignments
        """
        return dict(zip(self.student_ids, self.genes))

    def count_professor_assignments(self) -> Dict[str, int]:
        """
        Count how many students are assigned to each professor.

        Returns:
            Dictionary mapping professor_id -> count
        """
        counts: Dict[str, int] = {}
        for prof_id in self.genes:
            counts[prof_id] = counts.get(prof_id, 0) + 1
        return counts

    def pretty_print(self) -> str:
        """
        Generate a human-readable representation.

        Returns:
            Formatted string showing all assignments
        """
        lines = ["Chromosome:", "-" * 40]
        for i, (student_id, prof_id) in enumerate(
            zip(self.student_ids, self.genes)
        ):
            lines.append(f"  {student_id} -> {prof_id}")

        if self.objectives:
            lines.append("-" * 40)
            lines.append(f"  {self.objectives}")

        if self.constraints:
            lines.append(f"  {self.constraints}")

        if self.fitness is not None:
            lines.append(f"  Fitness: {self.fitness:.4f}")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"Chromosome(length={self.length}, "
            f"evaluated={self.is_evaluated()}, "
            f"fitness={self.fitness})"
        )
