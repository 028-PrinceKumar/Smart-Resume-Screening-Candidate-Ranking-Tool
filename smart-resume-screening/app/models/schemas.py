"""Pydantic schemas for API request/response validation and MongoDB documents."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., description="Job title, e.g. 'Data Scientist'")
    description: str = Field(..., description="Full job description text")


class JobDescriptionOut(BaseModel):
    id: str
    title: str
    description: str
    required_skills: list[str]
    education_requirement: dict
    experience_requirement_years: float
    created_at: datetime


class ComponentScoresOut(BaseModel):
    skill_match: float
    semantic_similarity: float
    experience_match: float
    education_match: float


class CandidateOut(BaseModel):
    id: str
    job_id: str
    filename: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = []
    education: dict = {}
    experience_years: float = 0.0
    job_entries: list[str] = []
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    overall_score: float = 0.0
    component_scores: ComponentScoresOut
    rank: Optional[int] = None
    shortlisted: bool = False
    strengths: list[str] = []
    gaps: list[str] = []
    resume_text_preview: str = ""
    created_at: datetime


class UploadErrorOut(BaseModel):
    filename: str
    error: str


class UploadResponse(BaseModel):
    job_id: str
    processed: list[CandidateOut]
    errors: list[UploadErrorOut]


class DashboardSummaryOut(BaseModel):
    total_resumes: int
    average_match_score: float
    top_candidate: Optional[dict] = None
    shortlisted_count: int
    below_threshold_count: int
    shortlist_threshold: float
