"""Upload page: create/select a job description and upload candidate resumes."""
from __future__ import annotations

import streamlit as st

from components.api_client import APIClientError, create_job, upload_resumes

SAMPLE_JD = """We are hiring a Data Scientist / Machine Learning Engineer.

Required Skills: Python, SQL, Machine Learning, Scikit-learn, Pandas, NumPy
Preferred Skills: TensorFlow, PyTorch, FastAPI, Docker, AWS

Education: Bachelor's degree in Computer Science, Data Science, or a related field.
Experience: 3+ years of experience in data science or machine learning roles.

Responsibilities:
- Build and deploy machine learning models
- Analyze large datasets and extract actionable insights
- Collaborate with engineering teams to productionize models
- Communicate findings to non-technical stakeholders
"""


def render() -> None:
    st.header("📤 Job Description & Resume Upload")

    st.subheader("1. Job Description")
    col1, col2 = st.columns([3, 1])
    with col1:
        title = st.text_input("Job Title", value="Data Scientist")
    with col2:
        use_sample = st.button("Use sample JD")

    description = st.text_area(
        "Job Description",
        value=SAMPLE_JD if use_sample else "",
        height=280,
        placeholder="Paste the full job description here...",
    )

    if st.button("Create / Update Job Description", type="primary"):
        if not title.strip() or not description.strip():
            st.error("Please provide both a job title and a description.")
        else:
            try:
                job = create_job(title, description)
                st.session_state.job_id = job["id"]
                st.success(f"Job description saved (ID: {job['id']})")
                with st.expander("Extracted requirements"):
                    st.write("**Required skills:**", ", ".join(job["required_skills"]) or "None detected")
                    st.write("**Education requirement:**", job["education_requirement"].get("level", "unknown"))
                    st.write("**Experience requirement (years):**", job["experience_requirement_years"])
            except APIClientError as exc:
                st.error(str(exc))

    st.divider()
    st.subheader("2. Upload Resumes")

    if not st.session_state.get("job_id"):
        st.warning("Create a job description above before uploading resumes.")
        return

    files = st.file_uploader(
        "Upload candidate resumes (PDF or DOCX, multiple allowed)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

    if st.button("Process Resumes", type="primary", disabled=not files):
        with st.spinner(f"Extracting, matching, and scoring {len(files)} resume(s)..."):
            payload = [(f.name, f.getvalue(), f.type or "application/octet-stream") for f in files]
            try:
                result = upload_resumes(st.session_state.job_id, payload)
            except APIClientError as exc:
                st.error(str(exc))
                return

        st.success(f"Processed {len(result['processed'])} resume(s) successfully.")
        if result["errors"]:
            st.warning(f"{len(result['errors'])} file(s) could not be processed:")
            for err in result["errors"]:
                st.write(f"- **{err['filename']}**: {err['error']}")

        if result["processed"]:
            st.info("Go to **🏆 Candidate Ranking** to view results.")
