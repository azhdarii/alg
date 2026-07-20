"""Population initialization module."""

import random
from typing import List
from ..models.student import Student
from ..models.professor import Professor
from ..models.chromosome import Chromosome
from ..models.population import Population


class PopulationInitializer:
    """
    Initializes a population of chromosomes.

    This class generates valid initial solutions for the genetic algorithm.
    The initialization is independent of the specific algorithm
    (works for both Weighted Sum and NSGA-II).

    Initialization strategy:
    1. Create random assignments
    2. Ensure basic validity (all students assigned)
    3. Optionally bias towards field-matching solutions

    Follows Single Responsibility Principle: only handles population creation.
    """

    def __init__(
        self,
        students: List[Student],
        professors: List[Professor],
        seed: int = 42,
    ):
        """
        Initialize the population initializer.

        Args:
            students: List of Student objects
            professors: List of Professor objects
            seed: Random seed for reproducibility
        """
        self.students = students
        self.professors = professors
        self.professor_ids = [p.professor_id for p in professors]
        self.student_ids = [s.student_id for s in students]

        # Build field-based professor groups for biased initialization
        self._field_professors = {}
        for prof in professors:
            if prof.field not in self._field_professors:
                self._field_professors[prof.field] = []
            self._field_professors[prof.field].append(prof.professor_id)

        random.seed(seed)

    def initialize(
        self,
        population_size: int,
        bias_field_match: bool = True,
        field_match_ratio: float = 0.7,
    ) -> Population:
        """
        Create an initial population.

        Args:
            population_size: Number of chromosomes to create
            bias_field_match: If True, bias initialization towards field matching
            field_match_ratio: Ratio of field-matched assignments (if biasing)

        Returns:
            Population with initialized chromosomes
        """
        population = Population()

        for _ in range(population_size):
            chromosome = self._create_chromosome(bias_field_match, field_match_ratio)
            population.add(chromosome)

        return population

    def _create_chromosome(
        self, bias_field_match: bool, field_match_ratio: float
    ) -> Chromosome:
        """
        Create a single valid chromosome.

        Args:
            bias_field_match: Whether to bias towards field matching
            field_match_ratio: Ratio of field-matched assignments

        Returns:
            A new Chromosome
        """
        genes: List[str] = []

        for student in self.students:
            if bias_field_match and random.random() < field_match_ratio:
                # Try to assign from same field
                same_field = self._field_professors.get(student.field, [])
                if same_field:
                    prof_id = random.choice(same_field)
                    genes.append(prof_id)
                else:
                    # Fallback to random
                    genes.append(random.choice(self.professor_ids))
            else:
                # Random assignment
                genes.append(random.choice(self.professor_ids))

        return Chromosome(
            genes=genes,
            student_ids=self.student_ids.copy(),
        )

    def create_random(self) -> Chromosome:
        """
        Create a single random chromosome.

        Returns:
            A new Chromosome with random assignments
        """
        genes = [random.choice(self.professor_ids) for _ in self.students]
        return Chromosome(
            genes=genes,
            student_ids=self.student_ids.copy(),
        )

    def create_field_biased(self, bias_ratio: float = 0.8) -> Chromosome:
        """
        Create a chromosome biased towards field matching.

        Args:
            bias_ratio: Probability of field-matched assignment

        Returns:
            A new Chromosome with biased assignments
        """
        return self._create_chromosome(bias_field_match=True, field_match_ratio=bias_ratio)

    def create_from_preference(
        self, use_student_pref: bool = True, pref_ratio: float = 0.5
    ) -> Chromosome:
        """
        Create a chromosome based on preference lists.

        Args:
            use_student_pref: If True, use student preferences; else professor
            pref_ratio: Probability of using preference-based assignment

        Returns:
            A new Chromosome with preference-biased assignments
        """
        genes: List[str] = []

        for i, student in enumerate(self.students):
            if random.random() < pref_ratio:
                if use_student_pref and student.preference_list:
                    # Use student's preference
                    prof_id = random.choice(student.preference_list)
                    genes.append(prof_id)
                elif not use_student_pref:
                    # Find professors who prefer this student
                    preferring = [
                        p.professor_id
                        for p in self.professors
                        if student.student_id in p.preference_list
                    ]
                    if preferring:
                        prof_id = random.choice(preferring)
                        genes.append(prof_id)
                    else:
                        genes.append(random.choice(self.professor_ids))
                else:
                    genes.append(random.choice(self.professor_ids))
            else:
                genes.append(random.choice(self.professor_ids))

        return Chromosome(
            genes=genes,
            student_ids=self.student_ids.copy(),
        )

    def __repr__(self) -> str:
        return (
            f"PopulationInitializer(students={len(self.students)}, "
            f"professors={len(self.professors)})"
        )
