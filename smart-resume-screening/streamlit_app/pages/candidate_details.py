"""Candidate details page: full profile, explainable results, resume preview."""
from __future__ import annotations

import streamlit as st

from components.api_client import APIClientError, get_candidate


def render() -> None:
    st.header("🔍 Candidate Details")

    candidate_id = st.session_state.get("selected_candidate_id")
    if not candidate_id:
        st.warning("No candidate selected. Go to **🏆 Candidate Ranking** and choose a candidate first.")
        return

    try:
        c = get_candidate(candidate_id)
    except APIClientError as exc:
        st.error(str(exc))
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(c["name"] or "Unknown Candidate")
        st.caption(c["filename"])
        st.write(f"📧 **Email:** {c['email'] or 'Not found'}")
        st.write(f"📞 **Phone:** {c['phone'] or 'Not found'}")
        st.write(f"🎓 **Education:** {c['education'].get('level', 'unknown').title()}"
                  + (f" in {c['education'].get('field')}" if c['education'].get('field') else ""))
        st.write(f"💼 **Experience:** {c['experience_years']} years")
    with col2:
        st.metric("Overall Match Score", f"{c['overall_score']}%")
        st.metric("Rank", f"#{c['rank']}")
        st.write("✅ Shortlisted" if c["shortlisted"] else "❌ Not shortlisted")

    st.divider()
    st.subheader("Component Scores")
    cs = c["component_scores"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Skill Match", f"{cs['skill_match']}%")
    m2.metric("Semantic Similarity", f"{cs['semantic_similarity']}%")
    m3.metric("Experience Match", f"{cs['experience_match']}%")
    m4.metric("Education Match", f"{cs['education_match']}%")

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("✅ Matched Skills")
        st.write(", ".join(c["matched_skills"]) or "None")
        st.subheader("🧩 All Detected Skills")
        st.write(", ".join(c["skills"]) or "None detected")
    with col4:
        st.subheader("❌ Missing Skills")
        st.write(", ".join(c["missing_skills"]) or "None")
        st.subheader("💼 Job / Project Entries")
        for entry in c["job_entries"][:8]:
            st.write(f"- {entry}")

    st.divider()
    st.subheader("🧠 Why this candidate scored the way it did")
    st.markdown("**Strengths:**")
    for s in c["strengths"]:
        st.write(f"- {s}")
    st.markdown("**Gaps:**")
    for g in c["gaps"]:
        st.write(f"- {g}")

    st.divider()
    st.subheader("📄 Resume Preview")
    st.text_area("Extracted text (preview)", value=c["resume_text_preview"], height=200, disabled=True)
