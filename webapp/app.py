"""FastAPI web application for algorithm comparison."""

import os
import sys
import json
import time
import shutil
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Configuration
from src.algorithms.weighted_sum import WeightedSumGA, WeightedSumConfig
from src.algorithms.nsga2 import NSGA2, NSGA2Config
from src.comparison.metrics import RunMetrics, ComparisonMetrics
from src.comparison.statistics import StatisticalSummary
from src.comparison.statistical_test import MannWhitneyTest
from src.comparison.visualization import ComparisonVisualizer
from src.comparison.report import ComparisonReport

app = FastAPI(title="Student-Supervisor Assignment Optimizer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "output"
DATASETS_DIR = Path(__file__).parent / "datasets"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Current active dataset
active_dataset = {"name": "default", "path": str(Path(__file__).parent.parent)}


def get_config_for_dataset(dataset_path: str) -> Configuration:
    """Get configuration for a specific dataset."""
    config = Configuration()
    config.algorithm.population_size = 50
    config.algorithm.max_generations = 100
    config.algorithm.crossover_probability = 0.8
    config.algorithm.mutation_probability = 0.1
    config.algorithm.random_seed = 42

    path = Path(dataset_path)
    config.data.students_file = str(path / "Students.xlsx")
    config.data.professors_file = str(path / "Professors.xlsx")
    config.data.student_preferences_file = str(path / "StudentPreferences.xlsx")
    config.data.professor_preferences_file = str(path / "ProfessorPreferences.xlsx")
    config.data.universities_file = str(path / "Universities.xlsx")
    config.data.fields_file = str(path / "Fields.xlsx")

    return config


def get_default_config() -> Configuration:
    """Get default configuration with active dataset paths."""
    return get_config_for_dataset(active_dataset["path"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main page."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/status")
async def get_status():
    """Get server status."""
    return {"status": "running", "timestamp": datetime.now().isoformat()}


# ==================== Dataset Management ====================

@app.get("/api/datasets")
async def list_datasets():
    """List all available datasets."""
    datasets = []

    # Check for pre-defined datasets
    if DATASETS_DIR.exists():
        for d in DATASETS_DIR.iterdir():
            if d.is_dir() and (d / "Students.xlsx").exists():
                students = pd.read_excel(d / "Students.xlsx")
                profs = pd.read_excel(d / "Professors.xlsx")
                datasets.append({
                    "name": d.name,
                    "path": str(d),
                    "num_students": len(students),
                    "num_professors": len(profs),
                    "type": "predefined",
                    "active": d.name == active_dataset["name"]
                })

    # Check for default dataset
    default_path = Path(__file__).parent.parent
    if (default_path / "Students.xlsx").exists():
        students = pd.read_excel(default_path / "Students.xlsx")
        profs = pd.read_excel(default_path / "Professors.xlsx")
        datasets.append({
            "name": "default (60 students)",
            "path": str(default_path),
            "num_students": len(students),
            "num_professors": len(profs),
            "type": "default",
            "active": active_dataset["name"] == "default"
        })

    # Check for uploaded datasets
    if UPLOAD_DIR.exists():
        for d in UPLOAD_DIR.iterdir():
            if d.is_dir() and (d / "Students.xlsx").exists():
                students = pd.read_excel(d / "Students.xlsx")
                profs = pd.read_excel(d / "Professors.xlsx")
                datasets.append({
                    "name": d.name,
                    "path": str(d),
                    "num_students": len(students),
                    "num_professors": len(profs),
                    "type": "uploaded",
                    "active": d.name == active_dataset["name"]
                })

    return {"datasets": datasets, "active": active_dataset["name"]}


@app.post("/api/datasets/activate")
async def activate_dataset(name: str = Form(...), path: str = Form(...)):
    """Set a dataset as active."""
    global active_dataset
    active_dataset = {"name": name, "path": path}
    return {"message": f"Dataset '{name}' activated", "active": active_dataset["name"]}


@app.post("/api/datasets/upload")
async def upload_dataset(
    name: str = Form(...),
    students: UploadFile = File(...),
    professors: UploadFile = File(...),
    student_preferences: UploadFile = File(...),
    professor_preferences: UploadFile = File(...),
    universities: UploadFile = File(None),
    fields: UploadFile = File(None),
):
    """Upload a custom dataset."""
    # Create dataset directory
    dataset_dir = UPLOAD_DIR / name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    async def save_file(upload_file: UploadFile, filename: str):
        content = await upload_file.read()
        with open(dataset_dir / filename, "wb") as f:
            f.write(content)

    await save_file(students, "Students.xlsx")
    await save_file(professors, "Professors.xlsx")
    await save_file(student_preferences, "StudentPreferences.xlsx")
    await save_file(professor_preferences, "ProfessorPreferences.xlsx")

    if universities:
        await save_file(universities, "Universities.xlsx")
    if fields:
        await save_file(fields, "Fields.xlsx")

    # Create default files if not provided
    if not (dataset_dir / "Universities.xlsx").exists():
        default_unis = pd.read_excel(Path(__file__).parent.parent / "Universities.xlsx")
        default_unis.to_excel(dataset_dir / "Universities.xlsx", index=False)

    if not (dataset_dir / "Fields.xlsx").exists():
        default_fields = pd.read_excel(Path(__file__).parent.parent / "Fields.xlsx")
        default_fields.to_excel(dataset_dir / "Fields.xlsx", index=False)

    # Validate
    try:
        students_df = pd.read_excel(dataset_dir / "Students.xlsx")
        profs_df = pd.read_excel(dataset_dir / "Professors.xlsx")

        return {
            "message": f"Dataset '{name}' uploaded successfully",
            "num_students": len(students_df),
            "num_professors": len(profs_df),
            "path": str(dataset_dir)
        }
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}


@app.delete("/api/datasets/{name}")
async def delete_dataset(name: str):
    """Delete an uploaded dataset."""
    if name == "default":
        return {"error": "Cannot delete default dataset"}

    dataset_dir = UPLOAD_DIR / name
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
        return {"message": f"Dataset '{name}' deleted"}

    return {"error": f"Dataset '{name}' not found"}


@app.get("/api/datasets/{name}/preview")
async def preview_dataset(name: str):
    """Preview dataset contents."""
    # Find dataset path
    if name == "default":
        dataset_path = Path(__file__).parent.parent
    elif (DATASETS_DIR / name).exists():
        dataset_path = DATASETS_DIR / name
    elif (UPLOAD_DIR / name).exists():
        dataset_path = UPLOAD_DIR / name
    else:
        return {"error": f"Dataset '{name}' not found"}

    try:
        students = pd.read_excel(dataset_path / "Students.xlsx")
        profs = pd.read_excel(dataset_path / "Professors.xlsx")

        return {
            "name": name,
            "students": {
                "columns": students.columns.tolist(),
                "sample": students.head(5).to_dict(orient="records"),
                "total": len(students)
            },
            "professors": {
                "columns": profs.columns.tolist(),
                "sample": profs.head(5).to_dict(orient="records"),
                "total": len(profs)
            }
        }
    except Exception as e:
        return {"error": str(e)}


def parse_penalty_value(value: str) -> float:
    """Parse penalty value, supporting 'inf' for hard constraints."""
    if value.lower() in ('inf', 'infinity'):
        return float('inf')
    try:
        return float(value)
    except (ValueError, TypeError):
        return 10.0


@app.post("/api/run-single")
async def run_single_algorithm(
    algorithm: str = Form(...),
    population_size: int = Form(50),
    max_generations: int = Form(100),
    crossover_prob: float = Form(0.8),
    mutation_prob: float = Form(0.1),
    tournament_size: int = Form(3),
    elite_size: int = Form(2),
    seed: int = Form(42),
    # Weighted Sum specific parameters
    weight_student: float = Form(0.4),
    weight_professor: float = Form(0.4),
    weight_fairness: float = Form(0.2),
    penalty_capacity: str = Form("10"),
    penalty_field: str = Form("5"),
):
    """Run a single algorithm and return results."""
    try:
        config = get_default_config()
        config.algorithm.population_size = population_size
        config.algorithm.max_generations = max_generations
        config.algorithm.crossover_probability = crossover_prob
        config.algorithm.mutation_probability = mutation_prob
        config.algorithm.random_seed = seed

        # Redirect output
        config.logging.log_to_console = False

        # Parse penalty values (support "inf" for hard constraints)
        cap_penalty = parse_penalty_value(penalty_capacity)
        field_penalty = parse_penalty_value(penalty_field)

        start_time = time.time()

        if algorithm == "weighted_sum":
            # Normalize weights to sum to 1.0
            total_weight = weight_student + weight_professor + weight_fairness
            if total_weight > 0:
                weights = [weight_student / total_weight, weight_professor / total_weight, weight_fairness / total_weight]
            else:
                weights = [0.4, 0.4, 0.2]

            # For hard constraints (inf), use a very large penalty instead
            constraint_weight = 1.0
            if cap_penalty == float('inf') or field_penalty == float('inf'):
                # Use large penalty multiplier for hard constraints
                config.penalty.capacity_penalty_per_student = 1e6 if cap_penalty == float('inf') else cap_penalty
                config.penalty.field_mismatch_penalty = 1e6 if field_penalty == float('inf') else field_penalty
                constraint_weight = 0.001  # Small weight to avoid numerical issues
            else:
                config.penalty.capacity_penalty_per_student = cap_penalty
                config.penalty.field_mismatch_penalty = field_penalty
                constraint_weight = 0.01

            ws_config = WeightedSumConfig(
                weights=weights,
                constraint_weight=constraint_weight,
                preserve_elitism=elite_size,
                tournament_size=tournament_size,
            )
            ga = WeightedSumGA(config=config, ws_config=ws_config)
            ga.run()
            best = ga.get_best_solution()

            if best is None:
                return {"error": "No solution found"}

            return {
                "algorithm": "Weighted Sum GA",
                "execution_time": round(time.time() - start_time, 2),
                "student_satisfaction": round(best.objectives.student_satisfaction, 4),
                "professor_satisfaction": round(best.objectives.professor_satisfaction, 4),
                "fairness": round(best.objectives.fairness, 4),
                "capacity_penalty": round(best.constraints.capacity_violation, 2),
                "field_penalty": best.constraints.field_mismatch_count,
                "fitness": round(best.fitness, 6) if best.fitness else None,
                "assignments": best.to_assignment_dict(),
                "weights": weights,
                "penalty_capacity": cap_penalty if cap_penalty != float('inf') else "inf",
                "penalty_field": field_penalty if field_penalty != float('inf') else "inf",
            }

        elif algorithm == "nsga2":
            nsga2_config = NSGA2Config(
                tournament_size=tournament_size,
                use_constraint_dominance=True,
            )
            ga = NSGA2(config=config, nsga2_config=nsga2_config)
            ga.run()
            pareto_front = ga.get_pareto_front()
            objectives = ga.get_pareto_front_objectives()

            if not pareto_front:
                return {"error": "No Pareto front found"}

            # Get best values
            best_student = max(c.objectives.student_satisfaction for c in pareto_front)
            best_professor = max(c.objectives.professor_satisfaction for c in pareto_front)
            best_fairness = min(c.objectives.fairness for c in pareto_front)

            # Sanitize objectives for JSON (replace inf with large number)
            sanitized_objectives = []
            for obj in objectives[:20]:
                sanitized = {
                    "student_satisfaction": obj["student_satisfaction"],
                    "professor_satisfaction": obj["professor_satisfaction"],
                    "fairness": obj["fairness"],
                    "rank": obj["rank"],
                    "crowding_distance": 999.0 if obj["crowding_distance"] == float("inf") else obj["crowding_distance"],
                }
                sanitized_objectives.append(sanitized)

            return {
                "algorithm": "NSGA-II",
                "execution_time": round(time.time() - start_time, 2),
                "student_satisfaction": round(best_student, 4),
                "professor_satisfaction": round(best_professor, 4),
                "fairness": round(best_fairness, 4),
                "num_pareto_solutions": len(pareto_front),
                "pareto_front": sanitized_objectives,
            }

        else:
            return {"error": f"Unknown algorithm: {algorithm}"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/compare")
async def compare_algorithms(
    num_runs: int = Form(5),
    population_size: int = Form(50),
    max_generations: int = Form(100),
    crossover_prob: float = Form(0.8),
    mutation_prob: float = Form(0.1),
    tournament_size: int = Form(3),
    elite_size: int = Form(2),
    # Weighted Sum specific parameters
    weight_student: float = Form(0.4),
    weight_professor: float = Form(0.4),
    weight_fairness: float = Form(0.2),
    penalty_capacity: str = Form("10"),
    penalty_field: str = Form("5"),
):
    """Run comparison between both algorithms."""
    try:
        config = get_default_config()
        config.algorithm.population_size = population_size
        config.algorithm.max_generations = max_generations
        config.algorithm.crossover_probability = crossover_prob
        config.algorithm.mutation_probability = mutation_prob
        config.logging.log_to_console = False

        # Parse penalty values
        cap_penalty = parse_penalty_value(penalty_capacity)
        field_penalty = parse_penalty_value(penalty_field)

        # Normalize weights
        total_weight = weight_student + weight_professor + weight_fairness
        if total_weight > 0:
            weights = [weight_student / total_weight, weight_professor / total_weight, weight_fairness / total_weight]
        else:
            weights = [0.4, 0.4, 0.2]

        # Setup penalty config
        if cap_penalty == float('inf') or field_penalty == float('inf'):
            config.penalty.capacity_penalty_per_student = 1e6 if cap_penalty == float('inf') else cap_penalty
            config.penalty.field_mismatch_penalty = 1e6 if field_penalty == float('inf') else field_penalty
            constraint_weight = 0.001
        else:
            config.penalty.capacity_penalty_per_student = cap_penalty
            config.penalty.field_mismatch_penalty = field_penalty
            constraint_weight = 0.01

        # Run Weighted Sum
        ws_results = []
        nsga2_results = []

        for run_id in range(num_runs):
            seed = run_id + 1

            # Weighted Sum
            ws_config_run = Configuration()
            ws_config_run.algorithm.population_size = population_size
            ws_config_run.algorithm.max_generations = max_generations
            ws_config_run.algorithm.crossover_probability = crossover_prob
            ws_config_run.algorithm.mutation_probability = mutation_prob
            ws_config_run.algorithm.random_seed = seed
            ws_config_run.data = config.data
            ws_config_run.penalty = config.penalty
            ws_config_run.logging.log_to_console = False
            ws_config_run.logging.log_interval = max_generations

            ws_algo_config = WeightedSumConfig(
                weights=weights,
                constraint_weight=constraint_weight,
                preserve_elitism=elite_size,
                tournament_size=tournament_size,
            )

            start = time.time()
            ga_ws = WeightedSumGA(config=ws_config_run, ws_config=ws_algo_config)
            ga_ws.run()
            ws_time = time.time() - start

            best = ga_ws.get_best_solution()
            if best:
                ws_results.append({
                    "run": run_id + 1,
                    "student_satisfaction": best.objectives.student_satisfaction,
                    "professor_satisfaction": best.objectives.professor_satisfaction,
                    "fairness": best.objectives.fairness,
                    "execution_time": ws_time,
                })

            # NSGA-II
            nsga2_config_run = Configuration()
            nsga2_config_run.algorithm.population_size = population_size
            nsga2_config_run.algorithm.max_generations = max_generations
            nsga2_config_run.algorithm.crossover_probability = crossover_prob
            nsga2_config_run.algorithm.mutation_probability = mutation_prob
            nsga2_config_run.algorithm.random_seed = seed
            nsga2_config_run.data = config.data
            nsga2_config_run.penalty = config.penalty
            nsga2_config_run.logging.log_to_console = False
            nsga2_config_run.logging.log_interval = max_generations

            nsga2_algo_config = NSGA2Config(
                tournament_size=tournament_size,
                use_constraint_dominance=True,
            )

            start = time.time()
            ga_nsga2 = NSGA2(config=nsga2_config_run, nsga2_config=nsga2_algo_config)
            ga_nsga2.run()
            nsga2_time = time.time() - start

            pareto = ga_nsga2.get_pareto_front()
            if pareto:
                nsga2_results.append({
                    "run": run_id + 1,
                    "student_satisfaction": max(c.objectives.student_satisfaction for c in pareto),
                    "professor_satisfaction": max(c.objectives.professor_satisfaction for c in pareto),
                    "fairness": min(c.objectives.fairness for c in pareto),
                    "execution_time": nsga2_time,
                    "num_pareto_solutions": len(pareto),
                })

        # Compute statistics
        stats_calc = StatisticalSummary()

        ws_stats = {}
        nsga2_stats = {}
        for metric in ["student_satisfaction", "professor_satisfaction", "fairness", "execution_time"]:
            ws_values = [r[metric] for r in ws_results]
            nsga2_values = [r[metric] for r in nsga2_results]
            ws_stats[metric] = stats_calc.compute(ws_values, metric)
            nsga2_stats[metric] = stats_calc.compute(nsga2_values, metric)

        # Statistical tests
        test = MannWhitneyTest(alpha=0.05)
        test_results = []
        for metric in ["student_satisfaction", "professor_satisfaction", "fairness", "execution_time"]:
            ws_values = [r[metric] for r in ws_results]
            nsga2_values = [r[metric] for r in nsga2_results]
            result = test.test(ws_values, nsga2_values, metric, "Weighted Sum", "NSGA-II")
            test_results.append({
                "metric": metric,
                "u_statistic": round(result.u_statistic, 2),
                "p_value": round(result.p_value, 4),
                "significant": result.significant,
                "ws_median": round(result.group1_median, 4),
                "nsga2_median": round(result.group2_median, 4),
            })

        return {
            "num_runs": num_runs,
            "weighted_sum": {
                "runs": ws_results,
                "stats": {k: {"median": round(v.median, 4), "q1": round(v.q1, 4), "q3": round(v.q3, 4)}
                         for k, v in ws_stats.items()},
            },
            "nsga2": {
                "runs": nsga2_results,
                "stats": {k: {"median": round(v.median, 4), "q1": round(v.q1, 4), "q3": round(v.q3, 4)}
                         for k, v in nsga2_stats.items()},
            },
            "statistical_tests": test_results,
        }

    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}


@app.get("/api/sample-assignments")
async def get_sample_assignments():
    """Get sample assignment results for demonstration."""
    return {
        "assignments": {
            "S01": "P02", "S02": "P01", "S03": "P02", "S04": "P01",
            "S05": "P03", "S06": "P01", "S07": "P02", "S08": "P02",
            "S09": "P03", "S10": "P03", "S11": "P01", "S12": "P01",
            "S13": "P01", "S14": "P03", "S15": "P02",
            "S16": "P04", "S17": "P05", "S18": "P04", "S19": "P04",
            "S20": "P04", "S21": "P06", "S22": "P05", "S23": "P05",
            "S24": "P04", "S25": "P04", "S26": "P06", "S27": "P05",
            "S28": "P06", "S29": "P04", "S30": "P06",
        }
    }


# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
