"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import job_routes, ranking_routes, resume_routes
from app.database.mongodb import check_connection
from app.utils.helpers import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if check_connection():
        logger.info("Connected to MongoDB successfully.")
    else:
        logger.warning(
            "Could not connect to MongoDB at startup. "
            "Make sure it is running (see README / docker-compose)."
        )
    yield


app = FastAPI(
    title="Smart Resume Screening & Candidate Ranking API",
    description=(
        "REST API for uploading job descriptions and resumes, extracting "
        "candidate information, computing match scores, and ranking candidates."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_routes.router)
app.include_router(resume_routes.router)
app.include_router(ranking_routes.router)


@app.get("/", tags=["Health"])
def root() -> dict:
    return {"status": "ok", "service": "smart-resume-screening-api"}


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "healthy", "database_connected": check_connection()}
