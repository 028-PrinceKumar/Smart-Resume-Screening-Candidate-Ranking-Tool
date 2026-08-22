"""Candidate ranking page: professional ranking table."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.api_client import APIClientError, get_ranked_candidates


def render() -> None:
    st.header("🏆 Candidate Ranking")

    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("No job description selected. Go to **Upload & Job Description** first.")
        return

    try:
        candidates = get_ranked_candidates(job_id)
    except APIClientError as exc:
        st.error(str(exc))
        return

    if not candidates:
        st.info("No resumes processed yet for this job.")
        return

    df = pd.DataFrame(
        [
            {
                "Rank": c["rank"],
                "Name": c["name"] or "Unknown",
                "Filename": c["filename"],
                "Overall Score (%)": c["overall_score"],
                "Skill Match (%)": c["component_scores"]["skill_match"],
                "Semantic Similarity (%)": c["component_scores"]["semantic_similarity"],
                "Experience Match (%)": c["component_scores"]["experience_match"],
                "Education Match (%)": c["component_scores"]["education_match"],
                "Shortlisted": "✅" if c["shortlisted"] else "❌",
                "id": c["id"],
            }
            for c in candidates
        ]
    )

    st.dataframe(
        df.drop(columns=["id"]).style.background_gradient(
            subset=["Overall Score (%)"], cmap="Greens"
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("View Candidate Details")
    name_options = {f"#{row.Rank} - {row.Name} ({row['Overall Score (%)']}%)": row.id for row in df.itertuples()}
    choice = st.selectbox("Select a candidate", list(name_options.keys()))
    if st.button("Open Candidate Details", type="primary"):
        st.session_state.selected_candidate_id = name_options[choice]
        st.info("Go to **🔍 Candidate Details** in the sidebar to view the full profile.")
