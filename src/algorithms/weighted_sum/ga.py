"""Weighted Sum Genetic Algorithm implementation."""

import random
from typing import List, Optional, Tuple
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
from .config import WeightedSumConfig
from .fitness import WeightedSumFitness
from .selection import BinaryTournamentSelection
from .replacement import ElitistReplacement


class WeightedSumGA:
    """
    Weighted Sum Genetic Algorithm for Student-Supervisor Assignment.

    This algorithm combines multiple objectives into a single fitness
    value using weighted summation, then applies standard GA operations.

    Algorithm Flow:
    1. Initialize population
    2. Evaluate objectives and constraints
    3. Compute weighted fitness
    4. Repeat until max generations:
        a. Select parents (binary tournament)
        b. Apply crossover
        c. Apply mutation
        d. Repair offspring
        e. Evaluate offspring
        f. Compute offspring fitness
        g. Create next generation (elitist replacement)
    5. Return best solution

    Design for Inheritance:
        This class is designed to be inherited by NSGA-II:
        - _compute_fitness() is the key difference
        - _select_parents() can be overridden
        - _create_next_generation() is the main extension point
        - evaluate_chromosome() is shared

    Follows Open/Closed Principle: open for extension (NSGA-II),
    closed for modification (shared infrastructure unchanged).
    """

    def __init__(
        self,
        config: Configuration,
        ws_config: Optional[WeightedSumConfig] = None,
    ):
        """
        Initialize the Weighted Sum GA.

        Args:
            config: Main configuration
            ws_config: Weighted Sum specific configuration
        """
        self.config = config
        self.ws_config = ws_config or WeightedSumConfig()

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
        self.fitness_calculator: Optional[WeightedSumFitness] = None

        # Operators (initialized later)
        self.initializer: Optional[PopulationInitializer] = None
        self.selection: Optional[BinaryTournamentSelection] = None
        self.replacement: Optional[ElitistReplacement] = None
        self.repair: Optional[RepairOperator] = None
        self.mutation_operators: List[MutationOperator] = []
        self.crossover_operators: List[CrossoverOperator] = []

        # Logger
        self.logger: Optional[OptimizationLogger] = None

        # Best solution found
        self.best_solution: Optional[Chromosome] = None

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
        self.fitness_calculator = WeightedSumFitness(self.ws_config)

        # Population initializer
        self.initializer = PopulationInitializer(
            self.students,
            self.professors,
            seed=self.config.algorithm.random_seed or 42,
        )

        # Selection
        self.selection = BinaryTournamentSelection(
            tournament_size=self.ws_config.tournament_size
        )

        # Replacement
        self.replacement = ElitistReplacement(
            preserve_count=self.ws_config.preserve_elitism
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

        print(f"      Fitness weights: {self.ws_config.weights}")
        print(f"      Elitism: {self.ws_config.preserve_elitism}")
        print(f"      Tournament size: {self.ws_config.tournament_size}")

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

        population.generation = 0
        print(f"      Population size: {population.size}")

        return population

    def evaluate_chromosome(self, chromosome: Chromosome) -> None:
        """
        Evaluate a single chromosome (objectives, constraints, fitness).

        This method is shared between Weighted Sum and can be
        overridden or extended by NSGA-II.

        Args:
            chromosome: Chromosome to evaluate
        """
        # Compute objectives
        chromosome.objectives = self.objective_evaluator.evaluate(chromosome)

        # Compute constraints
        chromosome.constraints = self.constraint_evaluator.evaluate(chromosome)

        # Compute fitness (Weighted Sum specific)
        chromosome.fitness = self.fitness_calculator.compute_fitness(chromosome)

    def evaluate_population(self, population: Population) -> None:
        """Evaluate all unevaluated chromosomes in population."""
        for chromosome in population:
            if not chromosome.is_evaluated():
                self.evaluate_chromosome(chromosome)
            elif chromosome.fitness is None:
                chromosome.fitness = self.fitness_calculator.compute_fitness(chromosome)

    def _select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        """
        Select two parents from population.

        This method can be overridden by NSGA-II to use different
        selection (e.g., based on Pareto rank + crowding distance).

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

        Randomly selects one mutation operator and applies it.

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

    def _create_next_generation(
        self,
        current_population: Population,
        offspring: List[Chromosome],
    ) -> Population:
        """
        Create next generation using replacement strategy.

        This method can be overridden by NSGA-II to use
        Pareto-based replacement.

        Args:
            current_population: Current generation
            offspring: New offspring

        Returns:
            New Population
        """
        return self.replacement.create_next_generation(current_population, offspring)

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

    def run(self) -> Population:
        """
        Execute the Weighted Sum Genetic Algorithm.

        Returns:
            Final population with best solution
        """
        print("\n" + "=" * 60)
        print("WEIGHTED SUM GENETIC ALGORITHM")
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
        stats = population.compute_statistics()
        print(f"\n[4/6] Starting evolution...")
        print(f"      Initial best fitness: {stats.best_fitness:.4f}")

        # Evolution loop
        for generation in range(1, self.config.algorithm.max_generations + 1):
            # Generate offspring
            offspring = self._generate_offspring(population)

            # Evaluate offspring
            for chromosome in offspring:
                self.evaluate_chromosome(chromosome)

            # Create next generation
            population = self._create_next_generation(population, offspring)

            # Update best solution
            current_best = population.get_best()
            if current_best and (
                self.best_solution is None
                or current_best.fitness > self.best_solution.fitness
            ):
                self.best_solution = current_best.deep_copy()

            # Log progress
            self.logger.log_generation(population, generation)

            # Print progress every 10 generations
            if generation % 10 == 0:
                stats = population.compute_statistics()
                print(
                    f"      Gen {generation:4d} | "
                    f"Best: {stats.best_fitness:.4f} | "
                    f"Avg: {stats.avg_fitness:.4f}"
                )

        # Finalize
        print(f"\n[5/6] Evolution complete!")
        self.logger.finish(population)

        # Print best solution
        self._print_best_solution()

        print(f"\n[6/6] Done!")
        return population

    def _print_best_solution(self) -> None:
        """Print the best solution found."""
        if self.best_solution is None:
            print("No solution found!")
            return

        print("\n" + "=" * 60)
        print("BEST SOLUTION FOUND")
        print("=" * 60)

        print(f"\nFitness: {self.best_solution.fitness:.6f}")
        print(f"\nObjectives:")
        print(f"  Student Satisfaction:  {self.best_solution.objectives.student_satisfaction:.4f}")
        print(f"  Professor Satisfaction: {self.best_solution.objectives.professor_satisfaction:.4f}")
        print(f"  Fairness (lower=better): {self.best_solution.objectives.fairness:.4f}")

        print(f"\nConstraints:")
        print(f"  Capacity Violations: {self.best_solution.constraints.capacity_violation:.2f}")
        print(f"  Field Mismatches: {self.best_solution.constraints.field_mismatch_count}")

        print(f"\nAssignments:")
        for student_id, prof_id in self.best_solution.to_assignment_dict().items():
            student = next(s for s in self.students if s.student_id == student_id)
            prof = next(p for p in self.professors if p.professor_id == prof_id)
            match = "V" if student.field == prof.field else "X"
            rank = student.get_preference_rank(prof_id)
            print(f"  {student_id} ({student.field[:3]}) -> {prof_id} ({prof.field[:3]}) [{match}] pref={rank}")

        # Professor load
        print(f"\nProfessor Load:")
        load = self.best_solution.count_professor_assignments()
        for prof in self.professors:
            count = load.get(prof.professor_id, 0)
            status = "OK" if prof.min_capacity <= count <= prof.capacity else "VIOLATION"
            print(f"  {prof.professor_id}: {count}/{prof.capacity} [{status}]")

    def get_best_solution(self) -> Optional[Chromosome]:
        """Get the best solution found during optimization."""
        return self.best_solution

    def __repr__(self) -> str:
        return (
            f"WeightedSumGA(\n"
            f"  config={self.config.algorithm},\n"
            f"  ws_config={self.ws_config}\n"
            f")"
        )
