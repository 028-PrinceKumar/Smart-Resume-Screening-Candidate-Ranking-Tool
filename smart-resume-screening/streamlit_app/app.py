"""
Smart Resume Screening & Candidate Ranking Tool - Streamlit frontend entry point.

Run with: streamlit run streamlit_app/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from components.api_client import check_health  # noqa: E402
from pages import candidate_details, candidates, dashboard, upload  # noqa: E402

st.set_page_config(
    page_title="Smart Resume Screening",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = None

PAGES = {
    "📊 Dashboard": dashboard,
    "📤 Upload & Job Description": upload,
    "🏆 Candidate Ranking": candidates,
    "🔍 Candidate Details": candidate_details,
}


def main() -> None:
    with st.sidebar:
        st.title("🧭 Resume Screening")
        st.caption("AI-powered candidate ranking")

        if check_health():
            st.success("Backend connected")
        else:
            st.error("Backend unreachable - start the FastAPI server (see README).")

        st.divider()
        choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

        st.divider()
        if st.session_state.job_id:
            st.info(f"Active Job ID:\n`{st.session_state.job_id}`")
        else:
            st.warning("No job description created yet.")

    PAGES[choice].render()


if __name__ == "__main__":
    main()
