import pandas as pd
import numpy as np
import random
import argparse
from pathlib import Path

from dataset_config import (
    NUM_UNIVERSITIES, NUM_FIELDS, PROFESSORS_PER_FIELD,
    MALE_STUDENTS, FEMALE_STUDENTS, QUOTA_PERCENTAGE,
    MAX_STUDENT_PREFERENCES, MAX_PROFESSOR_PREFERENCES,
    MIN_GPA, MAX_GPA, RANDOM_SEED, OUTPUT_DIR,
)


# ── Name pools for synthetic generation ──────────────────────

UNIVERSITY_PREFIXES = [
    "Sharif", "Tehran", "Amirkabir", "Isfahan", "Ferdowsi",
    "Shahid Beheshti", "Tabriz", "Shiraz", "Guilan", "Mazandaran",
    "Kurdistan", "Bu-Ali Sina", "Zanjan", "Yazd", "Kerman",
    "Razi", "Shahed", "Tarbiat Modares", "K.N. Toosi", "Allameh Tabataba'i",
    "Imam Khomeini", "Yasouj", "Semnan", "Mazandaran", "Gondishapour",
    "Lorestan", "Hormozgan", "Sistan", "Baluchestan", "Chaharmahal",
    "Alzahra", "Tarbiat Moallem", "Payame Noor", "Islamic Azad", "Malayer",
    "Bojnurd", "Birjand", "JundiShapur", "Bandar Abbas", "Khorasan",
    "Velayat", "Ayatollah", "Mofid", "Shahroud", "Ahar",
]

UNIVERSITY_SUFFIXES = [
    "University of Technology", "University", "Institute of Technology",
    "University of Medical Sciences", "University of Science",
    "Polytechnic", "University of Advanced Technology",
]

CITIES = [
    "Tehran", "Isfahan", "Mashhad", "Tabriz", "Shiraz",
    "Kermanshah", "Rasht", "Sari", "Sanandaj", "Hamadan",
    "Ardabil", "Zanjan", "Yazd", "Kerman", "Ahvaz",
    "Bandar Abbas", "Qazvin", "Semnan", "Bojnurd", "Birjand",
    "Yasouj", "Khorramabad", "Urmia", "Bushehr", "Abadan",
]

FIELD_NAMES = [
    "Artificial Intelligence", "Software Engineering",
    "Computer Networks", "Computer Architecture",
    
]

ACADEMIC_RANKS = ["Professor", "Associate Professor", "Assistant Professor"]

FIRST_NAMES_M = [
    "Mohammad", "Ali", "Reza", "Amir", "Hossein", "Mehdi", "Arash",
    "Milad", "Peiman", "Navid", "Kian", "Danial", "Mobin", "Yasin",
    "Pouria", "Saman", "Arman", "Parsa", "Kasra", "Benyamin", "Sina",
    "Omid", "Kamran", "Vahid", "Ehsan", "Shayan", "Armin", "Dariush",
    "Farhad", "Shapour", "Ramtin", "Babak", "Cyrus", "Dara", "Kaveh",
    "Rostam", "Siavash", "Aria", "Amin", "Mehran", "Sobhan", "Yaghoob",
    "Soroush", "Pouya", "Shervin", "Payam", "Shahab", "Iman", "Hamed",
    "Javad", "Mahdi", "Mostafa", "Hamidreza", "Alireza", "Pourya",
    "Behnam", "Amirhossein", "Erfan", "Pourdad", "Khashayar",
]

LAST_NAMES = [
    "Jafari", "Ahmadi", "Kazemi", "Hosseini", "Shahidi", "Razavi",
    "Mohammadi", "Karimi", "Ghorbani", "Sadeghi", "Rostami", "Moradi",
    "Faraji", "Taheri", "Bagheri", "Yousefi", "Zamani", "Nouri",
    "Salimi", "Asadi", "Habibi", "Norouzi", "Abbasi", "Ghafari",
    "Rahimi", "Farhadi", "Mokhtari", "Azimi", "Naseri", "Rahmani",
    "Kiani", "Mousavi", "Hashemi", "Najafi", "Ebrahimi", "Aziz",
    "Salehi", "Rezaei", "Mahdavi", "Shams", "Parast", "Khoshnevis",
    "Dehghan", "Bahrami", "Tavakoli", "Moharrami", "Zare", "Golmohammadi",
    "Samadi", "Mirzaei", "Ansari", "Vahedi", "Fallah", "Shirazi",
    "Ghasemi", "Amiri", "Soltani", "Ghods", "Aghaei",
]

FIRST_NAMES_F = [
    "Sara", "Maryam", "Zahra", "Fatemeh", "Nasim", "Zeinab", "Sahar",
    "Mahsa", "Parisa", "Nazanin", "Golnaz", "Azadeh", "Hanieh",
    "Mahboubeh", "Sedigheh", "Leila", "Taraneh", "Shirin", "Mina",
    "Negin", "Yalda", "Aysan", "Roya", "Somayeh", "Faezeh", "Zohreh",
    "Mahnaz", "Parvin", "Arezou", "Mobina", "Negar", "Elham", "Maryam",
    "Sakineh", "Fereshteh", "Ghazal", "Mahdieh", "Shadi", "Atieh",
    "Nasrin", "Tannaz", "Yeganeh", "Setareh", "Golnaz", "Hana",
    "Dorna", "Asal", "Neda", "Saba", "Mahsa", "Farzaneh", "Raha",
    "Bahar", "Shabnam", "Atefeh", "Zeynab", "Parastoo", "Mina",
    "Golnar", "Tara",
]


# ── Helpers ───────────────────────────────────────────────────

def calculate_quality_score(previous_gpa, current_gpa, university_weight, entry_type):
    average_gpa = (previous_gpa + current_gpa) / 2
    gpa_component = (average_gpa / float(MAX_GPA)) * 100
    university_component = university_weight * 100
    score = 0.60 * gpa_component + 0.40 * university_component
    if entry_type == "Quota":
        score *= 0.85
    return round(score, 2)


def pick_unique(pool, count, used=None):
    """Return `count` unique items from `pool`, avoiding `used` set."""
    if used is None:
        used = set()
    available = [x for x in pool if x not in used]
    if count > len(available):
        available = pool[:]  # wrap around if exhausted
    chosen = random.sample(available, min(count, len(available)))
    used.update(chosen)
    return chosen


# ── Main generation ──────────────────────────────────────────

def generate(seed=None):
    seed = seed if seed is not None else RANDOM_SEED
    random.seed(seed)
    np.random.seed(seed)

    total_students = MALE_STUDENTS + FEMALE_STUDENTS

    # ── 1. Universities ──────────────────────────────────────
    used_uni = set()
    universities = []
    for i in range(NUM_UNIVERSITIES):
        prefix = pick_unique(UNIVERSITY_PREFIXES, 1, used_uni)[0]
        suffix = random.choice(UNIVERSITY_SUFFIXES)
        city = random.choice(CITIES)
        name = f"{prefix} {suffix}"
        rank = i + 1
        qw = round(1.0 - ((rank - 1) / max(NUM_UNIVERSITIES - 1, 1)) * 0.5, 3)
        universities.append({
            "UniversityName": name, "Rank": rank,
            "QualityWeight": qw, "City": city,
        })

    df_universities = pd.DataFrame(universities)

    # ── 2. Fields ────────────────────────────────────────────
    chosen_fields = pick_unique(FIELD_NAMES, NUM_FIELDS)
    df_fields = pd.DataFrame({"FieldName": chosen_fields})

    # ── 3. Professors ────────────────────────────────────────
    prof_counter = 1
    professors = []
    used_prof_first = set()
    used_prof_last = set()
    buildings = [chr(ord("A") + i) for i in range(NUM_FIELDS)]

    for fi, field in enumerate(chosen_fields):
        for _ in range(PROFESSORS_PER_FIELD):
            first = pick_unique(FIRST_NAMES_M, 1, used_prof_first)[0]
            last = pick_unique(LAST_NAMES, 1, used_prof_last)[0]
            rank = random.choice(ACADEMIC_RANKS)
            if rank == "Professor":
                cap, mincap = 7, 2
            elif rank == "Associate Professor":
                cap, mincap = 5, 1
            else:
                cap, mincap = 4, 1
            bldg = buildings[fi % len(buildings)]
            room = random.randint(101, 499)
            pid = f"P{prof_counter:02d}"
            professors.append({
                "ProfessorID": pid,
                "ProfessorName": f"Dr. {first} {last}",
                "Field": field,
                "AcademicRank": rank,
                "Capacity": cap,
                "MinCapacity": mincap,
                "Office": f"Bldg-{bldg} {room}",
                "Email": f"{first.lower()[0]}.{last.lower()}@univ.ac.ir",
            })
            prof_counter += 1

    total_professors = len(professors)
    df_professors = pd.DataFrame(professors)

    # ── 4. Students ──────────────────────────────────────────
    uni_weights = {u["UniversityName"]: u["QualityWeight"] for u in universities}
    high_q = [n for n, w in uni_weights.items() if w >= 0.85]
    mid_q = [n for n, w in uni_weights.items() if 0.65 <= w < 0.85]
    low_q = [n for n, w in uni_weights.items() if w < 0.65]
    if not high_q:
        high_q = list(uni_weights.keys())
    if not mid_q:
        mid_q = list(uni_weights.keys())
    if not low_q:
        low_q = list(uni_weights.keys())

    # Distribute students across fields as evenly as possible
    male_per_field = [MALE_STUDENTS // NUM_FIELDS] * NUM_FIELDS
    female_per_field = [FEMALE_STUDENTS // NUM_FIELDS] * NUM_FIELDS
    for i in range(MALE_STUDENTS % NUM_FIELDS):
        male_per_field[i] += 1
    for i in range(FEMALE_STUDENTS % NUM_FIELDS):
        female_per_field[i] += 1

    num_quota = max(1, int(total_students * QUOTA_PERCENTAGE))
    quota_indices = set(random.sample(range(total_students), min(num_quota, total_students)))

    students = []
    sid = 1
    m_name_pool = list(FIRST_NAMES_M)
    f_name_pool = list(FIRST_NAMES_F)
    last_pool = list(LAST_NAMES)
    random.shuffle(m_name_pool)
    random.shuffle(f_name_pool)
    random.shuffle(last_pool)
    last_idx = 0

    def gen_name(gender):
        nonlocal last_idx
        if gender == "Male":
            first = m_name_pool[sid % len(m_name_pool)]
        else:
            first = f_name_pool[sid % len(f_name_pool)]
        last = last_pool[last_idx % len(last_pool)]
        last_idx += 1
        return f"{first} {last}"

    for fi, field in enumerate(chosen_fields):
        for _ in range(male_per_field[fi]):
            name = gen_name("Male")
            if random.random() < 0.4:
                uni = random.choice(high_q)
            elif random.random() < 0.7:
                uni = random.choice(mid_q)
            else:
                uni = random.choice(low_q)
            qw = uni_weights[uni]
            base_gpa = MIN_GPA + qw * (MAX_GPA - MIN_GPA) * 0.6
            prev_gpa = round(min(MAX_GPA, max(MIN_GPA, np.random.normal(base_gpa, 1.2))), 1)
            curr_gpa = round(min(MAX_GPA, max(MIN_GPA, np.random.normal(base_gpa + 0.3, 1.0))), 1)
            is_quota = (sid - 1) in quota_indices
            entry_type = "Quota" if is_quota else "Regular"
            quality_score = calculate_quality_score(prev_gpa, curr_gpa, qw, entry_type)
            students.append({
                "StudentID": f"S{sid:02d}",
                "StudentName": name,
                "Gender": "Male",
                "Field": field,
                "PreviousUniversity": uni,
                "PreviousGPA": prev_gpa,
                "CurrentGPA": curr_gpa,
                "EntryType": entry_type,
                "QualityScore": quality_score,
                "Notes": "",
            })
            sid += 1

        for _ in range(female_per_field[fi]):
            name = gen_name("Female")
            if random.random() < 0.4:
                uni = random.choice(high_q)
            elif random.random() < 0.7:
                uni = random.choice(mid_q)
            else:
                uni = random.choice(low_q)
            qw = uni_weights[uni]
            base_gpa = MIN_GPA + qw * (MAX_GPA - MIN_GPA) * 0.6
            prev_gpa = round(min(MAX_GPA, max(MIN_GPA, np.random.normal(base_gpa, 1.2))), 1)
            curr_gpa = round(min(MAX_GPA, max(MIN_GPA, np.random.normal(base_gpa + 0.3, 1.0))), 1)
            is_quota = (sid - 1) in quota_indices
            entry_type = "Quota" if is_quota else "Regular"
            quality_score = calculate_quality_score(prev_gpa, curr_gpa, qw, entry_type)
            students.append({
                "StudentID": f"S{sid:02d}",
                "StudentName": name,
                "Gender": "Female",
                "Field": field,
                "PreviousUniversity": uni,
                "PreviousGPA": prev_gpa,
                "CurrentGPA": curr_gpa,
                "EntryType": entry_type,
                "QualityScore": quality_score,
                "Notes": "",
            })
            sid += 1

    df_students = pd.DataFrame(students)

    # ── 5. Student preferences ───────────────────────────────
    field_profs = {}
    for p in professors:
        field_profs.setdefault(p["Field"], []).append(p["ProfessorID"])
    all_prof_ids = [p["ProfessorID"] for p in professors]

    student_prefs = []
    fewer_count = max(1, int(total_students * 0.15))
    fewer_student_indices = set(random.sample(range(total_students), min(fewer_count, total_students)))

    for idx, s in enumerate(students):
        same_field = field_profs.get(s["Field"], [])
        diff_field = [p for p in all_prof_ids if p not in same_field]

        if idx in fewer_student_indices:
            lo = max(1, MAX_STUDENT_PREFERENCES // 2)
            hi = min(MAX_STUDENT_PREFERENCES, total_professors)
            num_choices = random.randint(lo, hi)
        else:
            num_choices = min(MAX_STUDENT_PREFERENCES, total_professors)

        prefs = []
        same_copy = same_field[:]
        diff_copy = diff_field[:]
        random.shuffle(same_copy)
        random.shuffle(diff_copy)

        top_count = min(random.choice([3, 4]), len(same_copy))
        prefs.extend(same_copy[:top_count])
        remaining = same_copy[top_count:] + diff_copy
        random.shuffle(remaining)
        for prof in remaining:
            if len(prefs) >= num_choices:
                break
            if prof not in prefs:
                prefs.append(prof)

        row = {"StudentID": s["StudentID"]}
        for i, prof in enumerate(prefs[:MAX_STUDENT_PREFERENCES]):
            row[f"Choice{i+1}"] = prof
        student_prefs.append(row)

    df_student_prefs = pd.DataFrame(student_prefs).fillna("")

    # ── 6. Professor preferences ─────────────────────────────
    professor_prefs = []
    fewer_pcount = max(1, int(total_professors * 0.25))
    fewer_prof_indices = set(random.sample(range(total_professors), min(fewer_pcount, total_professors)))

    for idx, p in enumerate(professors):
        same_field_sids = [s["StudentID"] for s in students if s["Field"] == p["Field"]]
        diff_field_sids = [s["StudentID"] for s in students if s["Field"] != p["Field"]]

        if idx in fewer_prof_indices:
            lo = max(1, MAX_PROFESSOR_PREFERENCES // 2)
            hi = min(MAX_PROFESSOR_PREFERENCES, total_students)
            num_choices = random.randint(lo, hi)
        else:
            num_choices = min(MAX_PROFESSOR_PREFERENCES, total_students)

        same_sorted = sorted(same_field_sids, key=lambda sid_: -
            df_students[df_students["StudentID"] == sid_]["QualityScore"].values[0])
        diff_sorted = sorted(diff_field_sids, key=lambda sid_: -
            df_students[df_students["StudentID"] == sid_]["QualityScore"].values[0])

        top_same = int(num_choices * 0.7)
        prefs = same_sorted[:top_same]
        remaining_same = [s for s in same_sorted if s not in prefs]
        remaining_all = remaining_same + diff_sorted
        random.shuffle(remaining_all)
        for sid_ in remaining_all:
            if len(prefs) >= num_choices:
                break
            if sid_ not in prefs:
                prefs.append(sid_)

        row = {"ProfessorID": p["ProfessorID"]}
        for i, sid_ in enumerate(prefs[:MAX_PROFESSOR_PREFERENCES]):
            row[f"Choice{i+1}"] = sid_
        professor_prefs.append(row)

    df_professor_prefs = pd.DataFrame(professor_prefs).fillna("")

    # ── Save ─────────────────────────────────────────────────
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "Universities.xlsx": df_universities,
        "Fields.xlsx": df_fields,
        "Professors.xlsx": df_professors,
        "Students.xlsx": df_students,
        "StudentPreferences.xlsx": df_student_prefs,
        "ProfessorPreferences.xlsx": df_professor_prefs,
    }
    for fname, df in files.items():
        df.to_excel(output_dir / fname, index=False, sheet_name=fname.replace(".xlsx", ""))

    # ── Summary ──────────────────────────────────────────────
    print("=" * 60)
    print("DATASETS GENERATED SUCCESSFULLY")
    print("=" * 60)
    for fname, df in files.items():
        print(f"\n{fname}: {len(df)} rows")

    print(f"\n--- Config ---")
    print(f"Universities: {NUM_UNIVERSITIES}")
    print(f"Fields: {NUM_FIELDS}")
    print(f"Professors: {total_professors} ({PROFESSORS_PER_FIELD} per field)")
    print(f"Students: {total_students} ({MALE_STUDENTS}M + {FEMALE_STUDENTS}F)")
    print(f"Quota: {num_quota} ({QUOTA_PERCENTAGE*100:.1f}%)")
    print(f"Seed: {seed}")

    print(f"\n--- Gender Distribution ---")
    print(df_students["Gender"].value_counts().to_string())

    print(f"\n--- Entry Type Distribution ---")
    print(df_students["EntryType"].value_counts().to_string())

    print(f"\n--- Students per Field ---")
    print(df_students["Field"].value_counts().to_string())

    print(f"\n--- QualityScore Stats ---")
    print(f"Mean: {df_students['QualityScore'].mean():.2f}")
    print(f"Std:  {df_students['QualityScore'].std():.2f}")
    print(f"Min:  {df_students['QualityScore'].min():.2f}")
    print(f"Max:  {df_students['QualityScore'].max():.2f}")

    print(f"\n--- Quota Students ---")
    quota_students = df_students[df_students["EntryType"] == "Quota"]
    print(quota_students[["StudentID", "StudentName", "Field", "QualityScore"]].to_string(index=False))

    print(f"\n--- Student Preferences Stats ---")
    pref_counts = df_student_prefs.notna().sum(axis=1) - 1
    print(f"Avg choices per student: {pref_counts.mean():.1f}")
    print(f"Min choices: {pref_counts.min()}")
    print(f"Max choices: {pref_counts.max()}")

    print(f"\n--- Professor Preferences Stats ---")
    prof_pref_counts = df_professor_prefs.notna().sum(axis=1) - 1
    print(f"Avg choices per professor: {prof_pref_counts.mean():.1f}")
    print(f"Min choices: {prof_pref_counts.min()}")
    print(f"Max choices: {prof_pref_counts.max()}")

    print(f"\n--- Files Saved ---")
    for i, fname in enumerate(files, 1):
        print(f"{i}. {output_dir}/{fname}")

    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate datasets from config")
    parser.add_argument("--seed", type=int, default=None, help="Override random seed")
    args = parser.parse_args()
    generate(seed=args.seed)
