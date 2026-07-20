"""Objective function evaluation."""

from typing import List, Dict
from ..models.student import Student
from ..models.professor import Professor
from ..models.chromosome import Chromosome, ObjectiveValues


class ObjectiveEvaluator:
    """
    Evaluates objective functions for a chromosome.

    This class computes:
    1. Student Satisfaction
    2. Professor Satisfaction
    3. Fairness

    Each objective is computed separately and returned independently.
    No aggregation is performed (that belongs to the algorithm layer).

    Follows Single Responsibility Principle: only handles objective computation.
    """

    def __init__(
        self,
        students: List[Student],
        professors: List[Professor],
    ):
        """
        Initialize the objective evaluator.

        Args:
            students: List of Student objects
            professors: List of Professor objects
        """
        self.students = students
        self.professors = professors
        self._student_map = {s.student_id: s for s in students}
        self._professor_map = {p.professor_id: p for p in professors}
        self._student_indices = {s.student_id: i for i, s in enumerate(students)}
        self._professor_indices = {p.professor_id: i for i, p in enumerate(professors)}

        # Pre-compute maximum possible satisfaction for normalization
        self._max_student_satisfaction = self._compute_max_student_satisfaction()
        self._max_professor_satisfaction = self._compute_max_professor_satisfaction()

    def evaluate(self, chromosome: Chromosome) -> ObjectiveValues:
        """
        Evaluate all objectives for a chromosome.

        Args:
            chromosome: The solution to evaluate

        Returns:
            ObjectiveValues with all three objectives computed
        """
        student_sat = self._compute_student_satisfaction(chromosome)
        prof_sat = self._compute_professor_satisfaction(chromosome)
        fairness = self._compute_fairness(chromosome)

        return ObjectiveValues(
            student_satisfaction=student_sat,
            professor_satisfaction=prof_sat,
            fairness=fairness,
        )

    def _compute_student_satisfaction(self, chromosome: Chromosome) -> float:
        """
        Compute student satisfaction score.

        For each student, satisfaction is based on the rank of their
        assigned professor in their preference list.

        Formula: sum(1/rank) for all students, normalized to [0, 1]

        Args:
            chromosome: The solution to evaluate

        Returns:
            Normalized satisfaction score (0-1, higher is better)
        """
        if self._max_student_satisfaction == 0:
            return 0.0

        total = 0.0
        for i, student_id in enumerate(chromosome.student_ids):
            student = self._student_map[student_id]
            prof_id = chromosome.genes[i]
            rank = student.get_preference_rank(prof_id)

            if rank > 0:
                total += 1.0 / rank
            # If rank is 0 (not in list), contribute 0

        return total / self._max_student_satisfaction

    def _compute_professor_satisfaction(self, chromosome: Chromosome) -> float:
        """
        Compute professor satisfaction score.

        For each professor, satisfaction is based on the rank of each
        assigned student in their preference list.

        Formula: sum(1/rank) for all assignments, normalized to [0, 1]

        Args:
            chromosome: The solution to evaluate

        Returns:
            Normalized satisfaction score (0-1, higher is better)
        """
        if self._max_professor_satisfaction == 0:
            return 0.0

        total = 0.0
        # Group assignments by professor
        prof_assignments: Dict[str, List[str]] = {}
        for i, prof_id in enumerate(chromosome.genes):
            if prof_id not in prof_assignments:
                prof_assignments[prof_id] = []
            prof_assignments[prof_id].append(chromosome.student_ids[i])

        # Compute satisfaction for each professor
        for prof_id, assigned_students in prof_assignments.items():
            professor = self._professor_map[prof_id]
            for student_id in assigned_students:
                rank = professor.get_preference_rank(student_id)
                if rank > 0:
                    total += 1.0 / rank

        return total / self._max_professor_satisfaction

    def _compute_fairness(self, chromosome: Chromosome) -> float:
        """
        Compute fairness of quality distribution.

        Fairness is measured as the variance of average quality scores
        across professors. Lower variance means more fair distribution.

        Returns a normalized value where 0 = perfectly fair, 1 = most unfair.

        Args:
            chromosome: The solution to evaluate

        Returns:
            Normalized fairness value (0-1, lower is better)
        """
        # Group students by assigned professor
        prof_qualities: Dict[str, List[float]] = {}
        for i, prof_id in enumerate(chromosome.genes):
            if prof_id not in prof_qualities:
                prof_qualities[prof_id] = []
            student = self._student_map[chromosome.student_ids[i]]
            prof_qualities[prof_id].append(student.quality_score)

        # Compute average quality for each professor
        avg_qualities = []
        for prof_id, qualities in prof_qualities.items():
            if qualities:  # Only consider professors with students
                avg_qualities.append(sum(qualities) / len(qualities))

        if len(avg_qualities) <= 1:
            return 0.0  # Perfectly fair if only one professor has students

        # Compute variance
        overall_mean = sum(avg_qualities) / len(avg_qualities)
        variance = sum((q - overall_mean) ** 2 for q in avg_qualities) / len(
            avg_qualities
        )

        # Normalize variance to [0, 1] range
        # Max variance occurs when half have min quality, half have max
        # For our range (50-100), max variance is approximately (25)^2 = 625
        max_possible_variance = 625.0
        normalized = min(variance / max_possible_variance, 1.0)

        return normalized

    def _compute_max_student_satisfaction(self) -> float:
        """
        Compute theoretical maximum student satisfaction.

        This occurs when every student gets their first choice.

        Returns:
            Maximum possible student satisfaction score
        """
        total = 0.0
        for student in self.students:
            if student.preference_list:
                total += 1.0  # 1/1 for first choice
        return total
 

    def _compute_max_professor_satisfaction(self) -> float:
        """
        Compute theoretical maximum professor satisfaction.
        This occurs when every student is ranked #1 by their assigned professor.
        
        Since each student can only be assigned once, the max is limited
        by the number of students, not the sum of all professor capacities.
        
        Returns:
            Maximum possible professor satisfaction score
        """
        # The maximum is when ALL students are rank 1 for their professors
        # Limited by number of students, not total capacity
        return float(len(self.students))

    def compute_student_satisfaction_single(
        self, student_id: str, professor_id: str
    ) -> float:
        """
        Compute satisfaction for a single assignment.

        Args:
            student_id: The student
            professor_id: The assigned professor

        Returns:
            Satisfaction value (1/rank)
        """
        student = self._student_map[student_id]
        rank = student.get_preference_rank(professor_id)
        return 1.0 / rank if rank > 0 else 0.0

    def compute_professor_satisfaction_single(
        self, student_id: str, professor_id: str
    ) -> float:
        """
        Compute satisfaction for a single assignment (professor perspective).

        Args:
            student_id: The assigned student
            professor_id: The professor

        Returns:
            Satisfaction value (1/rank)
        """
        professor = self._professor_map[professor_id]
        rank = professor.get_preference_rank(student_id)
        return 1.0 / rank if rank > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"ObjectiveEvaluator(students={len(self.students)}, "
            f"professors={len(self.professors)})"
        )
