"""NSGA-II (Non-dominated Sorting Genetic Algorithm II) implementation."""

import random
from typing import List, Optional, Tuple, Dict, Any
from ...config.configuration import Configuration
from ...data import DataLoader
from ...models.student import Student
from ...models.professor import Professor
from ...models.chromosome import Chromosome
from ...models.population import Population
from ...evaluation import ObjectiveEvaluator, ConstraintEvaluator
from ...operators.mutation import MutationOperator, RandomResetMutation, SwapMutation
from ...operators.crossover import CrossoverOperator, UniformCrossover
from ...initialization import PopulationInitializer
from ...repair import RepairOperator
from ...logging_config import OptimizationLogger
from .config import NSGA2Config
from .sorting import FastNonDominatedSorting
from .crowding import CrowdingDistance
from .selection import NSGA2BinaryTournamentSelection


class NSGA2:
    """
    NSGA-II (Non-dominated Sorting Genetic Algorithm II) for
    Student-Supervisor Assignment.

    This is a true multi-objective genetic algorithm that maintains
    a Pareto front of non-dominated solutions. Unlike Weighted Sum,
    it does NOT collapse objectives into a single fitness value.

    Key Differences from Weighted Sum:
    1. No scalar fitness - uses Pareto rank + crowding distance
    2. Returns a set of non-dominated solutions (Pareto front)
    3. Preserves diversity through crowding distance
    4. Uses constraint-domination principle for constraints

    Algorithm Flow (Deb et al., 2002):
    1. Initialize population P of size N
    2. Evaluate all chromosomes
    3. Repeat until max generations:
        a. Create offspring Q of size N using selection, crossover, mutation
        b. Evaluate offspring
        c. Merge R = P + Q (size 2N)
        d. Apply Fast Non-Dominated Sorting to R
        e. Compute Crowding Distance for each front
        f. Fill next generation P' from best fronts
        g. If last front exceeds remaining slots, select by crowding distance
    4. Return final Pareto front

    Design:
        This class is INDEPENDENT from WeightedSumGA.
        It does NOT inherit from WeightedSumGA.
        It reuses shared infrastructure (models, evaluators, operators)
        but has its own algorithm-specific logic.

    Follows Open/Closed Principle: open for extension (future algorithms),
    closed for modification (shared infrastructure unchanged).
    """

    def __init__(
        self,
        config: Configuration,
        nsga2_config: Optional[NSGA2Config] = None,
    ):
        """
        Initialize NSGA-II.

        Args:
            config: Main configuration
            nsga2_config: NSGA-II specific configuration
        """
        self.config = config
        self.nsga2_config = nsga2_config or NSGA2Config()

        # Set random seed
        if config.algorithm.random_seed is not None:
            random.seed(config.algorithm.random_seed)

        # Data containers (loaded later)
        self.students: List[Student] = []
        self.professors: List[Professor] = []
        self.professor_ids: List[str] = []

        # Evaluators (initialized later)
        self.objective_evaluator: Optional[ObjectiveEvaluator] = None
        self.constraint_evaluator: Optional[ConstraintEvaluator] = None

        # NSGA-II specific components (initialized later)
        self.sorting: Optional[FastNonDominatedSorting] = None
        self.crowding: Optional[CrowdingDistance] = None
        self.selection: Optional[NSGA2BinaryTournamentSelection] = None

        # Shared components (initialized later)
        self.initializer: Optional[PopulationInitializer] = None
        self.repair: Optional[RepairOperator] = None
        self.mutation_operators: List[MutationOperator] = []
        self.crossover_operators: List[CrossoverOperator] = []

        # Logger
        self.logger: Optional[OptimizationLogger] = None

        # Final Pareto front
        self.pareto_front: List[Chromosome] = []

    def load_data(self) -> None:
        """Load data from Excel files."""
        print("[1/6] Loading data...")
        loader = DataLoader(self.config.data)
        self.students, self.professors = loader.load_all()
        self.professor_ids = [p.professor_id for p in self.professors]
        print(f"      Loaded {len(self.students)} students, {len(self.professors)} professors")

    def initialize_components(self) -> None:
        """Initialize all algorithm components."""
        print("[2/6] Initializing components...")

        # Evaluators
        self.objective_evaluator = ObjectiveEvaluator(self.students, self.professors)
        self.constraint_evaluator = ConstraintEvaluator(
            self.students, self.professors, self.config.penalty
        )

        # NSGA-II specific components
        self.sorting = FastNonDominatedSorting()
        self.crowding = CrowdingDistance()
        self.selection = NSGA2BinaryTournamentSelection(
            tournament_size=self.nsga2_config.tournament_size
        )

        # Population initializer
        self.initializer = PopulationInitializer(
            self.students,
            self.professors,
            seed=self.config.algorithm.random_seed or 42,
        )

        # Repair
        self.repair = RepairOperator(
            self.students, self.professors, self.constraint_evaluator
        )

        # Mutation operators
        self.mutation_operators = [
            RandomResetMutation(mutation_rate=self.config.algorithm.mutation_probability),
            SwapMutation(mutation_rate=self.config.algorithm.mutation_probability),
        ]

        # Crossover operators
        self.crossover_operators = [
            UniformCrossover(crossover_rate=self.config.algorithm.crossover_probability),
        ]

        # Logger
        self.logger = OptimizationLogger(self.config.logging)

        print(f"      Tournament size: {self.nsga2_config.tournament_size}")
        print(f"      Constraint dominance: {self.nsga2_config.use_constraint_dominance}")

    def initialize_population(self) -> Population:
        """Create and evaluate initial population."""
        print("[3/6] Creating initial population...")

        population = self.initializer.initialize(
            population_size=self.config.algorithm.population_size,
            bias_field_match=True,
            field_match_ratio=0.7,
        )

        # Evaluate all chromosomes
        for chromosome in population:
            self.evaluate_chromosome(chromosome)

        # Apply non-dominated sorting
        fronts = self.sorting.sort(population.chromosomes)
        self.crowding.compute(fronts)

        population.generation = 0
        print(f"      Population size: {population.size}")
        print(f"      Initial fronts: {len(fronts)}")

        return population

    def evaluate_chromosome(self, chromosome: Chromosome) -> None:
        """
        Evaluate a single chromosome.

        Unlike Weighted Sum, NSGA-II does NOT compute scalar fitness.
        Instead, it stores objectives and constraints for later use
        in non-dominated sorting and crowding distance.

        Args:
            chromosome: Chromosome to evaluate
        """
        # Compute objectives
        chromosome.objectives = self.objective_evaluator.evaluate(chromosome)

        # Compute constraints
        chromosome.constraints = self.constraint_evaluator.evaluate(chromosome)

        # NSGA-II does NOT compute fitness here
        # Fitness is determined by rank + crowding distance

    def evaluate_population(self, population: Population) -> None:
        """Evaluate all unevaluated chromosomes in population."""
        for chromosome in population:
            if not chromosome.is_evaluated():
                self.evaluate_chromosome(chromosome)

    def _select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        """
        Select two parents using NSGA-II binary tournament.

        Comparison rule:
        - Lower Pareto rank wins
        - If ranks equal, higher Crowding Distance wins

        Args:
            population: Current population

        Returns:
            Tuple of two parent chromosomes
        """
        return self.selection.select_pair(population)

    def _apply_crossover(
        self, parent1: Chromosome, parent2: Chromosome
    ) -> Tuple[Chromosome, Chromosome]:
        """
        Apply crossover to two parents.

        Args:
            parent1: First parent
            parent2: Second parent

        Returns:
            Tuple of two offspring
        """
        crossover = random.choice(self.crossover_operators)
        return crossover.crossover(parent1, parent2)

    def _apply_mutation(self, chromosome: Chromosome) -> Chromosome:
        """
        Apply mutation to a chromosome.

        Args:
            chromosome: Chromosome to mutate

        Returns:
            Mutated chromosome
        """
        mutation = random.choice(self.mutation_operators)
        return mutation.mutate(chromosome, self.professor_ids)

    def _repair_chromosome(self, chromosome: Chromosome) -> Chromosome:
        """
        Repair an infeasible chromosome.

        Args:
            chromosome: Chromosome to repair

        Returns:
            Repaired chromosome
        """
        return self.repair.repair(chromosome)

    def _generate_offspring(self, population: Population) -> List[Chromosome]:
        """
        Generate offspring population through selection, crossover, mutation.

        Args:
            population: Current population

        Returns:
            List of offspring chromosomes
        """
        offspring = []
        target_size = population.size

        while len(offspring) < target_size:
            # Selection
            parent1, parent2 = self._select_parents(population)

            # Crossover
            if random.random() < self.config.algorithm.crossover_probability:
                child1, child2 = self._apply_crossover(parent1, parent2)
            else:
                child1, child2 = parent1.deep_copy(), parent2.deep_copy()

            # Mutation
            child1 = self._apply_mutation(child1)
            child2 = self._apply_mutation(child2)

            # Repair
            child1 = self._repair_chromosome(child1)
            child2 = self._repair_chromosome(child2)

            # Add to offspring
            offspring.append(child1)
            if len(offspring) < target_size:
                offspring.append(child2)

        return offspring[:target_size]

    def _merge_populations(
        self, parent_pop: Population, offspring: List[Chromosome]
    ) -> List[Chromosome]:
        """
        Merge parent and offspring populations.

        This is the key NSGA-II step: combine P and Q to form R.

        Args:
            parent_pop: Current parent population
            offspring: Offspring population

        Returns:
            Merged list of chromosomes (size 2N)
        """
        merged = []
        for chrom in parent_pop:
            merged.append(chrom.deep_copy())
        for chrom in offspring:
            merged.append(chrom.deep_copy())
        return merged

    def _create_next_generation(
        self,
        merged: List[Chromosome],
        population_size: int,
    ) -> Population:
        """
        Create next generation from merged population using NSGA-II selection.

        Strategy:
        1. Apply Fast Non-Dominated Sorting
        2. Compute Crowding Distance
        3. Fill next generation front by front
        4. If last front exceeds remaining slots, select by crowding distance

        Args:
            merged: Merged parent + offspring (size 2N)
            population_size: Target population size (N)

        Returns:
            New Population of size N
        """
        # Apply non-dominated sorting
        fronts = self.sorting.sort(merged)

        # Compute crowding distance
        self.crowding.compute(fronts)

        # Fill next generation
        next_population = []
        front_idx = 0

        while front_idx < len(fronts) and len(next_population) < population_size:
            current_front = fronts[front_idx]

            if len(next_population) + len(current_front) <= population_size:
                # Entire front fits
                for chrom in current_front:
                    next_population.append(chrom.deep_copy())
            else:
                # Partial front - select by crowding distance
                remaining_slots = population_size - len(next_population)
                sorted_front = sorted(
                    current_front,
                    key=lambda c: c.metadata.get("crowding_distance", 0.0),
                    reverse=True,
                )
                for i in range(remaining_slots):
                    next_population.append(sorted_front[i].deep_copy())
                break

            front_idx += 1

        return Population(
            chromosomes=next_population,
            generation=0,  # Will be set by caller
        )

    def run(self) -> Population:
        """
        Execute NSGA-II.

        Returns:
            Final population with Pareto front
        """
        print("\n" + "=" * 60)
        print("NSGA-II (Non-dominated Sorting Genetic Algorithm II)")
        print("=" * 60)

        # Setup
        self.load_data()
        self.initialize_components()

        # Initialize population
        population = self.initialize_population()

        # Start logging
        self.logger.start()
        self.logger.log_generation(population, 0)

        # Print initial stats
        fronts = self.sorting.sort(population.chromosomes)
        print(f"\n[4/6] Starting evolution...")
        print(f"      Initial fronts: {len(fronts)}")
        print(f"      Front 0 size: {len(fronts[0]) if fronts else 0}")

        # Evolution loop
        for generation in range(1, self.config.algorithm.max_generations + 1):
            # Generate offspring
            offspring = self._generate_offspring(population)

            # Evaluate offspring
            for chromosome in offspring:
                self.evaluate_chromosome(chromosome)

            # Merge populations
            merged = self._merge_populations(population, offspring)

            # Create next generation using NSGA-II selection
            population = self._create_next_generation(
                merged, self.config.algorithm.population_size
            )
            population.generation = generation

            # Log progress
            self.logger.log_generation(population, generation)

            # Print progress every 10 generations
            if generation % 10 == 0:
                fronts = self.sorting.sort(population.chromosomes)
                print(
                    f"      Gen {generation:4d} | "
                    f"Fronts: {len(fronts)} | "
                    f"Front 0: {len(fronts[0]) if fronts else 0}"
                )

        # Finalize
        print(f"\n[5/6] Evolution complete!")
        self.logger.finish(population)

        # Extract final Pareto front
        self._extract_pareto_front(population)

        # Print results
        self._print_pareto_front()

        print(f"\n[6/6] Done!")
        return population

    def _extract_pareto_front(self, population: Population) -> None:
        """
        Extract the final Pareto front from the population.

        Args:
            population: Final population
        """
        fronts = self.sorting.sort(population.chromosomes)
        if fronts:
            self.pareto_front = fronts[0]
        else:
            self.pareto_front = []

    def _print_pareto_front(self) -> None:
        """Print the final Pareto front."""
        if not self.pareto_front:
            print("No Pareto front found!")
            return

        print("\n" + "=" * 60)
        print("FINAL PARETO FRONT")
        print("=" * 60)
        print(f"\nNumber of non-dominated solutions: {len(self.pareto_front)}")

        print("\n" + "-" * 60)
        print(f"{'ID':<6} {'Student':>10} {'Professor':>10} {'Fairness':>10} {'Rank':>6} {'Crowding':>10}")
        print("-" * 60)

        for i, chrom in enumerate(self.pareto_front):
            obj = chrom.objectives
            rank = chrom.metadata.get("rank", -1)
            crowding = chrom.metadata.get("crowding_distance", 0.0)

            # Handle infinite crowding distance
            crowding_str = "inf" if crowding == float("inf") else f"{crowding:.4f}"

            print(
                f"{i+1:<6} "
                f"{obj.student_satisfaction:>10.4f} "
                f"{obj.professor_satisfaction:>10.4f} "
                f"{obj.fairness:>10.4f} "
                f"{rank:>6} "
                f"{crowding_str:>10}"
            )

        print("-" * 60)

        # Print objective ranges
        student_sats = [c.objectives.student_satisfaction for c in self.pareto_front]
        prof_sats = [c.objectives.professor_satisfaction for c in self.pareto_front]
        fairness_vals = [c.objectives.fairness for c in self.pareto_front]

        print("\nObjective Ranges:")
        print(f"  Student Satisfaction:  [{min(student_sats):.4f}, {max(student_sats):.4f}]")
        print(f"  Professor Satisfaction: [{min(prof_sats):.4f}, {max(prof_sats):.4f}]")
        print(f"  Fairness:              [{min(fairness_vals):.4f}, {max(fairness_vals):.4f}]")

        # Print constraint info
        feasible_count = sum(
            1 for c in self.pareto_front
            if c.constraints and c.constraints.total_penalty == 0
        )
        print(f"\nFeasible solutions: {feasible_count}/{len(self.pareto_front)}")

    def get_pareto_front(self) -> List[Chromosome]:
        """Get the final Pareto front."""
        return self.pareto_front

    def get_pareto_front_objectives(self) -> List[Dict[str, float]]:
        """
        Get objective values for all solutions in Pareto front.

        Returns:
            List of dictionaries with objective values
        """
        result = []
        for chrom in self.pareto_front:
            result.append({
                "student_satisfaction": chrom.objectives.student_satisfaction,
                "professor_satisfaction": chrom.objectives.professor_satisfaction,
                "fairness": chrom.objectives.fairness,
                "rank": chrom.metadata.get("rank", -1),
                "crowding_distance": chrom.metadata.get("crowding_distance", 0.0),
            })
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "algorithm": "NSGA-II",
            "population_size": self.config.algorithm.population_size,
            "generations": self.config.algorithm.max_generations,
            "pareto_front_size": len(self.pareto_front),
            "num_objectives": 3,
            "objectives": ["student_satisfaction", "professor_satisfaction", "fairness"],
        }

    def __repr__(self) -> str:
        return (
            f"NSGA2(\n"
            f"  config={self.config.algorithm},\n"
            f"  nsga2_config={self.nsga2_config}\n"
            f")"
        )
