"""Repair operator for correcting infeasible solutions."""

import random
from typing import List, Dict, Tuple
from ..models.student import Student
from ..models.professor import Professor
from ..models.chromosome import Chromosome
from ..evaluation.constraints import ConstraintEvaluator


class RepairOperator:
    """
    Repair operator for correcting infeasible solutions.

    After crossover or mutation, some solutions may violate constraints
    (e.g., professor capacity exceeded). This operator attempts to
    repair such solutions while preserving as much of the good
    characteristics as possible.

    Repair strategy:
    1. Identify violating assignments
    2. Try to reassign students to feasible professors
    3. Prioritize keeping field-matched assignments
    4. Maintain preference satisfaction where possible

    Follows Single Responsibility Principle: only handles repair.
    """

    def __init__(
        self,
        students: List[Student],
        professors: List[Professor],
        constraint_evaluator: ConstraintEvaluator,
        max_attempts: int = 100,
    ):
        """
        Initialize the repair operator.

        Args:
            students: List of Student objects
            professors: List of Professor objects
            constraint_evaluator: Evaluator for checking constraints
            max_attempts: Maximum repair attempts per chromosome
        """
        self.students = students
        self.professors = professors
        self.constraint_evaluator = constraint_evaluator
        self.max_attempts = max_attempts

        self._student_map = {s.student_id: s for s in students}
        self._professor_map = {p.professor_id: p for p in professors}
        self._student_indices = {s.student_id: i for i, s in enumerate(students)}

        # Build field-based professor groups
        self._field_professors: Dict[str, List[str]] = {}
        for prof in professors:
            if prof.field not in self._field_professors:
                self._field_professors[prof.field] = []
            self._field_professors[prof.field].append(prof.professor_id)

    def repair(self, chromosome: Chromosome) -> Chromosome:
        """
        Attempt to repair an infeasible chromosome.

        Args:
            chromosome: The chromosome to repair

        Returns:
            Repaired chromosome (may still be infeasible if repair failed)
        """
        repaired = chromosome.deep_copy()

        for _ in range(self.max_attempts):
            constraints = self.constraint_evaluator.evaluate(repaired)

            if constraints.total_penalty == 0:
                # Already feasible
                return repaired

            # Try to fix capacity violations
            if constraints.capacity_violation > 0:
                repaired = self._repair_capacity(repaired)

            # Try to fix field mismatches (optional, lower priority)
            # Field mismatches are soft constraints, so we don't force repair

        return repaired

    def _repair_capacity(self, chromosome: Chromosome) -> Chromosome:
        """
        Repair capacity violations.

        Strategy:
        1. Find professors with over-capacity
        2. Find students assigned to them
        3. Reassign excess students to under-capacity professors

        Args:
            chromosome: The chromosome to repair

        Returns:
            Repaired chromosome
        """
        prof_counts = chromosome.count_professor_assignments()

        # Find over-capacity professors and their students
        over_capacity: List[Tuple[str, int]] = []
        for prof in self.professors:
            count = prof_counts.get(prof.professor_id, 0)
            if count > prof.capacity:
                over_capacity.append((prof.professor_id, count - prof.capacity))

        # Find under-capacity professors
        under_capacity: List[str] = []
        for prof in self.professors:
            count = prof_counts.get(prof.professor_id, 0)
            if count < prof.min_capacity:
                under_capacity.append(prof.professor_id)

        if not over_capacity or not under_capacity:
            return chromosome

        # Try to reassign excess students
        for prof_id, excess in over_capacity:
            # Get students assigned to this professor
            assigned_students = [
                chromosome.student_ids[i]
                for i in range(chromosome.length)
                if chromosome.genes[i] == prof_id
            ]

            # Sort by preference (reassign students who prefer this prof less)
            assigned_students.sort(
                key=lambda s: self._student_map[s].get_preference_rank(prof_id),
                reverse=True,
            )

            # Reassign excess students
            for student_id in assigned_students[:excess]:
                if not under_capacity:
                    break

                # Find best target professor
                target_prof = self._find_best_target(
                    student_id, under_capacity, chromosome
                )
                if target_prof:
                    # Perform reassignment
                    idx = self._student_indices[student_id]
                    chromosome.genes[idx] = target_prof

                    # Update under-capacity list
                    prof_counts[target_prof] = prof_counts.get(target_prof, 0) + 1
                    if prof_counts[target_prof] >= self._professor_map[target_prof].min_capacity:
                        under_capacity.remove(target_prof)

        return chromosome

    def _find_best_target(
        self,
        student_id: str,
        candidates: List[str],
        chromosome: Chromosome,
    ) -> str:
        """
        Find the best target professor for reassignment.

        Prioritizes:
        1. Field match
        2. Student preference
        3. Professor preference

        Args:
            student_id: Student to reassign
            candidates: List of candidate professor IDs
            chromosome: Current chromosome state

        Returns:
            Best professor ID, or None if no good target found
        """
        student = self._student_map[student_id]
        best_target = None
        best_score = -1

        for prof_id in candidates:
            professor = self._professor_map[prof_id]
            score = 0.0

            # Field match bonus
            if student.field == professor.field:
                score += 10.0

            # Student preference bonus
            student_rank = student.get_preference_rank(prof_id)
            if student_rank > 0:
                score += 1.0 / student_rank

            # Professor preference bonus
            prof_rank = professor.get_preference_rank(student_id)
            if prof_rank > 0:
                score += 0.5 / prof_rank

            if score > best_score:
                best_score = score
                best_target = prof_id

        return best_target

    def repair_field_mismatch(self, chromosome: Chromosome) -> Chromosome:
        """
        Attempt to reduce field mismatches (optional repair).

        This is a softer repair that tries to improve field matching
        without violating capacity constraints.

        Args:
            chromosome: The chromosome to repair

        Returns:
            Repaired chromosome
        """
        repaired = chromosome.deep_copy()

        for i in range(repaired.length):
            student = self._student_map[repaired.student_ids[i]]
            current_prof = repaired.genes[i]

            # Skip if already matched
            if student.field == self._professor_map[current_prof].field:
                continue

            # Find field-matched professors with capacity
            same_field = self._field_professors.get(student.field, [])
            for prof_id in same_field:
                prof = self._professor_map[prof_id]
                prof_count = repaired.count_professor_assignments().get(prof_id, 0)

                if prof_count < prof.capacity:
                    # Can reassign here
                    repaired.genes[i] = prof_id
                    break

        return repaired

    def __repr__(self) -> str:
        return (
            f"RepairOperator(students={len(self.students)}, "
            f"professors={len(self.professors)}, "
            f"max_attempts={self.max_attempts})"
        )
