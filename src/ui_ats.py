import streamlit as st


def show_ats(
    skill_match,
    resume_job_similarity,
    matched_skills,
    missing_skills,
    job_category,
    job_confidence,
    overall_score,
    score_label,
    score_result,
    resume_quality_score,
    quality_label,
    quality_checks,
):
    st.header("🎯 ATS Dashboard")
