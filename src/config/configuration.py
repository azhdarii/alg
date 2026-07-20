"""Configuration management for the optimization system."""

from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path


@dataclass
class PenaltyConfig:
    """
    Penalty coefficients for constraint violations.

    Attributes:
        capacity_penalty_per_student: Penalty per student over/under capacity
        field_mismatch_penalty: Penalty for field mismatch
    """

    capacity_penalty_per_student: float = 10.0
    field_mismatch_penalty: float = 5.0

    def __repr__(self) -> str:
        return (
            f"PenaltyConfig(capacity={self.capacity_penalty_per_student}, "
            f"field={self.field_mismatch_penalty})"
        )


@dataclass
class AlgorithmConfig:
    """
    Configuration for genetic algorithm parameters.

    Attributes:
        population_size: Number of chromosomes in population
        max_generations: Maximum number of generations
        crossover_probability: Probability of crossover (0-1)
        mutation_probability: Probability of mutation (0-1)
        random_seed: Seed for reproducibility
    """

    population_size: int = 100
    max_generations: int = 200
    crossover_probability: float = 0.8
    mutation_probability: float = 0.1
    random_seed: Optional[int] = 42

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.population_size < 2:
            raise ValueError("Population size must be >= 2")
        if self.max_generations < 1:
            raise ValueError("Max generations must be >= 1")
        if not 0 <= self.crossover_probability <= 1:
            raise ValueError("Crossover probability must be 0-1")
        if not 0 <= self.mutation_probability <= 1:
            raise ValueError("Mutation probability must be 0-1")

    def __repr__(self) -> str:
        return (
            f"AlgorithmConfig(pop={self.population_size}, "
            f"gen={self.max_generations}, "
            f"cx={self.crossover_probability}, "
            f"mut={self.mutation_probability})"
        )


@dataclass
class DataConfig:
    """
    Configuration for data file paths.

    Attributes:
        students_file: Path to students Excel file
        professors_file: Path to professors Excel file
        student_preferences_file: Path to student preferences file
        professor_preferences_file: Path to professor preferences file
        universities_file: Path to universities Excel file
        fields_file: Path to fields Excel file
        output_dir: Directory for output files
    """

    students_file: str = "data/Students.xlsx"
    professors_file: str = "data/Professors.xlsx"
    student_preferences_file: str = "data/StudentPreferences.xlsx"
    professor_preferences_file: str = "data/ProfessorPreferences.xlsx"
    universities_file: str = "data/Universities.xlsx"
    fields_file: str = "data/Fields.xlsx"
    output_dir: str = "output"


@dataclass
class LoggingConfig:
    """
    Configuration for logging.

    Attributes:
        log_file: Path to log file
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_to_console: Whether to also log to console
        log_interval: Log statistics every N generations
    """

    log_file: str = "output/optimization_log.csv"
    log_level: str = "INFO"
    log_to_console: bool = True
    log_interval: int = 10


@dataclass
class Configuration:
    """
    Main configuration class aggregating all settings.

    This class follows the Single Responsibility Principle by delegating
    to specialized configuration dataclasses.

    Attributes:
        algorithm: Algorithm parameters
        penalty: Penalty coefficients
        data: Data file paths
        logging: Logging settings
    """

    algorithm: AlgorithmConfig = field(default_factory=AlgorithmConfig)
    penalty: PenaltyConfig = field(default_factory=PenaltyConfig)
    data: DataConfig = field(default_factory=DataConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_json(cls, filepath: str) -> "Configuration":
        """
        Load configuration from JSON file.

        Args:
            filepath: Path to JSON configuration file

        Returns:
            Configuration object
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        config = cls()
        if "algorithm" in data:
            config.algorithm = AlgorithmConfig(**data["algorithm"])
        if "penalty" in data:
            config.penalty = PenaltyConfig(**data["penalty"])
        if "data" in data:
            config.data = DataConfig(**data["data"])
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        return config

    def to_json(self, filepath: str) -> None:
        """
        Save configuration to JSON file.

        Args:
            filepath: Path to save JSON configuration
        """
        data = {
            "algorithm": {
                "population_size": self.algorithm.population_size,
                "max_generations": self.algorithm.max_generations,
                "crossover_probability": self.algorithm.crossover_probability,
                "mutation_probability": self.algorithm.mutation_probability,
                "random_seed": self.algorithm.random_seed,
            },
            "penalty": {
                "capacity_penalty_per_student": self.penalty.capacity_penalty_per_student,
                "field_mismatch_penalty": self.penalty.field_mismatch_penalty,
            },
            "data": {
                "students_file": self.data.students_file,
                "professors_file": self.data.professors_file,
                "student_preferences_file": self.data.student_preferences_file,
                "professor_preferences_file": self.data.professor_preferences_file,
                "universities_file": self.data.universities_file,
                "fields_file": self.data.fields_file,
                "output_dir": self.data.output_dir,
            },
            "logging": {
                "log_file": self.logging.log_file,
                "log_level": self.logging.log_level,
                "log_to_console": self.logging.log_to_console,
                "log_interval": self.logging.log_interval,
            },
        }
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def validate(self) -> bool:
        """
        Validate all configuration settings.

        Returns:
            True if valid, raises ValueError otherwise
        """
        # AlgorithmConfig validates itself in __post_init__
        # PenaltyConfig and others have sensible defaults
        Path(self.data.output_dir).mkdir(parents=True, exist_ok=True)
        return True

    def __repr__(self) -> str:
        return (
            f"Configuration(\n"
            f"  algorithm={self.algorithm},\n"
            f"  penalty={self.penalty},\n"
            f"  data={self.data},\n"
            f"  logging={self.logging}\n"
            f")"
        )
