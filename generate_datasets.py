import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

# ============================================================
# 1. UNIVERSITIES
# ============================================================
universities_data = [
    ("Sharif University of Technology", 1, "Tehran"),
    ("University of Tehran", 2, "Tehran"),
    ("Amirkabir University of Technology", 3, "Tehran"),
    ("Iran University of Science and Technology", 4, "Tehran"),
    ("Isfahan University of Technology", 5, "Isfahan"),
    ("Ferdowsi University of Mashhad", 6, "Mashhad"),
    ("Shahid Beheshti University", 7, "Tehran"),
    ("University of Isfahan", 8, "Isfahan"),
    ("Tarbiat Modares University", 9, "Tehran"),
    ("K.N. Toosi University of Technology", 10, "Tehran"),
    ("University of Tabriz", 11, "Tabriz"),
    ("Shiraz University", 12, "Shiraz"),
    ("Razi University", 13, "Kermanshah"),
    ("University of Guilan", 14, "Rasht"),
    ("Mazandaran University", 15, "Sari"),
    ("University of Kurdistan", 16, "Sanandaj"),
    ("Bu-Ali Sina University", 17, "Hamadan"),
    ("University of Mohaghegh Ardabili", 18, "Ardabil"),
    ("University of Zanjan", 19, "Zanjan"),
    ("Payame Noor University", 20, "Tehran"),
    ("Islamic Azad University (Central Tehran)", 21, "Tehran"),
    ("Shahed University", 22, "Tehran"),
    ("Allameh Tabataba'i University", 23, "Tehran"),
    ("Imam Khomeini International University", 24, "Qazvin"),
    ("Yasouj University", 25, "Yasouj"),
]

universities = []
for name, rank, city in universities_data:
    qw = round(1.0 - ((rank - 1) / 24) * 0.5, 3)
    universities.append({"UniversityName": name, "Rank": rank, "QualityWeight": qw, "City": city})

df_universities = pd.DataFrame(universities)

# ============================================================
# 2. FIELDS
# ============================================================
fields_data = [
    "Artificial Intelligence",
    "Software Engineering",
    "Computer Networks",
    "Computer Architecture",
]

df_fields = pd.DataFrame({"FieldName": fields_data})

# ============================================================
# 3. PROFESSORS
# ============================================================
professors_data = [
    # AI - 3 professors
    ("P01", "Dr. Ahmad Mohammadi", "Artificial Intelligence", "Professor", 7, 2, "Bldg-A 301", "a.mohammadi@univ.ac.ir"),
    ("P02", "Dr. Fatemeh Hosseini", "Artificial Intelligence", "Associate Professor", 5, 1, "Bldg-A 305", "f.hosseini@univ.ac.ir"),
    ("P03", "Dr. Mohammad Rezaei", "Artificial Intelligence", "Assistant Professor", 4, 1, "Bldg-A 310", "m.rezaei@univ.ac.ir"),
    # SE - 3 professors
    ("P04", "Dr. Ali Karimi", "Software Engineering", "Professor", 7, 2, "Bldg-B 201", "a.karimi@univ.ac.ir"),
    ("P05", "Dr. Zahra Ahmadi", "Software Engineering", "Associate Professor", 5, 1, "Bldg-B 205", "z.ahmadi@univ.ac.ir"),
    ("P06", "Dr. Reza Faraji", "Software Engineering", "Assistant Professor", 4, 1, "Bldg-B 210", "r.faraji@univ.ac.ir"),
    # CN - 3 professors
    ("P07", "Dr. Hossein Mousavi", "Computer Networks", "Professor", 7, 2, "Bldg-C 101", "h.mousavi@univ.ac.ir"),
    ("P08", "Dr. Maryam Sadeghi", "Computer Networks", "Associate Professor", 5, 1, "Bldg-C 105", "m.sadeghi@univ.ac.ir"),
    ("P09", "Dr. Saeed Jafari", "Computer Networks", "Assistant Professor", 4, 1, "Bldg-C 110", "s.jafari@univ.ac.ir"),
    # CA - 3 professors
    ("P10", "Dr. Behzad Ghorbani", "Computer Architecture", "Professor", 7, 2, "Bldg-D 101", "b.ghorbani@univ.ac.ir"),
    ("P11", "Dr. Nasrin Taghavi", "Computer Architecture", "Associate Professor", 5, 1, "Bldg-D 105", "n.taghavi@univ.ac.ir"),
    ("P12", "Dr. Amir Pourebrahim", "Computer Architecture", "Assistant Professor", 4, 1, "Bldg-D 110", "a.pourebrahim@univ.ac.ir"),
]

professors = []
for pid, name, field, rank, cap, mincap, office, email in professors_data:
    professors.append({
        "ProfessorID": pid, "ProfessorName": name, "Field": field,
        "AcademicRank": rank, "Capacity": cap, "MinCapacity": mincap,
        "Office": office, "Email": email
    })

df_professors = pd.DataFrame(professors)

# ============================================================
# 4. STUDENTS
# ============================================================

# Name pools (Iranian names)
male_names = [
    "Mohammad Jafari", "Ali Ahmadi", "Reza Kazemi", "Amir Hosseini",
    "Mohammad Reza", "Hossein Shahidi", "Ali Razavi", "Saeed Mohammadi",
    "Mehdi Karimi", "Arash Ghorbani", "Milad Sadeghi", "Peiman Hosseini",
    "Navid Jafari", "Kian Rahimi", "Danial Farhadi", "Amir Mahdi Pour",
    "Mobin Taheri", "Yasin Mokhtari", "Pouria Azimi", "Saman Bagheri",
    "Arman Yousefi", "Parsa Zamani", "Kasra Nouri", "Benyamin Salimi",
    "Sina Asadi", "Omid Habibi", "Kamran Moradi", "Vahid Norouzi",
    "Ehsan Abbasi", "Shayan Ghafari"
]

female_names = [
    "Sara Bagheri", "Maryam Hosseini", "Zahra Moradi", "Fatemeh Rostami",
    "Nasim Yekta", "Zeinab Karimi", "Sahar Ahmadi", "Mahsa Rezaei",
    "Parisa Mousavi", "Nazanin Sadeghi", "Golnaz Shahidi", "Azadeh Faraji",
    "Hanieh Jafari", "Mahboubeh Ghorbani", "Sedigheh Taheri", "Leila Mohammadi",
    "Taraneh Razavi", "Shirin Hosseini", "Mina Bagheri", "Negin Asadi",
    "Yalda Zamani", "Aysan Pour", "Roya Abbasi", "Somayeh Norouzi",
    "Faezeh Salehi", "Zohreh Kazemi", "Mahnaz Rezaei", "Parvin Ahmadi",
    "Arezou Mohammadi", "Maryam Jafari"
]

# Universities with weights for realistic GPA generation
uni_weights = {u["UniversityName"]: u["QualityWeight"] for u in universities}
high_quality_unis = [name for name, w in uni_weights.items() if w >= 0.85]
mid_quality_unis = [name for name, w in uni_weights.items() if 0.65 <= w < 0.85]
low_quality_unis = [name for name, w in uni_weights.items() if w < 0.65]

# Field distribution: 15 per field, 30M/30F total
# Per field: 8 male + 7 female or 7 male + 8 female (alternating)
field_students = {
    "Artificial Intelligence": {"male": 8, "female": 7},
    "Software Engineering": {"male": 7, "female": 8},
    "Computer Networks": {"male": 8, "female": 7},
    "Computer Architecture": {"male": 7, "female": 8},
}

# 6 quota students (10% of 60)
quota_indices = random.sample(range(60), 6)  # Which student indices are quota

students = []
student_id = 1
male_idx = 0
female_idx = 0

for field in fields_data:
    m_count = field_students[field]["male"]
    f_count = field_students[field]["female"]

    # Male students for this field
    for i in range(m_count):
        name = male_names[male_idx]
        male_idx += 1

        # University selection (weighted toward better unis for better students)
        if random.random() < 0.4:
            uni = random.choice(high_quality_unis)
        elif random.random() < 0.7:
            uni = random.choice(mid_quality_unis)
        else:
            uni = random.choice(low_quality_unis)

        qw = uni_weights[uni]

        # GPA generation (correlated with university quality)
        base_gpa = 12 + qw * 6  # Range roughly 15-18
        prev_gpa = round(min(20, max(12, np.random.normal(base_gpa, 1.2))), 1)
        curr_gpa = round(min(20, max(12, np.random.normal(base_gpa + 0.3, 1.0))), 1)

        # Entry type
        is_quota = student_id - 1 in quota_indices
        entry_type = "Quota" if is_quota else "Regular"

        # Quality score
        gpa_comp = ((prev_gpa + curr_gpa) / 2) / 20.0 * 100
        uni_comp = qw * 100
        base_score = (gpa_comp * 0.60) + (uni_comp * 0.40)
        quality_score = round(base_score * 0.85 if is_quota else base_score, 2)

        students.append({
            "StudentID": f"S{student_id:02d}",
            "StudentName": name,
            "Gender": "Male",
            "Field": field,
            "PreviousUniversity": uni,
            "PreviousGPA": prev_gpa,
            "CurrentGPA": curr_gpa,
            "EntryType": entry_type,
            "QualityScore": quality_score,
            "Notes": ""
        })
        student_id += 1

    # Female students for this field
    for i in range(f_count):
        name = female_names[female_idx]
        female_idx += 1

        if random.random() < 0.4:
            uni = random.choice(high_quality_unis)
        elif random.random() < 0.7:
            uni = random.choice(mid_quality_unis)
        else:
            uni = random.choice(low_quality_unis)

        qw = uni_weights[uni]

        base_gpa = 12 + qw * 6
        prev_gpa = round(min(20, max(12, np.random.normal(base_gpa, 1.2))), 1)
        curr_gpa = round(min(20, max(12, np.random.normal(base_gpa + 0.3, 1.0))), 1)

        is_quota = student_id - 1 in quota_indices
        entry_type = "Quota" if is_quota else "Regular"

        gpa_comp = ((prev_gpa + curr_gpa) / 2) / 20.0 * 100
        uni_comp = qw * 100
        base_score = (gpa_comp * 0.60) + (uni_comp * 0.40)
        quality_score = round(base_score * 0.85 if is_quota else base_score, 2)

        students.append({
            "StudentID": f"S{student_id:02d}",
            "StudentName": name,
            "Gender": "Female",
            "Field": field,
            "PreviousUniversity": uni,
            "PreviousGPA": prev_gpa,
            "CurrentGPA": curr_gpa,
            "EntryType": entry_type,
            "QualityScore": quality_score,
            "Notes": ""
        })
        student_id += 1

df_students = pd.DataFrame(students)

# ============================================================
# 5. STUDENT PREFERENCES
# ============================================================

# Build field -> professor mapping
field_professors = {}
for p in professors:
    field_professors.setdefault(p["Field"], []).append(p["ProfessorID"])

all_prof_ids = [p["ProfessorID"] for p in professors]

student_prefs = []
# Explicitly choose which students will rank fewer (15% = 9 students)
fewer_student_indices = random.sample(range(60), 9)
print(f"DEBUG: fewer_student_indices = {sorted(fewer_student_indices)}")

for idx, s in enumerate(students):
    sid = s["StudentID"]
    student_field = s["Field"]
    same_field_profs = field_professors[student_field]
    diff_field_profs = [p for p in all_prof_ids if p not in same_field_profs]

    # 15% rank fewer (8-11 choices), rest rank all 12
    if idx in fewer_student_indices:
        num_choices = random.randint(8, 11)
    else:
        num_choices = 12

    if idx < 5 or idx in fewer_student_indices:
        print(f"DEBUG: idx={idx}, sid={s['StudentID']}, num_choices={num_choices}, in_fewer={idx in fewer_student_indices}")

    # Build preference: 70% same field in top choices
    prefs = []
    same_copy = same_field_profs.copy()
    diff_copy = diff_field_profs.copy()
    random.shuffle(same_copy)
    random.shuffle(diff_copy)

    # First 3-4 choices: mostly same field
    top_count = min(random.choice([3, 4]), len(same_copy))
    prefs.extend(same_copy[:top_count])
    remaining_same = same_copy[top_count:]

    # Fill remaining with mix
    all_remaining = remaining_same + diff_copy
    random.shuffle(all_remaining)

    for prof in all_remaining:
        if len(prefs) >= num_choices:
            break
        if prof not in prefs:
            prefs.append(prof)

    row = {"StudentID": sid}
    for i, prof in enumerate(prefs[:12]):
        row[f"Choice{i+1}"] = prof
    student_prefs.append(row)

df_student_prefs = pd.DataFrame(student_prefs)
# Fill NaN with empty string
df_student_prefs = df_student_prefs.fillna("")

# ============================================================
# 6. PROFESSOR PREFERENCES
# ============================================================

professor_prefs = []
# Explicitly choose which professors will rank fewer (20% = 2-3 professors)
fewer_prof_indices = random.sample(range(12), 3)

for idx, p in enumerate(professors):
    pid = p["ProfessorID"]
    prof_field = p["Field"]
    same_field_students = [s["StudentID"] for s in students if s["Field"] == prof_field]
    diff_field_students = [s["StudentID"] for s in students if s["Field"] != prof_field]

    # 25% rank fewer (30-55 choices), rest rank all 60
    if idx in fewer_prof_indices:
        num_choices = random.randint(30, 55)
    else:
        num_choices = 60

    # Sort by quality score within field groups
    same_sorted = sorted(same_field_students, key=lambda sid: 
        -df_students[df_students["StudentID"] == sid]["QualityScore"].values[0])
    diff_sorted = sorted(diff_field_students, key=lambda sid: 
        -df_students[df_students["StudentID"] == sid]["QualityScore"].values[0])

    # 70% of top choices from same field
    top_same_count = int(num_choices * 0.7)
    prefs = same_sorted[:top_same_count]

    # Fill remaining
    remaining_same = [s for s in same_sorted if s not in prefs]
    all_remaining = remaining_same + diff_sorted
    random.shuffle(all_remaining)  # Shuffle to avoid pure quality ordering

    for sid in all_remaining:
        if len(prefs) >= num_choices:
            break
        if sid not in prefs:
            prefs.append(sid)

    row = {"ProfessorID": pid}
    for i, sid in enumerate(prefs[:60]):
        row[f"Choice{i+1}"] = sid
    professor_prefs.append(row)

df_professor_prefs = pd.DataFrame(professor_prefs)
df_professor_prefs = df_professor_prefs.fillna("")

# ============================================================
# SAVE TO EXCEL
# ============================================================

output_dir = r"D:\darsha\arshad\term2\algorithm\project"

df_universities.to_excel(f"{output_dir}/Universities.xlsx", index=False, sheet_name="Universities")
df_fields.to_excel(f"{output_dir}/Fields.xlsx", index=False, sheet_name="Fields")
df_professors.to_excel(f"{output_dir}/Professors.xlsx", index=False, sheet_name="Professors")
df_students.to_excel(f"{output_dir}/Students.xlsx", index=False, sheet_name="Students")
df_student_prefs.to_excel(f"{output_dir}/StudentPreferences.xlsx", index=False, sheet_name="StudentPreferences")
df_professor_prefs.to_excel(f"{output_dir}/ProfessorPreferences.xlsx", index=False, sheet_name="ProfessorPreferences")

print("=" * 60)
print("DATASETS GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"\nUniversities: {len(df_universities)} rows")
print(f"Fields: {len(df_fields)} rows")
print(f"Professors: {len(df_professors)} rows")
print(f"Students: {len(df_students)} rows")
print(f"StudentPreferences: {len(df_student_prefs)} rows")
print(f"ProfessorPreferences: {len(df_professor_prefs)} rows")

print("\n--- Gender Distribution ---")
print(df_students["Gender"].value_counts().to_string())

print("\n--- Entry Type Distribution ---")
print(df_students["EntryType"].value_counts().to_string())

print("\n--- Students per Field ---")
print(df_students["Field"].value_counts().to_string())

print("\n--- QualityScore Stats ---")
print(f"Mean: {df_students['QualityScore'].mean():.2f}")
print(f"Std:  {df_students['QualityScore'].std():.2f}")
print(f"Min:  {df_students['QualityScore'].min():.2f}")
print(f"Max:  {df_students['QualityScore'].max():.2f}")

print("\n--- Quota Students ---")
quota_students = df_students[df_students["EntryType"] == "Quota"]
print(quota_students[["StudentID", "StudentName", "Field", "QualityScore"]].to_string(index=False))

print("\n--- Student Preferences Stats ---")
pref_counts = df_student_prefs.notna().sum(axis=1) - 1  # Subtract StudentID column
print(f"Avg choices per student: {pref_counts.mean():.1f}")
print(f"Min choices: {pref_counts.min()}")
print(f"Max choices: {pref_counts.max()}")

print("\n--- Professor Preferences Stats ---")
prof_pref_counts = df_professor_prefs.notna().sum(axis=1) - 1
print(f"Avg choices per professor: {prof_pref_counts.mean():.1f}")
print(f"Min choices: {prof_pref_counts.min()}")
print(f"Max choices: {prof_pref_counts.max()}")

print("\n--- Files Saved ---")
print(f"1. {output_dir}/Universities.xlsx")
print(f"2. {output_dir}/Fields.xlsx")
print(f"3. {output_dir}/Professors.xlsx")
print(f"4. {output_dir}/Students.xlsx")
print(f"5. {output_dir}/StudentPreferences.xlsx")
print(f"6. {output_dir}/ProfessorPreferences.xlsx")
