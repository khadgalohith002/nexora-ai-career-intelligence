import os
import sys

# Test imports
try:
    from src.resume_parser import extract_resume_text
    from src.text_preprocessor import preprocess_resume
    from src.information_extractor import extract_contact_information
    from src.skill_extractor import extract_skills
    from src.section_extractor import extract_sections
    from src.job_analyzer import analyze_job_description, compare_skills
    from src.matching_engine import calculate_text_similarity
    from src.job_classifier import classify_job
    from src.scoring_engine import calculate_overall_score, get_score_label
    from src.resume_quality import calculate_resume_quality, get_quality_label
    from src.candidate_level import detect_candidate_level
    from src.ai_feedback import generate_ai_feedback
    from src.ats_optimizer import generate_ats_suggestions
    from src.interview_generator import generate_interview_questions
    from src.database import init_db
    from src.job_service import get_jobs, calculate_resume_match
    from src.ui_intro import render_cinematic_intro
    from src.intro_assets import BAT_WING_LEFT_B64, BAT_AI_EMBLEM_B64, HERO_BAT_BG_B64
    print("ALL MODULE IMPORTS SUCCESSFUL!")
except Exception as e:
    print(f"IMPORT ERROR: {type(e).__name__}: {e}")
