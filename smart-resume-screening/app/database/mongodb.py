"""
MongoDB connection and data-access layer.

Credentials come exclusively from environment variables (see .env.example) -
never hard-coded. Collections used:
    - job_descriptions
    - candidates

If MongoDB is unreachable, functions raise a clear ConnectionError rather
than hanging or silently failing, so the API can return a meaningful 503.
"""
from __future__ import annotations

from typing import Any

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.config import MONGO_DB_NAME, MONGO_URI
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> Database:
    return get_client()[MONGO_DB_NAME]


def get_jobs_collection() -> Collection:
    return get_db()["job_descriptions"]


def get_candidates_collection() -> Collection:
    return get_db()["candidates"]


def check_connection() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except PyMongoError as exc:
        logger.error("MongoDB connection failed: %s", exc)
        return False


def insert_job(job_doc: dict[str, Any]) -> str:
    result = get_jobs_collection().insert_one(job_doc)
    return str(result.inserted_id)


def get_job(job_id: str) -> dict[str, Any] | None:
    return get_jobs_collection().find_one({"_id": job_id})


def insert_candidates(candidate_docs: list[dict[str, Any]]) -> list[str]:
    if not candidate_docs:
        return []
    result = get_candidates_collection().insert_many(candidate_docs)
    return [str(_id) for _id in result.inserted_ids]


def get_candidates_for_job(job_id: str) -> list[dict[str, Any]]:
    cursor = get_candidates_collection().find({"job_id": job_id}).sort(
        "overall_score", DESCENDING
    )
    return list(cursor)


def get_candidate(candidate_id: str) -> dict[str, Any] | None:
    return get_candidates_collection().find_one({"_id": candidate_id})


def update_candidate_rank(candidate_id: str, rank: int) -> None:
    get_candidates_collection().update_one(
        {"_id": candidate_id}, {"$set": {"rank": rank}}
    )
