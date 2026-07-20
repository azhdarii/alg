"""Assignment data model."""

from dataclasses import dataclass


@dataclass
class Assignment:
    """
    Represents a single student-professor assignment.

    This is an immutable record of an assignment decision.
    Used for storing final results or intermediate solutions.

    Attributes:
        student_id: The assigned student
        professor_id: The assigned professor
        student_field: Student's research field
        professor_field: Professor's research field
        field_match: Whether fields match
        student_rank: Student's preference rank for this professor
        professor_rank: Professor's preference rank for this student
    """

    student_id: str
    professor_id: str
    student_field: str
    professor_field: str
    field_match: bool
    student_rank: int
    professor_rank: int

    def __repr__(self) -> str:
        match_str = "MATCH" if self.field_match else "MISMATCH"
        return (
            f"Assignment({self.student_id}->{self.professor_id}, "
            f"{match_str}, s_rank={self.student_rank}, p_rank={self.professor_rank})"
        )
