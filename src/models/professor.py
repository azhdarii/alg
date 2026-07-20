"""Professor data model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Professor:
    """
    Represents a professor/supervisor in the assignment problem.

    Attributes:
        professor_id: Unique identifier (e.g., 'P01')
        name: Full name of the professor
        field: Primary research field
        academic_rank: 'Professor', 'Associate Professor', or 'Assistant Professor'
        capacity: Maximum number of students
        min_capacity: Minimum number of students
        office: Office location
        email: Contact email
        preference_list: Ordered list of preferred student IDs
    """

    professor_id: str
    name: str
    field: str
    academic_rank: str
    capacity: int
    min_capacity: int
    office: str
    email: str
    preference_list: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate professor data after initialization."""
        if self.capacity < 1:
            raise ValueError(f"Capacity must be >= 1, got {self.capacity}")
        if self.min_capacity < 0:
            raise ValueError(f"MinCapacity must be >= 0, got {self.min_capacity}")
        if self.min_capacity > self.capacity:
            raise ValueError(
                f"MinCapacity ({self.min_capacity}) cannot exceed "
                f"Capacity ({self.capacity})"
            )

    def get_preference_rank(self, student_id: str) -> int:
        """
        Get the rank of a student in professor's preference list.

        Args:
            student_id: The student to look up

        Returns:
            Rank (1-based), or 0 if not in list
        """
        if student_id in self.preference_list:
            return self.preference_list.index(student_id) + 1
        return 0

    def has_preference(self, student_id: str) -> bool:
        """Check if professor has this student in preference list."""
        return student_id in self.preference_list

    def __repr__(self) -> str:
        return (
            f"Professor(id={self.professor_id}, name='{self.name}', "
            f"field='{self.field}', capacity={self.capacity})"
        )
