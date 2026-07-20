"""Hard constraint handling for Weighted Sum GA."""

from typing import List
from ..models.chromosome import Chromosome
from ..models.student import Student
from ..models.professor import Professor


class HardConstraintHandler:
    """
    Handles hard constraints by modifying fitness to strongly prefer
    feasible solutions over infeasible ones.

    This implements the Constraint-Domination Principle:
    1. Feasible solutions always beat infeasible solutions
    2. Between two infeasible solutions, the one with less violation wins
    3. Between two feasible solutions, compare normally

    This is different from soft constraints which just penalize violations.
    Hard constraints make infeasible solutions virtually impossible to survive.
    """

    def __init__(
        self,
        students: List[Student],
        professors: List[Professor],
        capacity_hard: bool = False,
        field_hard: bool = False,
        hard_penalty: float = 1e6,
    ):
        """
        Initialize hard constraint handler.

        Args:
            students: List of students
            professors: List of professors
            capacity_hard: Whether capacity is a hard constraint
            field_hard: Whether field matching is a hard constraint
            hard_penalty: Penalty for hard constraint violations
        """
        self.students = students
        self.professors = professors
        self.capacity_hard = capacity_hard
        self.field_hard = field_hard
        self.hard_penalty = hard_penalty
        self._student_map = {s.student_id: s for s in students}
        self._professor_map = {p.professor_id: p for p in professors}

    def compute_hard_penalty(self, chromosome: Chromosome) -> float:
        """
        Compute additional penalty for hard constraints.

        This penalty is MUCH larger than soft constraint penalties,
        making infeasible solutions virtually uncompetitive.

        Args:
            chromosome: The chromosome to evaluate

        Returns:
            Additional penalty for hard constraint violations
        """
        penalty = 0.0

        if self.capacity_hard:
            capacity_violations = self._count_capacity_violations(chromosome)
            penalty += capacity_violations * self.hard_penalty

        if self.field_hard:
            field_mismatches = self._count_field_mismatches(chromosome)
            penalty += field_mismatches * self.hard_penalty

        return penalty

    def _count_capacity_violations(self, chromosome: Chromosome) -> int:
        """Count total capacity violations."""
        prof_counts = chromosome.count_professor_assignments()
        violations = 0

        for prof in self.professors:
            count = prof_counts.get(prof.professor_id, 0)
            if count > prof.capacity:
                violations += count - prof.capacity
            if count < prof.min_capacity:
                violations += prof.min_capacity - count

        return violations

    def _count_field_mismatches(self, chromosome: Chromosome) -> int:
        """Count field mismatches."""
        mismatches = 0
        for i, prof_id in enumerate(chromosome.genes):
            student = self._student_map[chromosome.student_ids[i]]
            professor = self._professor_map[prof_id]
            if student.field != professor.field:
                mismatches += 1
        return mismatches

    def is_feasible(self, chromosome: Chromosome) -> bool:
        """
        Check if chromosome satisfies all hard constraints.

        Args:
            chromosome: The chromosome to check

        Returns:
            True if feasible, False otherwise
        """
        if self.capacity_hard:
            if self._count_capacity_violations(chromosome) > 0:
                return False

        if self.field_hard:
            if self._count_field_mismatches(chromosome) > 0:
                return False

        return True

    def constraint_dominance(self, chrom_a: Chromosome, chrom_b: Chromosome) -> int:
        """
        Compare two chromosomes using constraint-domination principle.

        Returns:
            1 if chrom_a dominates chrom_b
            -1 if chrom_b dominates chrom_a
            0 if neither dominates
        """
        feasible_a = self.is_feasible(chrom_a)
        feasible_b = self.is_feasible(chrom_b)

        # Feasible always beats infeasible
        if feasible_a and not feasible_b:
            return 1
        if not feasible_a and feasible_b:
            return -1

        # Both feasible or both infeasible
        if feasible_a and feasible_b:
            # Both feasible - no constraint domination (use objectives)
            return 0

        # Both infeasible - less violation wins
        penalty_a = self.compute_hard_penalty(chrom_a)
        penalty_b = self.compute_hard_penalty(chrom_b)

        if penalty_a < penalty_b:
            return 1
        elif penalty_a > penalty_b:
            return -1
        else:
            return 0

    def adjust_fitness(self, chromosome: Chromosome, base_fitness: float) -> float:
        """
        Adjust fitness based on hard constraints.

        For feasible solutions: return base_fitness
        For infeasible solutions: return very negative value

        Args:
            chromosome: The chromosome
            base_fitness: Original fitness value

        Returns:
            Adjusted fitness
        """
        if self.is_feasible(chromosome):
            return base_fitness
        else:
            # Return very negative fitness for infeasible solutions
            penalty = self.compute_hard_penalty(chromosome)
            return base_fitness - penalty

    def __repr__(self) -> str:
        return (
            f"HardConstraintHandler(\n"
            f"  capacity_hard={self.capacity_hard},\n"
            f"  field_hard={self.field_hard},\n"
            f"  hard_penalty={self.hard_penalty}\n"
            f")"
        )
