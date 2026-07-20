"""Student data model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Student:
    """
    Represents a graduate student in the assignment problem.

    Attributes:
        student_id: Unique identifier (e.g., 'S01')
        name: Full name of the student
        gender: 'Male' or 'Female'
        field: Research field (e.g., 'Artificial Intelligence')
        previous_university: Name of previous university
        previous_gpa: GPA from previous education (0-20 scale)
        current_gpa: Current GPA (0-20 scale)
        entry_type: 'Regular' or 'Quota'
        quality_score: Computed quality score (0-100)
        preference_list: Ordered list of preferred professor IDs
    """

    student_id: str
    name: str
    gender: str
    field: str
    previous_university: str
    previous_gpa: float
    current_gpa: float
    entry_type: str
    quality_score: float
    preference_list: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate student data after initialization."""
        if not 0 <= self.previous_gpa <= 20:
            raise ValueError(f"PreviousGPA must be 0-20, got {self.previous_gpa}")
        if not 0 <= self.current_gpa <= 20:
            raise ValueError(f"CurrentGPA must be 0-20, got {self.current_gpa}")
        if not 0 <= self.quality_score <= 100:
            raise ValueError(f"QualityScore must be 0-100, got {self.quality_score}")
        if self.entry_type not in ("Regular", "Quota"):
            raise ValueError(f"EntryType must be 'Regular' or 'Quota', got {self.entry_type}")

    def get_preference_rank(self, professor_id: str) -> int:
        """
        Get the rank of a professor in student's preference list.

        Args:
            professor_id: The professor to look up

        Returns:
            Rank (1-based), or 0 if not in list
        """
        if professor_id in self.preference_list:
            return self.preference_list.index(professor_id) + 1
        return 0

    def has_preference(self, professor_id: str) -> bool:
        """Check if student has this professor in preference list."""
        return professor_id in self.preference_list

    def __repr__(self) -> str:
        return (
            f"Student(id={self.student_id}, name='{self.name}', "
            f"field='{self.field}', quality={self.quality_score:.1f})"
        )
