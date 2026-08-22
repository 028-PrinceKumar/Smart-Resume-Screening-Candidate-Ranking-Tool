# Smart Resume Screening & Candidate Ranking Tool

An end-to-end AI/ML web application that helps recruiters upload multiple candidate
resumes and a job description, then automatically extracts candidate information,
computes an explainable match score, and ranks candidates from best to worst fit.

Built as a portfolio-grade project: real NLP/ML techniques (TF-IDF, cosine similarity,
Sentence-Transformer embeddings, rule-based extraction), a modular FastAPI backend,
a Streamlit recruiter dashboard, and MongoDB persistence. No paid APIs are used
anywhere in the pipeline.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [System Architecture](#system-architecture)
6. [Workflow](#workflow)
7. [Installation](#installation)
8. [Environment Variables](#environment-variables)
9. [How to Run](#how-to-run)
10. [API Endpoints](#api-endpoints)
11. [Screenshots](#screenshots)
12. [Example Output](#example-output)
13. [Testing](#testing)
14. [Docker Setup](#docker-setup)
15. [Future Improvements](#future-improvements)
16. [License](#license)

---

## Project Overview

Recruiters often receive hundreds of resumes per job opening and must manually
skim each one against a job description. This project automates that first pass:
it parses resumes (PDF/DOCX), extracts structured candidate data, compares each
resume against the job description using multiple NLP techniques, computes a
weighted, explainable match score, and presents recruiters with a ranked
dashboard instead of a pile of PDFs.

## Problem Statement

Manual resume screening is slow, inconsistent, and hard to justify. Two recruiters
reviewing the same stack of resumes will often shortlist different candidates.
This tool provides a repeatable, transparent, and configurable scoring process so
that:

- Every candidate is scored against the **same** criteria.
- The score is **explainable** — recruiters see *why* a candidate scored well or
  poorly, not just a number.
- Recruiters keep full control: scoring weights and the shortlist threshold are
  configurable, and the tool augments (not replaces) human judgment.

## Features

- **Job description intake** — paste a JD, auto-extract required skills,
  education requirement, and experience requirement.
- **Multi-resume upload** — PDF and DOCX, with file-size and format validation
  and per-file error isolation (one bad resume never crashes the batch).
- **Resume parsing** — text extraction, cleaning, and structured extraction of
  name, email, phone, skills, education, years of experience, and job/project
  entries.
- **Matching engine** — TF-IDF + cosine similarity, rule-based skill matching,
  and optional Sentence-Transformer semantic similarity (auto-fallback to
  TF-IDF if the embedding model isn't available).
- **Configurable weighted scoring** — Skill Match 40% / Semantic Similarity
  30% / Experience Match 20% / Education Match 10% by default, all
  configurable via environment variables.
- **Explainable results** — every candidate gets a "why they scored this way"
  breakdown: strengths and gaps, matched vs. missing skills.
- **Candidate ranking table** — sorted highest to lowest score.
- **Recruiter dashboard** — total resumes, average score, top candidate,
  shortlisted count, below-threshold count, score distribution chart, skill
  match chart, and configurable shortlist threshold (default 70%).
- **Candidate detail view** — full profile with resume text preview.

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Frontend   | Streamlit |
| Backend    | Python, FastAPI |
| ML / NLP   | NumPy, Pandas, Scikit-learn, NLTK, Sentence-Transformers |
| Database   | MongoDB |
| Resume Parsing | pdfplumber (PDF), docx2txt (DOCX) |
| Testing    | pytest |
| Containerization | Docker, docker-compose |

## System Architecture

```
smart-resume-screening/
│
├── app/                        # FastAPI backend
│   ├── main.py                 # App entry point
│   ├── config.py                # Central configuration (weights, thresholds, DB, skill DB)
│   ├── api/                     # REST route handlers
│   │   ├── resume_routes.py
│   │   ├── job_routes.py
│   │   └── ranking_routes.py
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── services/                # ML/NLP business logic (framework-agnostic)
│   │   ├── resume_parser.py
│   │   ├── text_preprocessor.py
│   │   ├── skill_extractor.py
│   │   ├── experience_extractor.py
│   │   ├── education_extractor.py
│   │   ├── similarity.py
│   │   ├── scoring.py
│   │   └── ranking.py
│   ├── database/
│   │   └── mongodb.py           # MongoDB connection & data-access layer
│   └── utils/
│       └── helpers.py
│
├── streamlit_app/               # Streamlit frontend
│   ├── app.py
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── upload.py
│   │   ├── candidates.py
│   │   └── candidate_details.py
│   └── components/
│       └── api_client.py        # HTTP client wrapping the FastAPI backend
│
├── data/
│   ├── sample_resumes/          # 3 sample DOCX resumes (strong/medium/weak fit)
│   └── sample_job_descriptions/ # 1 sample JD
│
├── tests/                       # pytest test suite
├── models/                      # (optional) cached ML model artifacts
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

The UI, REST API, ML/NLP logic, and database access are cleanly separated:
Streamlit never talks to MongoDB or scikit-learn directly — it only calls the
FastAPI REST API, which delegates business logic to the `services/` layer.

## Workflow

```
Job Description
   → Resume Upload
      → PDF/DOCX Text Extraction
         → Text Cleaning & Preprocessing
            → Skill / Education / Experience Extraction
               → Resume-JD Matching (TF-IDF + Semantic + Skills)
                  → Candidate Score (weighted)
                     → Candidate Ranking
                        → Recruiter Dashboard
                           → Candidate Details
```

## Installation

### Prerequisites

- Python 3.11+
- MongoDB (local install, or via Docker — see below)
- Git

### 1. Clone / unzip the project

```bash
cd smart-resume-screening
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> Note: `sentence-transformers` will download an open-source embedding model
> (`all-MiniLM-L6-v2`, ~90MB) the first time it runs. If you're offline or
> want to skip this, set `USE_SEMANTIC_MATCHING=false` in your `.env` — the
> system automatically falls back to TF-IDF-only similarity with no code
> changes required.

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | Database name | `resume_screening` |
| `API_HOST` / `API_PORT` | FastAPI bind host/port | `0.0.0.0` / `8000` |
| `API_BASE_URL` | Base URL the Streamlit app calls | `http://localhost:8000` |
| `MAX_FILE_SIZE_MB` | Max resume upload size | `5` |
| `WEIGHT_SKILL_MATCH` | Scoring weight | `0.40` |
| `WEIGHT_SEMANTIC_SIMILARITY` | Scoring weight | `0.30` |
| `WEIGHT_EXPERIENCE_MATCH` | Scoring weight | `0.20` |
| `WEIGHT_EDUCATION_MATCH` | Scoring weight | `0.10` |
| `SHORTLIST_THRESHOLD` | Score % to be auto-shortlisted | `70.0` |
| `SENTENCE_TRANSFORMER_MODEL` | Open-source embedding model name | `all-MiniLM-L6-v2` |
| `USE_SEMANTIC_MATCHING` | Enable/disable semantic scoring | `true` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

**No secrets are hard-coded anywhere** — the `.env` file is git-ignored, and
`.env.example` documents every variable without real credentials.

## How to Run

### Option A — Run locally (no Docker)

**1. Start MongoDB** (if not already running):

```bash
mongod --dbpath /path/to/your/data/db
```

**2. Run the FastAPI backend** (from the project root, with venv activated):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API docs are then available at `http://localhost:8000/docs`.

**3. Run the Streamlit frontend** (in a second terminal, venv activated):

```bash
streamlit run streamlit_app/app.py
```

Open `http://localhost:8501` in your browser.

**4. Try it immediately** using the built-in "Use sample JD" button on the
Upload page, and the sample resumes in `data/sample_resumes/`.

### Option B — Run with Docker (recommended)

```bash
docker compose up --build
```

This starts MongoDB, the FastAPI backend, and the Streamlit frontend together.

- Streamlit UI: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check (includes DB connectivity) |
| `POST` | `/api/jobs` | Create a job description; auto-extracts requirements |
| `GET` | `/api/jobs/{job_id}` | Fetch a job description |
| `POST` | `/api/resumes/upload/{job_id}` | Upload & process one or more resumes |
| `GET` | `/api/jobs/{job_id}/candidates` | Get ranked candidates for a job |
| `GET` | `/api/candidates/{candidate_id}` | Get full candidate details |
| `GET` | `/api/jobs/{job_id}/dashboard` | Get dashboard summary statistics |

Full interactive documentation (Swagger UI) is auto-generated by FastAPI at
`/docs` once the backend is running.

## Screenshots

> Run the app locally and add your own screenshots here:
> - `docs/screenshots/dashboard.png` — Recruiter dashboard
> - `docs/screenshots/upload.png` — Job description & resume upload
> - `docs/screenshots/ranking.png` — Candidate ranking table
> - `docs/screenshots/candidate_details.png` — Candidate detail view

## Example Output

Using the bundled sample job description and sample resumes:

```
Rank  Candidate       Overall Score   Skill Match   Semantic Similarity   Experience   Education
1     Amit Sharma     80.7%           100%          35.7%                 100%         100%
2     Priya Verma     56.6%           45.5%         28.0%                 100%         100%
3     Rohit Kumar     31.5%           0.0%          5.0%                  100%         100%
```

Amit Sharma's candidate detail view explains the score as:

- **Strengths:** Strong skill overlap (AWS, Docker, FastAPI, Machine Learning);
  meets or exceeds required experience level; meets required education level.
- **Gaps:** No significant gaps identified.

## Testing

```bash
pytest tests/ -v
```

The suite covers resume text extraction, skill extraction/matching, TF-IDF
similarity, weighted score calculation, ranking/tie-breaking, and API request
validation. Tests that require a live MongoDB connection degrade gracefully
(expecting a `503` if the DB isn't reachable) so the suite can run in CI
without a database.

## Docker Setup

```bash
docker compose up --build
```

Services defined in `docker-compose.yml`:

- `mongodb` — MongoDB 7 with a persistent named volume
- `api` — FastAPI backend (port 8000)
- `streamlit` — Streamlit frontend (port 8501)

Stop everything with `docker compose down` (add `-v` to also remove the
MongoDB data volume).

## Future Improvements

- Add authentication/authorization for recruiter accounts.
- Support bulk export of ranking results to CSV/PDF.
- Add resume anonymization mode for bias-reduced screening.
- Fine-tune a domain-specific embedding model for better semantic matching.
- Add OCR support for scanned/image-based resumes.
- Multi-language resume support.
- Deploy reference infrastructure (e.g. Kubernetes manifests / cloud IaC).

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

## Full Command Reference

```bash
# 1. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start MongoDB (local)
mongod --dbpath /path/to/data/db
# OR via Docker only:
docker run -d -p 27017:27017 --name resume_mongo mongo:7

# 4. Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Run Streamlit
streamlit run streamlit_app/app.py

# 6. Run tests
pytest tests/ -v

# 7. Build & run everything with Docker
docker compose up --build

# 8. Initialize a Git repository
git init

# 9. Create the first commit
git add .
git commit -m "Initial commit: Smart Resume Screening & Candidate Ranking Tool"

# 10. Connect the project to GitHub
git remote add origin https://github.com/<your-username>/smart-resume-screening.git
git branch -M main

# 11. Push the project to GitHub
git push -u origin main
```
