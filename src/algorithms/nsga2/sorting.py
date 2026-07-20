"""Fast Non-Dominated Sorting for NSGA-II."""

from typing import List, Dict, Set
from ...models.chromosome import Chromosome


class FastNonDominatedSorting:
    """
    Fast Non-Dominated Sorting algorithm.

    Assigns Pareto ranks to chromosomes by identifying non-dominated fronts.
    This is the core component of NSGA-II for multi-objective optimization.

    Algorithm (Deb et al., 2002):
    1. For each chromosome, count how many chromosomes dominate it (n_p)
    2. For each chromosome, find the set of chromosomes it dominates (S_p)
    3. Front 1 = all chromosomes with n_p = 0
    4. For each chromosome in Front 1, decrement n_p of all chromosomes in S_p
    5. Any chromosome with n_p = 0 becomes Front 2
    6. Repeat until all chromosomes are assigned

    Complexity: O(M * N^2) where M = number of objectives, N = population size

    Design Note:
        This class is independent of Weighted Sum and can be reused
        by any multi-objective algorithm that needs Pareto ranking.

    Follows Single Responsibility Principle: only handles sorting.
    """

    def __init__(self):
        """Initialize the non-dominated sorting algorithm."""
        pass

    def sort(self, chromosomes: List[Chromosome]) -> List[List[Chromosome]]:
        """
        Perform fast non-dominated sorting.

        Args:
            chromosomes: List of chromosomes to sort

        Returns:
            List of fronts, where each front is a list of chromosomes.
            Front 0 contains non-dominated solutions (best Pareto front).
        """
        if not chromosomes:
            return []

        n = len(chromosomes)

        # n_p[i] = number of chromosomes that dominate chromosomes[i]
        n_p: List[int] = [0] * n

        # S_p[i] = set of chromosomes that chromosomes[i] dominates
        s_p: List[Set[int]] = [set() for _ in range(n)]

        # Pre-compute objective vectors for efficiency
        obj_vectors = []
        for chrom in chromosomes:
            if chrom.objectives is not None:
                obj_vectors.append(chrom.objectives.to_list())
            else:
                # Default: worst possible values
                obj_vectors.append([0.0, 0.0, 1.0])

        # Compare all pairs
        for i in range(n):
            for j in range(i + 1, n):
                if self._dominates(obj_vectors[i], obj_vectors[j]):
                    s_p[i].add(j)
                    n_p[j] += 1
                elif self._dominates(obj_vectors[j], obj_vectors[i]):
                    s_p[j].add(i)
                    n_p[i] += 1

        # Initialize fronts
        fronts: List[List[int]] = [[]]

        # Front 0: all chromosomes with n_p = 0
        for i in range(n):
            if n_p[i] == 0:
                fronts[0].append(i)

        # Build remaining fronts
        current_front = 0
        while fronts[current_front]:
            next_front: List[int] = []

            for i in fronts[current_front]:
                for j in s_p[i]:
                    n_p[j] -= 1
                    if n_p[j] == 0:
                        next_front.append(j)

            current_front += 1
            if next_front:
                fronts.append(next_front)
            else:
                break

        # Convert indices to chromosomes
        result = [[chromosomes[i] for i in front] for front in fronts]

        # Assign rank to each chromosome
        for rank, front in enumerate(result):
            for chrom in front:
                chrom.metadata["rank"] = rank

        return result

    def _dominates(self, obj_a: List[float], obj_b: List[float]) -> bool:
        """
        Check if solution A dominates solution B.

        Dominance rule (for minimization of fairness, maximization of others):
        - A is no worse than B in all objectives
        - A is strictly better than B in at least one objective

        Note: student_satisfaction and professor_satisfaction are MAXIMIZED
              fairness is MINIMIZED

        Args:
            obj_a: Objective values for solution A [student, professor, fairness]
            obj_b: Objective values for solution B [student, professor, fairness]

        Returns:
            True if A dominates B
        """
        # For student_satisfaction and professor_satisfaction: higher is better
        # For fairness: lower is better

        a_student, a_professor, a_fairness = obj_a
        b_student, b_professor, b_fairness = obj_b

        # Check if A is no worse than B in all objectives
        # Student: A >= B (higher is better)
        # Professor: A >= B (higher is better)
        # Fairness: A <= B (lower is better)
        no_worse_student = a_student >= b_student
        no_worse_professor = a_professor >= b_professor
        no_worse_fairness = a_fairness <= b_fairness

        if not (no_worse_student and no_worse_professor and no_worse_fairness):
            return False

        # Check if A is strictly better in at least one objective
        strictly_better_student = a_student > b_student
        strictly_better_professor = a_professor > b_professor
        strictly_better_fairness = a_fairness < b_fairness

        return strictly_better_student or strictly_better_professor or strictly_better_fairness

    def __repr__(self) -> str:
        return "FastNonDominatedSorting()"
