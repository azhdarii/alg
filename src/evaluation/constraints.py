"""Constraint evaluation for the assignment problem."""

from typing import List, Dict
from ..models.student import Student
from ..models.professor import Professor
from ..models.chromosome import Chromosome, ConstraintValues
from ..config.configuration import PenaltyConfig


class ConstraintEvaluator:
    """
    Evaluates constraint violations for a chromosome.

    This class computes:
    1. Professor Capacity violations
    2. Field Matching violations

    Each constraint is evaluated separately and returns its own penalty.
    Penalties are not combined with objectives (that belongs to algorithm layer).

    Follows Single Responsibility Principle: only handles constraint computation.
    """

    def __init__(
        self,
        students: List[Student],
        professors: List[Professor],
        penalty_config: PenaltyConfig,
    ):
        """
        Initialize the constraint evaluator.

        Args:
            students: List of Student objects
            professors: List of Professor objects
            penalty_config: Penalty coefficients for violations
        """
        self.students = students
        self.professors = professors
        self.penalty_config = penalty_config
        self._student_map = {s.student_id: s for s in students}
        self._professor_map = {p.professor_id: p for p in professors}

    def evaluate(self, chromosome: Chromosome) -> ConstraintValues:
        """
        Evaluate all constraints for a chromosome.

        Args:
            chromosome: The solution to evaluate

        Returns:
            ConstraintValues with all constraint violations
        """
        capacity_violation = self._compute_capacity_violation(chromosome)
        field_mismatch = self._compute_field_mismatch_count(chromosome)

        total_penalty = (
            capacity_violation * self.penalty_config.capacity_penalty_per_student
            + field_mismatch * self.penalty_config.field_mismatch_penalty
        )

        return ConstraintValues(
            capacity_violation=capacity_violation,
            field_mismatch_count=field_mismatch,
            total_penalty=total_penalty,
        )

    def _compute_capacity_violation(self, chromosome: Chromosome) -> float:
        """
        Compute total capacity violation across all professors.

        For each professor, if assigned students exceed capacity or
        fall below min_capacity, the violation is counted.

        Args:
            chromosome: The solution to evaluate

        Returns:
            Total capacity violation (sum of over/under capacity)
        """
        # Count assignments per professor
        prof_counts = chromosome.count_professor_assignments()

        total_violation = 0.0
        for prof in self.professors:
            count = prof_counts.get(prof.professor_id, 0)

            # Over capacity violation
            if count > prof.capacity:
                total_violation += count - prof.capacity

            # Under min capacity violation
            if count < prof.min_capacity:
                total_violation += prof.min_capacity - count

        return total_violation

    def _compute_field_mismatch_count(self, chromosome: Chromosome) -> int:
        """
        Count number of field mismatches.

        A mismatch occurs when a student is assigned to a professor
        from a different research field.

        Args:
            chromosome: The solution to evaluate

        Returns:
            Number of field mismatches
        """
        mismatch_count = 0
        for i, prof_id in enumerate(chromosome.genes):
            student = self._student_map[chromosome.student_ids[i]]
            professor = self._professor_map[prof_id]

            if student.field != professor.field:
                mismatch_count += 1

        return mismatch_count

    def compute_single_capacity_impact(
        self, professor_id: str, current_count: int, delta: int
    ) -> float:
        """
        Compute the change in capacity violation if we add/remove a student.

        Useful for repair operators and efficient local search.

        Args:
            professor_id: The affected professor
            current_count: Current number of assigned students
            delta: Change in count (+1 for add, -1 for remove)

        Returns:
            Change in violation (positive = worse, negative = better)
        """
        professor = self._professor_map[professor_id]
        new_count = current_count + delta

        # Current violation
        current_violation = 0.0
        if current_count > professor.capacity:
            current_violation = current_count - professor.capacity
        elif current_count < professor.min_capacity:
            current_violation = professor.min_capacity - current_count

        # New violation
        new_violation = 0.0
        if new_count > professor.capacity:
            new_violation = new_count - professor.capacity
        elif new_count < professor.min_capacity:
            new_violation = professor.min_capacity - new_count

        return new_violation - current_violation

    def is_feasible(self, chromosome: Chromosome) -> bool:
        """
        Check if a chromosome satisfies all constraints.

        Args:
            chromosome: The solution to check

        Returns:
            True if feasible, False otherwise
        """
        constraints = self.evaluate(chromosome)
        return constraints.total_penalty == 0.0

    def get_professor_load(self, chromosome: Chromosome) -> Dict[str, int]:
        """
        Get the number of students assigned to each professor.

        Args:
            chromosome: The solution to analyze

        Returns:
            Dictionary mapping professor_id -> assigned count
        """
        return chromosome.count_professor_assignments()

    def get_violating_professors(self, chromosome: Chromosome) -> List[str]:
        """
        Get list of professors with capacity violations.

        Args:
            chromosome: The solution to analyze

        Returns:
            List of professor IDs with violations
        """
        prof_counts = chromosome.count_professor_assignments()
        violating = []

        for prof in self.professors:
            count = prof_counts.get(prof.professor_id, 0)
            if count > prof.capacity or count < prof.min_capacity:
                violating.append(prof.professor_id)

        return violating

    def __repr__(self) -> str:
        return (
            f"ConstraintEvaluator(students={len(self.students)}, "
            f"professors={len(self.professors)}, "
            f"penalties={self.penalty_config})"
        )
