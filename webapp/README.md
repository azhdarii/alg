# Web Application for Algorithm Comparison

## Quick Start

### 1. Start the Server

```bash
cd D:\darsha\arshad\term2\algorithm\project
python -m uvicorn webapp.app:app --host 0.0.0.0 --port 8000
```

### 2. Open Browser

Go to: http://localhost:8000

---

## Features

### Single Run Tab
- Choose algorithm (Weighted Sum GA or NSGA-II)
- Configure parameters:
  - Population Size
  - Max Generations
  - Crossover Probability
  - Mutation Probability
  - Random Seed
- Click "Run Algorithm" to execute
- View results: satisfaction scores, fairness, assignments

### Compare Algorithms Tab
- Run both algorithms multiple times
- Configure number of runs (2-30)
- View statistical summary (Median, Q1, Q3)
- View Mann-Whitney U test results
- See which algorithm performs better

### About Tab
- Algorithm descriptions
- Objective explanations
- Statistical methodology

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web page |
| `/api/status` | GET | Server status |
| `/api/run-single` | POST | Run single algorithm |
| `/api/compare` | POST | Compare both algorithms |

---

## Built-in Dataset

The application uses the datasets from the project root:
- Students.xlsx (60 students)
- Professors.xlsx (12 professors)
- StudentPreferences.xlsx
- ProfessorPreferences.xlsx
- Universities.xlsx
- Fields.xlsx

---

## Troubleshooting

If the server doesn't start:
1. Make sure port 8000 is not in use
2. Check that all dependencies are installed:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```
3. Try killing all Python processes and restarting
