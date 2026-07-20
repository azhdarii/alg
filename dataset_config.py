"""
Dataset Generation Configuration
================================
Modify these values to control the size and characteristics of the
generated dataset. Then run:  python generate_datasets.py
"""

# ── Universities ──────────────────────────────────────────────
NUM_UNIVERSITIES = 25

# ── Academic fields ──────────────────────────────────────────
NUM_FIELDS = 4

# ── Professors ───────────────────────────────────────────────
PROFESSORS_PER_FIELD = 3

# ── Students ─────────────────────────────────────────────────
MALE_STUDENTS = 30
FEMALE_STUDENTS = 30

# ── Quota students ───────────────────────────────────────────
QUOTA_PERCENTAGE = 0.1

# ── Preferences ──────────────────────────────────────────────
MAX_STUDENT_PREFERENCES = 12
MAX_PROFESSOR_PREFERENCES = 60

# ── GPA generation ───────────────────────────────────────────
MIN_GPA = 12
MAX_GPA = 20

# ── Random seed ──────────────────────────────────────────────
RANDOM_SEED = 42

# ── Output ───────────────────────────────────────────────────
OUTPUT_DIR = "alg/webapp/datasets/new"
