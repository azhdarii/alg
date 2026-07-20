"""Generate test datasets of different sizes."""

import random
import pandas as pd
from pathlib import Path

random.seed(42)

# Names pools
MALE_NAMES = [
    "Mohammad Jafari", "Ali Ahmadi", "Reza Kazemi", "Amir Hosseini",
    "Mohammad Reza", "Hossein Shahidi", "Ali Razavi", "Saeed Mohammadi",
    "Mehdi Karimi", "Arash Ghorbani", "Milad Sadeghi", "Peiman Hosseini",
    "Navid Jafari", "Kian Rahimi", "Danial Farhadi", "Amir Mahdi Pour",
    "Mobin Taheri", "Yasin Mokhtari", "Pouria Azimi", "Saman Bagheri",
    "Arman Yousefi", "Parsa Zamani", "Kasra Nouri", "Benyamin Salimi",
    "Sina Asadi", "Omid Habibi", "Kamran Moradi", "Vahid Norouzi",
    "Ehsan Abbasi", "Shayan Ghafari", "Pedram Qorbani", "Kaveh Moradi",
    "Behnam Asgari", "Farhad Nazari", "Iman Hosseini", "Mostafa Karimi",
    "Reza Ahmadi", "Sobhan Jafari", "Younes Mohammadi", "Armin Razavi"
]

FEMALE_NAMES = [
    "Sara Bagheri", "Maryam Hosseini", "Zahra Moradi", "Fatemeh Rostami",
    "Nasim Yekta", "Zeinab Karimi", "Sahar Ahmadi", "Mahsa Rezaei",
    "Parisa Mousavi", "Nazanin Sadeghi", "Golnaz Shahidi", "Azadeh Faraji",
    "Hanieh Jafari", "Mahboubeh Ghorbani", "Sedigheh Taheri", "Leila Mohammadi",
    "Taraneh Razavi", "Shirin Hosseini", "Mina Bagheri", "Negin Asadi",
    "Yalda Zamani", "Aysan Pour", "Roya Abbasi", "Somayeh Norouzi",
    "Faezeh Salehi", "Zohreh Kazemi", "Mahnaz Rezaei", "Parvin Ahmadi",
    "Arezou Mohammadi", "Maryam Jafari", "Negar Akbari", "Elham Zamani",
    "Shadi Bahrami", "Pourandokht Mohammadi", "Mahsa Jafari", "Sanaz Ahmadi",
    "Noushin Ghorbani", "Parastoo Karimi", "Setareh Hosseini", "Ghazal Moradi"
]

FIELDS = ["Artificial Intelligence", "Software Engineering", "Computer Networks", "Computer Architecture"]

UNIVERSITIES = [
    ("Sharif University of Technology", 1.0),
    ("University of Tehran", 0.979),
    ("Amirkabir University of Technology", 0.958),
    ("Isfahan University of Technology", 0.917),
    ("Ferdowsi University of Mashhad", 0.896),
    ("Shahid Beheshti University", 0.875),
    ("Iran University of Science and Technology", 0.938),
    ("K.N. Toosi University of Technology", 0.813),
    ("University of Tabriz", 0.792),
    ("Shiraz University", 0.771),
]


def generate_professors(num_per_field: int = 3) -> pd.DataFrame:
    """Generate professors."""
    profs = []
    prof_id = 1
    for field in FIELDS:
        for i in range(num_per_field):
            rank = ["Professor", "Associate Professor", "Assistant Professor"][i % 3]
            capacity = [7, 5, 4][i % 3]
            min_cap = [2, 1, 1][i % 3]
            profs.append({
                "ProfessorID": f"P{prof_id:02d}",
                "ProfessorName": f"Dr. {random.choice(MALE_NAMES)}",
                "Field": field,
                "AcademicRank": rank,
                "Capacity": capacity,
                "MinCapacity": min_cap,
                "Office": f"Bldg-{chr(65+i)} {100+prof_id}",
                "Email": f"prof{prof_id}@univ.ac.ir"
            })
            prof_id += 1
    return pd.DataFrame(profs)


def generate_students(num_students: int) -> pd.DataFrame:
    """Generate students."""
    students = []
    num_per_field = num_students // 4
    remainder = num_students % 4

    stu_id = 1
    male_idx = 0
    female_idx = 0

    for field_idx, field in enumerate(FIELDS):
        count = num_per_field + (1 if field_idx < remainder else 0)
        for i in range(count):
            if i % 2 == 0 and male_idx < len(MALE_NAMES):
                name = MALE_NAMES[male_idx]
                male_idx += 1
                gender = "Male"
            elif female_idx < len(FEMALE_NAMES):
                name = FEMALE_NAMES[female_idx]
                female_idx += 1
                gender = "Female"
            else:
                name = MALE_NAMES[male_idx % len(MALE_NAMES)]
                male_idx += 1
                gender = "Male"

            uni = random.choice(UNIVERSITIES)
            qw = uni[1]
            base_gpa = 14 + qw * 4
            prev_gpa = round(min(20, max(12, random.gauss(base_gpa, 1.2))), 1)
            curr_gpa = round(min(20, max(12, random.gauss(base_gpa + 0.3, 1.0))), 1)

            gpa_comp = ((prev_gpa + curr_gpa) / 2) / 20.0 * 100
            uni_comp = qw * 100
            quality = round((gpa_comp * 0.6) + (uni_comp * 0.4), 2)

            entry_type = "Quota" if random.random() < 0.1 else "Regular"
            if entry_type == "Quota":
                quality = round(quality * 0.85, 2)

            students.append({
                "StudentID": f"S{stu_id:02d}",
                "StudentName": name,
                "Gender": gender,
                "Field": field,
                "PreviousUniversity": uni[0],
                "PreviousGPA": prev_gpa,
                "CurrentGPA": curr_gpa,
                "EntryType": entry_type,
                "QualityScore": quality,
                "Notes": ""
            })
            stu_id += 1

    return pd.DataFrame(students)


def generate_preferences(students_df: pd.DataFrame, profs_df: pd.DataFrame,
                         preference_type: str = "student") -> pd.DataFrame:
    """Generate preference lists."""
    if preference_type == "student":
        return generate_student_preferences(students_df, profs_df)
    else:
        return generate_professor_preferences(students_df, profs_df)


def generate_student_preferences(students_df: pd.DataFrame, profs_df: pd.DataFrame) -> pd.DataFrame:
    """Generate student preferences."""
    field_profs = {}
    for _, prof in profs_df.iterrows():
        field_profs.setdefault(prof["Field"], []).append(prof["ProfessorID"])

    all_profs = profs_df["ProfessorID"].tolist()
    prefs = []

    for _, student in students_df.iterrows():
        same_field = field_profs.get(student["Field"], [])
        diff_field = [p for p in all_profs if p not in same_field]

        num_choices = min(12, len(all_profs))
        chosen = same_field[:min(3, len(same_field))].copy()
        random.shuffle(diff_field)
        chosen.extend(diff_field[:num_choices - len(chosen)])
        random.shuffle(chosen[3:] if len(chosen) > 3 else chosen)

        row = {"StudentID": student["StudentID"]}
        for i, prof_id in enumerate(chosen[:num_choices]):
            row[f"Choice{i+1}"] = prof_id
        prefs.append(row)

    return pd.DataFrame(prefs)


def generate_professor_preferences(students_df: pd.DataFrame, profs_df: pd.DataFrame) -> pd.DataFrame:
    """Generate professor preferences."""
    field_students = {}
    for _, student in students_df.iterrows():
        field_students.setdefault(student["Field"], []).append(student["StudentID"])

    all_students = students_df["StudentID"].tolist()
    prefs = []

    for _, prof in profs_df.iterrows():
        same_field = field_students.get(prof["Field"], [])
        diff_field = [s for s in all_students if s not in same_field]

        num_choices = min(60, len(all_students))
        same_sorted = sorted(same_field, key=lambda x: float(x[1:]) if x[1:].isdigit() else 0, reverse=True)
        chosen = same_sorted[:int(num_choices * 0.7)]
        random.shuffle(diff_field)
        chosen.extend(diff_field[:num_choices - len(chosen)])

        row = {"ProfessorID": prof["ProfessorID"]}
        for i, stu_id in enumerate(chosen[:num_choices]):
            row[f"Choice{i+1}"] = stu_id
        prefs.append(row)

    return pd.DataFrame(prefs)


def generate_dataset(name: str, num_students: int, output_dir: Path):
    """Generate a complete dataset."""
    print(f"Generating {name} dataset ({num_students} students)...")

    profs_per_field = max(2, num_students // 20)
    profs_df = generate_professors(profs_per_field)
    students_df = generate_students(num_students)
    student_prefs_df = generate_preferences(students_df, profs_df, "student")
    prof_prefs_df = generate_preferences(students_df, profs_df, "professor")

    # Universities and fields
    unis_df = pd.DataFrame([
        {"UniversityName": name, "Rank": i+1, "QualityWeight": qw, "City": "Tehran"}
        for i, (name, qw) in enumerate(UNIVERSITIES)
    ])
    fields_df = pd.DataFrame({"FieldName": FIELDS})

    # Save
    dataset_dir = output_dir / name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    students_df.to_excel(dataset_dir / "Students.xlsx", index=False)
    profs_df.to_excel(dataset_dir / "Professors.xlsx", index=False)
    student_prefs_df.to_excel(dataset_dir / "StudentPreferences.xlsx", index=False)
    prof_prefs_df.to_excel(dataset_dir / "ProfessorPreferences.xlsx", index=False)
    unis_df.to_excel(dataset_dir / "Universities.xlsx", index=False)
    fields_df.to_excel(dataset_dir / "Fields.xlsx", index=False)

    print(f"  Students: {len(students_df)}, Professors: {len(profs_df)}")
    return dataset_dir


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "datasets"
    output_dir.mkdir(exist_ok=True)

    # Generate datasets of different sizes
    generate_dataset("small", 20, output_dir)
    generate_dataset("medium", 60, output_dir)
    generate_dataset("large", 150, output_dir)

    print("\nAll datasets generated!")
