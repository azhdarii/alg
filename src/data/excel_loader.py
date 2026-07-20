"""Excel data loader for reading datasets."""

import pandas as pd
from typing import List, Dict, Tuple
from ..models.student import Student
from ..models.professor import Professor
from ..config.configuration import DataConfig


class DataLoader:
    """
    Loads and validates data from Excel files.

    This class is responsible for:
    - Reading Excel files
    - Converting raw data to domain objects
    - Validating data consistency
    - Building preference lists

    Follows Single Responsibility Principle: only handles data loading.
    """

    def __init__(self, config: DataConfig):
        """
        Initialize the data loader.

        Args:
            config: Data configuration with file paths
        """
        self.config = config
        self._students: List[Student] = []
        self._professors: List[Professor] = []
        self._universities: Dict[str, float] = {}
        self._fields: List[str] = []

    def load_all(self) -> Tuple[List[Student], List[Professor]]:
        """
        Load all datasets and return domain objects.

        Returns:
            Tuple of (students, professors)

        Raises:
            FileNotFoundError: If any required file is missing
            ValueError: If data validation fails
        """
        self._load_universities()
        self._load_fields()
        self._load_professors()
        self._load_students()
        self._load_student_preferences()
        self._load_professor_preferences()
        self._validate_consistency()
        return self._students, self._professors

    def _load_universities(self) -> None:
        """Load university data and build weight lookup."""
        df = pd.read_excel(self.config.universities_file)
        for _, row in df.iterrows():
            self._universities[row["UniversityName"]] = row["QualityWeight"]

    def _load_fields(self) -> None:
        """Load available fields."""
        df = pd.read_excel(self.config.fields_file)
        self._fields = df["FieldName"].tolist()

    def _load_professors(self) -> None:
        """Load professor data from Excel."""
        df = pd.read_excel(self.config.professors_file)
        self._professors = []
        for _, row in df.iterrows():
            prof = Professor(
                professor_id=row["ProfessorID"],
                name=row["ProfessorName"],
                field=row["Field"],
                academic_rank=row["AcademicRank"],
                capacity=int(row["Capacity"]),
                min_capacity=int(row["MinCapacity"]),
                office=row["Office"],
                email=row["Email"],
            )
            self._professors.append(prof)

    def _load_students(self) -> None:
        """Load student data from Excel."""
        df = pd.read_excel(self.config.students_file)
        self._students = []
        for _, row in df.iterrows():
            student = Student(
                student_id=row["StudentID"],
                name=row["StudentName"],
                gender=row["Gender"],
                field=row["Field"],
                previous_university=row["PreviousUniversity"],
                previous_gpa=float(row["PreviousGPA"]),
                current_gpa=float(row["CurrentGPA"]),
                entry_type=row["EntryType"],
                quality_score=float(row["QualityScore"]),
            )
            self._students.append(student)

    def _load_student_preferences(self) -> None:
        """Load student preferences and assign to Student objects."""
        df = pd.read_excel(self.config.student_preferences_file)
        student_map = {s.student_id: s for s in self._students}

        for _, row in df.iterrows():
            student_id = row["StudentID"]
            if student_id not in student_map:
                continue

            preferences = []
            for i in range(1, 13):
                col = f"Choice{i}"
                if col in row and pd.notna(row[col]) and str(row[col]).strip():
                    preferences.append(str(row[col]))

            student_map[student_id].preference_list = preferences

    def _load_professor_preferences(self) -> None:
        """Load professor preferences and assign to Professor objects."""
        df = pd.read_excel(self.config.professor_preferences_file)
        prof_map = {p.professor_id: p for p in self._professors}

        for _, row in df.iterrows():
            prof_id = row["ProfessorID"]
            if prof_id not in prof_map:
                continue

            preferences = []
            for i in range(1, 61):
                col = f"Choice{i}"
                if col in row and pd.notna(row[col]) and str(row[col]).strip():
                    preferences.append(str(row[col]))

            prof_map[prof_id].preference_list = preferences

    def _validate_consistency(self) -> None:
        """Validate that data is consistent across files."""
        student_ids = {s.student_id for s in self._students}
        prof_ids = {p.professor_id for p in self._professors}
        student_fields = {s.field for s in self._students}
        prof_fields = {p.field for p in self._professors}

        # Check fields exist
        for field in student_fields:
            if field not in self._fields:
                raise ValueError(f"Student field '{field}' not in Fields.xlsx")

        for field in prof_fields:
            if field not in self._fields:
                raise ValueError(f"Professor field '{field}' not in Fields.xlsx")

        # Check all preference references exist
        for student in self._students:
            for prof_id in student.preference_list:
                if prof_id not in prof_ids:
                    raise ValueError(
                        f"Student {student.student_id} references "
                        f"unknown professor {prof_id}"
                    )

        for prof in self._professors:
            for sid in prof.preference_list:
                if sid not in student_ids:
                    raise ValueError(
                        f"Professor {prof.professor_id} references "
                        f"unknown student {sid}"
                    )

    def get_university_weight(self, university_name: str) -> float:
        """
        Get quality weight for a university.

        Args:
            university_name: Name of the university

        Returns:
            Quality weight (0.5-1.0)
        """
        return self._universities.get(university_name, 0.5)

    @property
    def students(self) -> List[Student]:
        """Get loaded students."""
        return self._students

    @property
    def professors(self) -> List[Professor]:
        """Get loaded professors."""
        return self._professors

    @property
    def fields(self) -> List[str]:
        """Get available fields."""
        return self._fields

    @property
    def num_students(self) -> int:
        """Number of loaded students."""
        return len(self._students)

    @property
    def num_professors(self) -> int:
        """Number of loaded professors."""
        return len(self._professors)

    def __repr__(self) -> str:
        return (
            f"DataLoader(students={self.num_students}, "
            f"professors={self.num_professors}, "
            f"fields={len(self._fields)})"
        )
