"""Recruiter dashboard: summary metrics, score distribution, skill match chart."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.api_client import APIClientError, get_dashboard, get_ranked_candidates


def render() -> None:
    st.header("📊 Recruiter Dashboard")

    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("No job description selected. Go to **Upload & Job Description** first.")
        return

    try:
        summary = get_dashboard(job_id)
        candidates = get_ranked_candidates(job_id)
    except APIClientError as exc:
        st.error(str(exc))
        return

    if summary["total_resumes"] == 0:
        st.info("No resumes processed yet for this job. Upload resumes to see the dashboard.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Resumes", summary["total_resumes"])
    col2.metric("Average Match Score", f"{summary['average_match_score']}%")
    top = summary.get("top_candidate") or {}
    col3.metric("Top Candidate", top.get("name") or "N/A", f"{top.get('score', 0)}%")
    col4.metric("Shortlist Threshold", f"{summary['shortlist_threshold']}%")

    col5, col6 = st.columns(2)
    col5.metric("✅ Shortlisted Candidates", summary["shortlisted_count"])
    col6.metric("⬇️ Below Threshold", summary["below_threshold_count"])

    st.divider()

    df = pd.DataFrame(
        [
            {
                "Name": c["name"] or c["filename"],
                "Overall Score": c["overall_score"],
                "Skill Match": c["component_scores"]["skill_match"],
                "Semantic Similarity": c["component_scores"]["semantic_similarity"],
                "Experience Match": c["component_scores"]["experience_match"],
                "Education Match": c["component_scores"]["education_match"],
                "Shortlisted": "Yes" if c["shortlisted"] else "No",
            }
            for c in candidates
        ]
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Score Distribution")
        fig1 = px.histogram(df, x="Overall Score", nbins=10, color="Shortlisted")
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Skill Match by Candidate")
        fig2 = px.bar(df.sort_values("Skill Match", ascending=True), x="Skill Match", y="Name", orientation="h")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Component Score Comparison")
    melted = df.melt(
        id_vars=["Name"],
        value_vars=["Skill Match", "Semantic Similarity", "Experience Match", "Education Match"],
        var_name="Component",
        value_name="Score",
    )
    fig3 = px.bar(melted, x="Name", y="Score", color="Component", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)
