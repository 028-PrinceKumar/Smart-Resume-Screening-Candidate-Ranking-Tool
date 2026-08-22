# Smart-Resume-Screening-Candidate-Ranking-Tool
An end-to-end AI/ML web application that helps recruiters upload multiple candidate resumes and a job description, then automatically extracts candidate information, computes an explainable match score, and ranks candidates from best to worst fit.

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


