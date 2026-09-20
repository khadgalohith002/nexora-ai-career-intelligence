
import sqlite3
import requests
import textwrap
import os
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# ============================================================
# BACKEND IMPORTS
# ============================================================

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
from src.ai_service import rewrite_resume
from src.pdf_generator import generate_analysis_pdf
from src.database import init_db
from src.job_service import get_jobs, calculate_resume_match, infer_target_role
from src.ui_intro import render_cinematic_intro
from src.ai_review_engine import generate_personalized_ai_review
from src.ui_ai_review import render_ai_review_tab
from src.ui_interview import render_interview_tab
from src.ui_skill_gap import render_skill_gap_tab
from src.ui_career_roadmap import render_career_roadmap_tab
from src.ui_job_vacancies import render_job_vacancies_tab
import importlib
import src.ai_service
import src.ui_resume_rewrite

try:
    from src.ui_resume_rewrite import render_resume_rewrite_tab
except ImportError:
    importlib.reload(src.ai_service)
    importlib.reload(src.ui_resume_rewrite)
    from src.ui_resume_rewrite import render_resume_rewrite_tab
# AI Assets & Icons managed directly via inline SVG / CSS



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NEXORA | AI Career Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CINEMATIC INTRO SCREEN (STARTUP ONLY)
# ============================================================

if "intro_seen" not in st.session_state:
    st.session_state.intro_seen = False

if not st.session_state.intro_seen:
    render_cinematic_intro()
    st.stop()


# ============================================================
# DATABASE
# ============================================================

init_db()


def save_analysis(filename, ats_score, quality_score, job_category):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resume_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            ats_score REAL,
            quality_score REAL,
            job_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO resume_history
        (filename, ats_score, quality_score, job_category)
        VALUES (?, ?, ?, ?)
        """,
        (
            filename,
            ats_score,
            quality_score,
            job_category,
        ),
    )

    conn.commit()
    conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "analysis" not in st.session_state:
    st.session_state.analysis = {}

if "rewritten_resume" not in st.session_state:
    st.session_state.rewritten_resume = None

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "📊 Dashboard"

if "job_results" not in st.session_state:
    st.session_state["job_results"] = []

if "job_search_performed" not in st.session_state:
    st.session_state["job_search_performed"] = False


@st.cache_data
def create_gauge_chart(score):
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(score),
            number={
                "suffix": "%",
                "font": {
                    "size": 42,
                    "color": "#f8fafc",
                },
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#64748b",
                },
                "bar": {
                    "color": "#d21f2b",
                },
                "bgcolor": "#1a2330",
                "borderwidth": 0,
            },
        )
    )

    gauge.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
    )

    return gauge


# ============================================================
# CINEMATIC RED / DARK UI
# ============================================================

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {{
        --bg: #040305;
        --panel: rgba(16, 12, 14, 0.92);
        --panel-2: rgba(26, 14, 17, 0.95);
        --line: rgba(255,255,255,0.09);
        --muted: #9b9193;
        --text: #f6f1f1;
        --red: #d21f2b;
        --red-bright: #ff4652;
    }}

    .stApp {{
        background:
            radial-gradient(circle at 78% 7%, rgba(188, 9, 26, 0.22), transparent 28%),
            radial-gradient(circle at 12% 30%, rgba(112, 8, 19, 0.18), transparent 26%),
            linear-gradient(180deg, #050406 0%, #030204 55%, #060406 100%);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }}

    .block-container {{
        max-width: 1380px;
        padding: 1.2rem 2rem 4rem;
    }}

    #MainMenu, footer {{ visibility: hidden; }}
    header {{ background: transparent !important; }}

    /* HEADER */
    .app-header {{
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 22px 0 18px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 0;
    }}

    .brand-wrap {{ display:flex; align-items:center; gap:14px; }}
    .brand-mark {{
        width: 46px; height: 30px;
        display:flex; align-items:center; justify-content:center;
        color:#ff4b55; font-size:24px;
        filter: drop-shadow(0 0 12px rgba(255,35,50,.45));
    }}

    .brand-title {{
        font-family:'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #fff;
        line-height: 1.05;
    }}
    .brand-title span {{ color: #e1333d; }}
    .brand-subtitle {{
        color: #8f8587;
        font-size: 10px;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        margin-top: 7px;
    }}
    .system-status {{
        display:flex; align-items:center; gap:9px;
        color:#c9bfc1; font-size:10px; letter-spacing:1.8px;
        font-weight:700;
    }}
    .status-dot {{
        width:7px; height:7px; border-radius:50%; background:#f03542;
        box-shadow:0 0 0 4px rgba(240,53,66,.12), 0 0 14px rgba(240,53,66,.9);
    }}

    .command-nav {{
        display:flex; gap:28px; align-items:center;
        padding: 15px 0 18px;
        border-bottom:1px solid var(--line);
        color:#817779; font-size:10px; font-weight:700;
        letter-spacing:1.4px; text-transform:uppercase;
        overflow-x:auto;
    }}
    .command-item {{ white-space:nowrap; }}
    .command-item.active {{ color:#fff; position:relative; }}
    .command-item.active:after {{
        content:""; position:absolute; left:0; right:0; bottom:-19px;
        height:2px; background:#d91f2c; box-shadow:0 0 10px rgba(217,31,44,.8);
    }}

    /* KEYFRAME ANIMATIONS (60FPS ACCURATE & FAST) */
    @keyframes batFadeInUp {{
        0% {{ opacity: 0; transform: translateY(14px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes batGlowPulse {{
        0% {{ box-shadow: 0 0 15px rgba(255, 45, 60, 0.2); }}
        50% {{ box-shadow: 0 0 35px rgba(255, 45, 60, 0.55), inset 0 0 15px rgba(255, 45, 60, 0.15); }}
        100% {{ box-shadow: 0 0 15px rgba(255, 45, 60, 0.2); }}
    }}

    @keyframes batShimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    @keyframes batIconFloat {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-4px) rotate(2deg); }}
        100% {{ transform: translateY(0px) rotate(0deg); }}
    }}

    @keyframes batStatusPulse {{
        0% {{ opacity: 0.6; transform: scale(0.96); }}
        50% {{ opacity: 1; transform: scale(1.04); }}
        100% {{ opacity: 0.6; transform: scale(0.96); }}
    }}

    /* ENHANCED ANIMATED ELEMENTS */
    .hero {{
        margin: 34px 0 22px;
        min-height: 320px;
        padding: 52px 58px;
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 8px;
        overflow:hidden;
        position:relative;
        background:
            radial-gradient(ellipse at 85% 20%, rgba(255,45,60,0.18) 0%, transparent 60%),
            linear-gradient(135deg, rgba(12,6,8,.98) 0%, rgba(20,9,13,.95) 50%, rgba(8,4,6,.99) 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 35px 80px rgba(0,0,0,.45);
        animation: batFadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        will-change: transform, opacity;
    }}
    .hero:before {{
        content:""; position:absolute; inset:0;
        background: linear-gradient(115deg, transparent 0 50%, rgba(255,35,45,.06) 50.2%, transparent 51%);
        pointer-events:none;
    }}
    .hero:after {{
        content:""; position:absolute; width:380px; height:380px; right:-80px; top:-90px;
        border-radius:50%; border:1px solid rgba(255,67,79,.14);
        box-shadow: 0 0 0 45px rgba(255,40,55,.025), 0 0 0 90px rgba(255,40,55,.018);
        animation: batStatusPulse 4s ease-in-out infinite;
        will-change: transform, opacity;
    }}
    .hero-eyebrow {{
        position:relative; z-index:1;
        display:inline-flex; align-items:center; gap:10px;
        color:#ff4b58; font-size:10px; font-weight:800;
        letter-spacing:2.5px; text-transform:uppercase; margin-bottom:18px;
    }}
    .hero-eyebrow:before {{ content:""; width:28px; height:1px; background:#ff4b58; }}
    .hero-title {{
        position:relative; z-index:1;
        margin:0; color:#fff;
        font-family:'Space Grotesk', sans-serif;
        font-size: clamp(42px, 6vw, 76px);
        line-height:.93; letter-spacing:-3px; font-weight:800;
        text-transform:uppercase;
    }}
    .hero-title span {{
        color:#d92330;
        background: linear-gradient(90deg, #ff4652, #e1333d, #ff6b75, #e1333d);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: batShimmer 5s linear infinite;
    }}
    .hero-description {{
        position:relative; z-index:1;
        max-width:640px; margin-top:22px;
        color:#b8abad; font-size:15px; line-height:1.8;
    }}

    /* FEATURE CARDS WITH FLOATING ICONS & SHIMMER HOVER */
    .feature-card {{
        background: linear-gradient(145deg, rgba(22, 12, 15, 0.94), rgba(12, 8, 9, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 24px 20px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        animation: batFadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        will-change: transform, opacity;
        position: relative;
        overflow: hidden;
    }}
    .feature-card:hover {{
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(255, 60, 75, 0.6);
        box-shadow: 0 14px 35px rgba(225, 20, 35, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }}
    .feature-icon {{
        font-size: 26px;
        color: #ff4b55;
        margin-bottom: 12px;
        display: inline-block;
        transition: transform 0.2s ease;
        animation: batIconFloat 3.5s ease-in-out infinite;
        will-change: transform;
    }}
    .feature-card:hover .feature-icon {{
        transform: scale(1.2) rotate(-4deg);
        filter: drop-shadow(0 0 12px rgba(255, 75, 85, 0.9));
    }}
    .feature-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }}
    .feature-description {{
        color: #9e9395;
        font-size: 12.5px;
        line-height: 1.6;
    }}

    /* STEP CARDS 3D HOVER ANIMATION */
    .step-box-card {{
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: batFadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        will-change: transform, opacity;
    }}
    .step-box-card:hover {{
        transform: translateY(-5px) !important;
        border-color: rgba(255, 75, 88, 0.75) !important;
        box-shadow: 0 16px 35px rgba(220, 25, 40, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }}
    .step-num-badge {{
        transition: all 0.2s ease !important;
    }}
    .step-box-card:hover .step-num-badge {{
        background: linear-gradient(135deg, #e21b28, #ff4d58) !important;
        color: #ffffff !important;
        transform: scale(1.12);
        box-shadow: 0 0 18px rgba(255, 75, 88, 0.8) !important;
    }}

    /* RESULT & METRIC CARDS ANIMATION */
    .result-card, .info-card, .input-panel {{
        background: linear-gradient(145deg, rgba(20, 10, 12, 0.94), rgba(10, 8, 9, 0.94));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 24px;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        animation: batFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .result-card:hover, .input-panel:hover {{
        border-color: rgba(255, 60, 75, 0.4);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
        transform: translateY(-4px);
    }}

    /* JOB CARDS HOVER ANIMATION */
    .job-card {{
        background: linear-gradient(145deg, rgba(24, 12, 15, 0.95), rgba(12, 9, 10, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 8px;
        padding: 26px;
        margin-bottom: 16px;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        animation: batFadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .job-card:hover {{
        transform: translateY(-6px) scale(1.008);
        border-color: rgba(255, 75, 88, 0.6);
        box-shadow: 0 20px 48px rgba(220, 25, 40, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }}
    .job-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        transition: color 0.25s ease;
    }}
    .job-card:hover .job-title {{
        color: #ff4d58;
    }}

    /* STREAMLIT BUTTON HOVER & GLOW ANIMATION */
    div[data-testid="stButton"] button {{
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative;
        overflow: hidden;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: translateY(-3px) scale(1.015) !important;
        box-shadow: 0 12px 30px rgba(226, 27, 40, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    }}

    /* FILE UPLOADER ANIMATED SCANNING GLOW */
    div[data-testid="stFileUploader"] {{
        border: 1px dashed rgba(255, 75, 88, 0.35) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stFileUploader"]:hover {{
        border-color: rgba(255, 75, 88, 0.85) !important;
        background: rgba(255, 45, 60, 0.04) !important;
        box-shadow: 0 0 25px rgba(255, 45, 60, 0.18) !important;
    }}

    /* SKILL BADGES MICRO-ANIMATION */
    .skill-badge {{
        display: inline-block;
        padding: 6px 14px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: rgba(255, 255, 255, 0.05);
        color: #e8dedf;
        border: 1px solid rgba(255, 255, 255, 0.12);
        transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
        cursor: default;
    }}
    .skill-badge:hover {{
        transform: scale(1.1) translateY(-2px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
    }}
    .matched-badge {{
        background: rgba(46, 204, 113, 0.14) !important;
        color: #2ecc71 !important;
        border: 1px solid rgba(46, 204, 113, 0.4) !important;
        box-shadow: 0 0 12px rgba(46, 204, 113, 0.2);
    }}
    .matched-badge:hover {{
        background: rgba(46, 204, 113, 0.28) !important;
        box-shadow: 0 0 20px rgba(46, 204, 113, 0.5) !important;
    }}
    .missing-badge {{
        background: rgba(241, 196, 15, 0.14) !important;
        color: #f1c40f !important;
        border: 1px solid rgba(241, 196, 15, 0.4) !important;
        box-shadow: 0 0 12px rgba(241, 196, 15, 0.2);
        animation: batStatusPulse 3s infinite ease-in-out;
    }}
    .missing-badge:hover {{
        background: rgba(241, 196, 15, 0.28) !important;
        box-shadow: 0 0 20px rgba(241, 196, 15, 0.5) !important;
    }}

    /* METRIC CARDS GLASSMORPHIC GLOW */
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, rgba(24, 12, 15, 0.92), rgba(12, 9, 10, 0.94)) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 16px 20px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px) !important;
        border-color: rgba(255, 75, 88, 0.5) !important;
        box-shadow: 0 14px 32px rgba(225, 20, 35, 0.25) !important;
    }}

    /* STREAMLIT PROGRESS BARS GLOW */
    div[data-testid="stProgress"] > div > div > div > div {{
        background: linear-gradient(90deg, #d21f2b 0%, #ff4b58 50%, #ff6b75 100%) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 14px rgba(255, 75, 88, 0.7) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CINEMATIC HEADER + NAVIGATION
# ============================================================

header_left, header_right = st.columns([3.5, 1])

with header_left:
    st.markdown(
        f"""
        <div class="app-header" style="border-bottom:none; padding-bottom:0;">
            <div class="brand-wrap">
                <div class="brand-mark" style="width:42px; height:42px; background:linear-gradient(135deg, #ff2a38, #990011); border-radius:10px; display:inline-flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(255,42,56,0.6); font-size:22px;">🤖</div>
                <div>
                    <div class="brand-title">NEXORA</div>
                    <div class="brand-subtitle">AI-powered career intelligence platform</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown("""<div style="text-align:right; padding-top:10px;"><span class="system-status"><span class="status-dot"></span> NEXORA ONLINE</span></div>""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="command-nav">
        <div class="command-item active">Command Center</div>
        <div class="command-item">Resume Analysis</div>
        <div class="command-item">ATS Intelligence</div>
        <div class="command-item">AI Review</div>
        <div class="command-item">Interview Lab</div>
        <div class="command-item">Career Intelligence</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO WITH SINGLE DRAGON HERO IMAGE
# ============================================================

st.markdown(
    f"""
    <div class="hero">
        <div style="display:flex; justify-content:space-between; align-items:center; position:relative; z-index:2; gap:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:300px;">
                <div class="hero-eyebrow">AI-Powered Career Intelligence Platform</div>
                <h1 class="hero-title">Build Your<br><span>Career</span> Edge.</h1>
                <div class="hero-description">
                    Analyze. Improve. Get Hired. Transform your resume into actionable career intelligence.
                    Analyze skills, measure ATS compatibility, uncover gaps, and prepare for your next opportunity.
                </div>
            </div>
            <div style="flex-shrink:0; padding-right:15px; text-align:center;">
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,45,60,0.3); padding: 22px 30px; border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 10px 40px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,45,60,0.08); text-align: center; min-width:220px;">
                    <div style="width: 56px; height: 56px; margin: 0 auto 10px; background: radial-gradient(circle, rgba(255,45,60,0.35) 0%, transparent 70%); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255,45,60,0.6); box-shadow: 0 0 25px rgba(255,45,60,0.5); font-size: 26px;">
                        🤖
                    </div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 1px; text-transform: uppercase;">NEXORA CORE</div>
                    <div style="font-size: 11px; color: #ff4b58; font-weight: 700; margin-top: 4px; letter-spacing: 1.5px; text-transform: uppercase;">AI Career Intelligence</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FEATURE CARDS
# ============================================================

feature1, feature2, feature3, feature4 = st.columns(4)

with feature1:
    st.markdown("""<div class="feature-card"><div class="feature-icon">◈</div><div class="feature-title">Resume Intelligence</div><div class="feature-description">Extract sections, candidate information and professional skills.</div></div>""", unsafe_allow_html=True)
with feature2:
    st.markdown("""<div class="feature-card"><div class="feature-icon">◎</div><div class="feature-title">ATS Optimization</div><div class="feature-description">Measure role compatibility and identify important skill gaps.</div></div>""", unsafe_allow_html=True)
with feature3:
    st.markdown("""<div class="feature-card"><div class="feature-icon">✦</div><div class="feature-title">AI Review</div><div class="feature-description">Receive strengths, weaknesses and actionable recommendations.</div></div>""", unsafe_allow_html=True)
with feature4:
    st.markdown("""<div class="feature-card"><div class="feature-icon">◌</div><div class="feature-title">Career Matching</div><div class="feature-description">Compare your profile against the opportunities you target.</div></div>""", unsafe_allow_html=True)


# ============================================================
# HOW IT WORKS SECTION (INTERACTIVE STEPS & NAVIGATION)
# ============================================================

st.markdown(
    """
    <style>
    .how-it-works-wrapper {
        margin: 36px 0 20px;
        padding: 32px 28px 20px;
        background: linear-gradient(145deg, rgba(22, 11, 14, 0.95), rgba(12, 9, 10, 0.95));
        border: 1px solid rgba(255, 45, 60, 0.2);
        border-radius: 8px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
    }
    .how-header-wrap {
        text-align: center;
        margin-bottom: 20px;
    }
    .how-badge {
        display: inline-block;
        color: #ff4d58;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 8px;
        padding: 4px 14px;
        background: rgba(220, 25, 40, 0.12);
        border: 1px solid rgba(255, 60, 75, 0.3);
        border-radius: 999px;
        box-shadow: 0 0 16px rgba(255, 45, 60, 0.22);
    }
    .how-main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(24px, 3.2vw, 36px);
        font-weight: 800;
        color: #ffffff;
        margin: 4px 0 8px;
    }
    .how-sub-title {
        color: #a89d9f;
        font-size: 13.5px;
        max-width: 580px;
        margin: 0 auto;
    }
    .step-box-card {
        background: linear-gradient(145deg, rgba(28, 15, 17, 0.94), rgba(13, 10, 11, 0.94));
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 6px;
        padding: 18px 14px 14px;
        min-height: 230px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .step-box-card.completed {
        border-color: rgba(46, 204, 113, 0.4);
        box-shadow: inset 0 0 15px rgba(46, 204, 113, 0.1);
    }
    .step-box-card.active-step {
        border-color: rgba(255, 60, 75, 0.55);
        box-shadow: 0 0 20px rgba(255, 45, 60, 0.25);
    }
    .step-num-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: rgba(220, 25, 40, 0.2);
        border: 1px solid rgba(255, 75, 88, 0.45);
        color: #ff5a64;
        font-size: 12px;
        font-weight: 900;
        border-radius: 50%;
        margin-bottom: 10px;
    }
    .step-box-title {
        color: #ffffff;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .step-box-desc {
        color: #9e9395;
        font-size: 11px;
        line-height: 1.55;
    }
    .step-status-chip {
        display: inline-block;
        font-size: 9.5px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .chip-complete { background: rgba(46, 204, 113, 0.18); color: #2ecc71; border: 1px solid rgba(46, 204, 113, 0.35); }
    .chip-active { background: rgba(255, 75, 88, 0.2); color: #ff5a64; border: 1px solid rgba(255, 75, 88, 0.4); }
    .chip-waiting { background: rgba(255, 255, 255, 0.05); color: #7f7577; border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>

    <div class="how-it-works-wrapper">
        <div class="how-header-wrap">
            <div class="how-badge">HOW IT WORKS</div>
            <h2 class="how-main-title">Your Resume → Career Intelligence</h2>
            <div class="how-sub-title">Follow these 5 simple steps to get a complete AI-powered career analysis. Click any step below to navigate directly.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5, gap="small")

is_done = st.session_state.get("analysis_complete", False)
is_uploaded = st.session_state.get("resume_upload") is not None

with s_col1:
    chip_class = "chip-complete" if is_uploaded else "chip-active"
    chip_label = "✓ RESUME READY" if is_uploaded else "⚡ STEP 01"
    st.markdown(f"""
        <div class="step-box-card {'active-step' if not is_uploaded else 'completed'}">
            <div>
                <div class="step-num-badge">01</div>
                <div class="step-box-title">📄 UPLOAD RESUME</div>
                <div class="step-box-desc">Upload your PDF or DOCX resume file to extract skills, experience and sections.</div>
            </div>
            <div><span class="step-status-chip {chip_class}">{chip_label}</span></div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("📄 01. Upload", key="btn_step_1", use_container_width=True):
        st.info("👇 Upload your resume file in the Resume Input box below!")

with s_col2:
    chip_class = "chip-complete" if is_done else ("chip-active" if is_uploaded else "chip-waiting")
    chip_label = "✓ COMPLETED" if is_done else ("⚡ READY" if is_uploaded else "WAITING")
    st.markdown(f"""
        <div class="step-box-card {'completed' if is_done else ''}">
            <div>
                <div class="step-num-badge">02</div>
                <div class="step-box-title">🧠 AI ANALYSIS</div>
                <div class="step-box-desc">Extract candidate skills, experience level, sections and ML similarity.</div>
            </div>
            <div><span class="step-status-chip {chip_class}">{chip_label}</span></div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🧠 02. Analyze", key="btn_step_2", use_container_width=True):
        st.session_state["pending_tab"] = "📊 Dashboard"
        st.rerun()

with s_col3:
    chip_class = "chip-complete" if is_done else "chip-waiting"
    chip_label = "✓ COMPLETED" if is_done else "WAITING"
    st.markdown(f"""
        <div class="step-box-card {'completed' if is_done else ''}">
            <div>
                <div class="step-num-badge">03</div>
                <div class="step-box-title">🎯 ATS CHECK</div>
                <div class="step-box-desc">Evaluate ATS score, missing keywords, formatting and role compatibility.</div>
            </div>
            <div><span class="step-status-chip {chip_class}">{chip_label}</span></div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🎯 03. ATS Check", key="btn_step_3", use_container_width=True):
        st.session_state["pending_tab"] = "🎯 ATS Analysis"
        st.rerun()

with s_col4:
    chip_class = "chip-complete" if is_done else "chip-waiting"
    chip_label = "✓ COMPLETED" if is_done else "WAITING"
    st.markdown(f"""
        <div class="step-box-card {'completed' if is_done else ''}">
            <div>
                <div class="step-num-badge">04</div>
                <div class="step-box-title">🤖 AI REVIEW</div>
                <div class="step-box-desc">Receive strengths, weaknesses, career feedback and interview preparation.</div>
            </div>
            <div><span class="step-status-chip {chip_class}">{chip_label}</span></div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🤖 04. AI Review", key="btn_step_4", use_container_width=True):
        st.session_state["pending_tab"] = "🤖 AI Review"
        st.rerun()

with s_col5:
    chip_class = "chip-complete" if is_done else "chip-waiting"
    chip_label = "✓ LIVE JOBS" if is_done else "LIVE"
    st.markdown(f"""
        <div class="step-box-card {'completed' if is_done else ''}">
            <div>
                <div class="step-num-badge">05</div>
                <div class="step-box-title">💼 OPPORTUNITIES</div>
                <div class="step-box-desc">Find live matching job vacancies across India with real Adzuna API integration.</div>
            </div>
            <div><span class="step-status-chip {chip_class}">{chip_label}</span></div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("💼 05. Job Vacancies", key="btn_step_5", use_container_width=True):
        st.session_state["pending_tab"] = "💼 Job Vacancies"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# RESUME INPUT WORKSPACE & FLOW INDICATOR
# ============================================================

st.markdown(
    """
    <div style="
        display:flex; justify-content:center; align-items:center; gap:18px;
        margin:15px 0 25px; padding:12px 24px;
        background:linear-gradient(90deg, rgba(28,15,17,0.85), rgba(13,10,11,0.85));
        border:1px solid rgba(255,60,75,0.25); border-radius:30px;
    ">
        <span style="color:#ff5a64; font-weight:800; font-size:12px; letter-spacing:1px;">📄 UPLOAD</span>
        <span style="color:#665557;">→</span>
        <span style="color:#ff5a64; font-weight:800; font-size:12px; letter-spacing:1px;">🧠 ANALYZE</span>
        <span style="color:#665557;">→</span>
        <span style="color:#ff5a64; font-weight:800; font-size:12px; letter-spacing:1px;">📊 RESULTS</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">Resume Intelligence Workspace</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Upload your resume and define the opportunity you want to target.</div>', unsafe_allow_html=True)

left_input, right_input = st.columns([1, 1], gap="large")

with left_input:
    st.markdown("""<div class="input-panel"><div class="panel-title">Resume Input</div><div class="panel-description">Upload your PDF or DOCX file. Your document will be used for complete analysis.</div></div>""", unsafe_allow_html=True)
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx"], label_visibility="collapsed", key="resume_upload")
    if resume is not None:
        current_resume_id = f"{resume.name}_{resume.size}"
        if st.session_state.get("uploaded_resume_id") != current_resume_id:
            st.session_state["uploaded_resume_id"] = current_resume_id
            st.session_state.analysis = {}
            st.session_state.analysis_complete = False
            st.session_state.rewritten_resume = None
            if "job_search_results" in st.session_state:
                st.session_state["job_search_results"] = None
        st.success(f"Resume ready: {resume.name}")

with right_input:
    st.markdown("""<div class="input-panel"><div class="panel-title">Target Opportunity</div><div class="panel-description">Define the role and paste the job description you want to match against.</div></div>""", unsafe_allow_html=True)
    target_job = st.text_input("Target Job", placeholder="Example: Software Engineer", key="target_job")
    job_description = st.text_area("Job Description", placeholder="Paste the target job description here...", height=180, key="job_description")


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 1.8, 1])
with analyze_col2:
    analyze = st.button("ANALYZE MY RESUME  →", type="primary", use_container_width=True)


# ============================================================
# ANALYSIS ENGINE PIPELINE
# ============================================================

if analyze:

    if resume is None:

        st.warning("⚠️ Please upload your resume first.")

        st.stop()

    if not job_description.strip():
        if target_job.strip():
            job_description = f"Job Position: {target_job}. Professional role requiring relevant technical skills, domain expertise, project experience, and candidate capabilities."
        else:
            job_description = "General Professional Candidate Position requiring relevant industry experience, technical skills, domain expertise, project achievements, and professional qualifications."

    try:

        pipeline = st.status("🧠 **AI Analysis Pipeline Running...**", expanded=True)
        pipeline.write("📄 **Step 1/5:** Reading and extracting resume document content...")

        # ------------------------------------------------
        # 1. EXTRACT RESUME
        # ------------------------------------------------

        resume_text = extract_resume_text(resume)

        if not resume_text:

            pipeline.update(label="❌ **Extraction Failed**", state="error", expanded=True)
            st.error("❌ No text could be extracted from the resume.")
            st.stop()

        if resume_text.startswith("Error"):

            pipeline.update(label="❌ **Extraction Error**", state="error", expanded=True)
            st.error(resume_text)
            st.stop()

        pipeline.write("🔍 **Step 2/5:** Preprocessing text & detecting candidate skills...")

        # ------------------------------------------------
        # 2. PREPROCESS
        # ------------------------------------------------

        processed_resume = preprocess_resume(resume_text)
        cleaned_resume = processed_resume["cleaned_text"]
        normalized_resume = processed_resume["normalized_text"]

        # ------------------------------------------------
        # 3. CANDIDATE INFORMATION
        # ------------------------------------------------

        contact_info = extract_contact_information(cleaned_resume)
        detected_skills = extract_skills(cleaned_resume)
        resume_sections = extract_sections(cleaned_resume)

        pipeline.write("🎯 **Step 3/5:** Evaluating job requirements & calculating ATS score...")

        # ------------------------------------------------
        # 4. JOB ANALYSIS
        # ------------------------------------------------

        job_analysis = analyze_job_description(job_description)
        job_skills = job_analysis["required_skills"]

        skill_comparison = compare_skills(detected_skills, job_skills)
        matched_skills = skill_comparison["matched_skills"]
        missing_skills = skill_comparison["missing_skills"]
        skill_match = skill_comparison["skill_match_percentage"]

        # ------------------------------------------------
        # 5. ML SIMILARITY
        # ------------------------------------------------

        resume_job_similarity = calculate_text_similarity(
            normalized_resume,
            job_analysis["normalized_text"],
        )

        # ------------------------------------------------
        # 6. JOB CLASSIFICATION
        # ------------------------------------------------

        job_classification = classify_job(job_description)
        job_category = job_classification["category"]
        job_confidence = job_classification["confidence"]

        # ------------------------------------------------
        # 7. CANDIDATE LEVEL
        # ------------------------------------------------

        candidate_level_result = detect_candidate_level(job_description)
        candidate_level = candidate_level_result["level"]
        years_required = candidate_level_result["years_required"]
        level_confidence = candidate_level_result["confidence"]

        # ------------------------------------------------
        # 8. OVERALL SCORE
        # ------------------------------------------------

        score_result = calculate_overall_score(skill_match, resume_job_similarity)
        overall_score = score_result["overall_score"]
        score_label = get_score_label(overall_score)

        # ------------------------------------------------
        # 9. RESUME QUALITY
        # ------------------------------------------------

        quality_result = calculate_resume_quality(
            contact_info,
            detected_skills,
            resume_sections,
        )

        resume_quality_score = quality_result["quality_score"]
        quality_checks = quality_result["checks"]
        quality_label = get_quality_label(resume_quality_score)

        # ------------------------------------------------
        # 10. AI FEEDBACK
        # ------------------------------------------------

        feedback = generate_ai_feedback(
            overall_score,
            resume_quality_score,
            matched_skills,
            missing_skills,
            quality_checks,
        )

        # ------------------------------------------------
        # 11. ATS SUGGESTIONS
        # ------------------------------------------------

        ats_result = generate_ats_suggestions(
            missing_skills,
            quality_checks,
            overall_score,
        )

        # ------------------------------------------------
        # 12. INTERVIEW & PERSONALIZED AI REVIEW
        # ------------------------------------------------

        interview_questions = generate_interview_questions(
            detected_skills,
            missing_skills,
            job_category,
            candidate_level,
        )

        pipeline.write("🤖 **Step 4/5:** Running AI Review & generating personalized insights...")

        ai_review_result = generate_personalized_ai_review(
            resume_data={
                "resume_text": resume_text,
                "cleaned_resume": cleaned_resume,
                "contact_info": contact_info,
                "detected_skills": detected_skills,
                "resume_sections": resume_sections,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "job_skills": job_skills,
                "overall_score": overall_score,
                "resume_quality_score": resume_quality_score,
                "candidate_level": candidate_level,
                "skill_match": skill_match,
                "resume_job_similarity": resume_job_similarity,
            },
            job_description=job_description,
            target_job=target_job,
        )

        pipeline.write("💼 **Step 5/5:** Calculating profile match & live job compatibility...")
        pipeline.update(label="✅ **AI Career Intelligence Analysis Complete!**", state="complete", expanded=False)

        # ----------------------------------------------------
        # SAVE RESULTS IN SESSION
        # ----------------------------------------------------

        inferred_role = infer_target_role(
            resume_text=resume_text,
            detected_skills=detected_skills,
            job_category=job_category,
        )
        target_role = target_job.strip() if target_job and target_job.strip() else inferred_role

        st.session_state.analysis = {
            "resume": resume,
            "resume_name": resume.name,
            "resume_text": resume_text,
            "cleaned_resume": cleaned_resume,
            "normalized_resume": normalized_resume,
            "contact_info": contact_info,
            "detected_skills": detected_skills,
            "resume_sections": resume_sections,
            "job_description": job_description,
            "target_job": target_job,
            "target_role": target_role,
            "job_analysis": job_analysis,
            "job_skills": job_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_match": skill_match,
            "resume_job_similarity": resume_job_similarity,
            "job_category": job_category,
            "job_confidence": job_confidence,
            "candidate_level": candidate_level,
            "years_required": years_required,
            "level_confidence": level_confidence,
            "score_result": score_result,
            "overall_score": overall_score,
            "score_label": score_label,
            "resume_quality_score": resume_quality_score,
            "quality_checks": quality_checks,
            "quality_label": quality_label,
            "feedback": feedback,
            "ats_result": ats_result,
            "interview_questions": interview_questions,
            "ai_review": ai_review_result,
        }

        st.session_state.analysis_complete = True

        save_analysis(
            resume.name,
            overall_score,
            resume_quality_score,
            job_category,
        )

        st.success("✅ Resume analyzed successfully.")

    except Exception as error:

        st.error(
            f"❌ Analysis failed: {type(error).__name__}: {error}"
        )

        st.stop()


# ============================================================
# LOAD ANALYSIS FROM SESSION
# ============================================================

def render_pending_card(tab_name):
    st.markdown(
        f"""
        <div style="
            margin: 25px 0; padding: 40px 30px; text-align: center;
            background: linear-gradient(145deg, rgba(22, 11, 14, 0.95), rgba(12, 9, 10, 0.95));
            border: 1px dashed rgba(255, 45, 60, 0.35); border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        ">
            <div style="font-size: 38px; margin-bottom: 12px;">⚡</div>
            <h3 style="color:#ffffff; font-family:'Space Grotesk', sans-serif; font-size:22px; margin-bottom:8px;">
                Resume Intelligence Pending for {tab_name}
            </h3>
            <p style="color:#a89d9f; font-size:14px; max-width:580px; margin: 0 auto 20px;">
                Upload your resume PDF/DOCX in the <b>Resume Intelligence Workspace</b> above and click <b>ANALYZE MY RESUME</b> to unlock AI insights, ATS scoring, and custom recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========================================================
# 7 TABS (PERSISTENT SESSION STATE NAVIGATOR)
# ========================================================

st.markdown("<br>", unsafe_allow_html=True)

tab_options = [
    "📊 Dashboard",
    "🎯 ATS Analysis",
    "🧠 Skill Gap Analysis",
    "🚀 Career Roadmap",
    "🤖 AI Review",
    "🎤 Interview",
    "✍️ Resume Rewrite",
    "👤 Profile",
    "💼 Job Vacancies",
]

if "pending_tab" in st.session_state:
    st.session_state["active_tab"] = st.session_state.pop("pending_tab")

current_tab = st.session_state.get("active_tab", "📊 Dashboard")
if current_tab in ["Skill Gap Analysis", "🧠 Skill Gap Analysis", "Skill Gap"]:
    current_tab = "🧠 Skill Gap Analysis"
elif current_tab in ["Career Roadmap", "🚀 Career Roadmap", "Roadmap"]:
    current_tab = "🚀 Career Roadmap"
elif current_tab in ["Job Vacancies", "💼 Job Vacancies"]:
    current_tab = "💼 Job Vacancies"
elif current_tab not in tab_options:
    current_tab = "📊 Dashboard"

selected_tab = st.radio(
    "Navigation Tabs",
    options=tab_options,
    index=tab_options.index(current_tab),
    key="active_tab",
    horizontal=True,
    label_visibility="collapsed",
)

has_analysis = st.session_state.get("analysis_complete", False)

if has_analysis:
    data = st.session_state.analysis

    resume_text = data["resume_text"]
    cleaned_resume = data["cleaned_resume"]
    normalized_resume = data["normalized_resume"]

    contact_info = data["contact_info"]
    detected_skills = data["detected_skills"]
    resume_sections = data["resume_sections"]

    job_description = data["job_description"]
    target_job = data["target_job"]

    job_analysis = data["job_analysis"]

    job_skills = data["job_skills"]

    matched_skills = data["matched_skills"]
    missing_skills = data["missing_skills"]

    skill_match = data["skill_match"]
    resume_job_similarity = data["resume_job_similarity"]

    job_category = data["job_category"]
    job_confidence = data["job_confidence"]

    candidate_level = data["candidate_level"]
    years_required = data["years_required"]
    level_confidence = data["level_confidence"]

    score_result = data["score_result"]
    overall_score = data["overall_score"]
    score_label = data["score_label"]

    resume_quality_score = data["resume_quality_score"]
    quality_checks = data["quality_checks"]
    quality_label = data["quality_label"]

    feedback = data["feedback"]
    ats_result = data["ats_result"]

    interview_questions = data["interview_questions"]

# ========================================================
# TAB 1 - DASHBOARD
# ========================================================

if selected_tab == "📊 Dashboard":

    if not has_analysis:
        render_pending_card("Dashboard")
    else:

        st.markdown(
            '<div class="section-heading">📊 Candidate Intelligence</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="section-description">
                Resume analysis completed using NLP, scoring and AI.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric(
                "ATS / Overall Score",
                f"{overall_score:.0f}%",
                score_label,
            )

        with metric2:
            st.metric(
                "Resume Quality",
                f"{resume_quality_score:.0f}%",
                quality_label,
            )

        with metric3:
            st.metric(
                "Skill Match",
                f"{skill_match:.0f}%",
            )

        with metric4:
            st.metric(
                "ML Similarity",
                f"{resume_job_similarity:.0f}%",
            )

        st.markdown("")

        # ----------------------------------------------------
        # SCORE VISUALIZATION
        # ----------------------------------------------------

        score_left, score_right = st.columns(
            [1, 1.4],
            gap="large",
        )

        with score_left:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("### Overall Match")

            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=float(overall_score),
                    number={
                        "suffix": "%",
                        "font": {
                            "size": 42,
                            "color": "#f8fafc",
                        },
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickcolor": "#64748b",
                        },
                        "bar": {
                            "color": "#3b82f6",
                        },
                        "bgcolor": "#1a2330",
                        "borderwidth": 0,
                        "steps": [
                            {
                                "range": [0, 50],
                                "color": "#111722",
                            },
                            {
                                "range": [50, 75],
                                "color": "#172033",
                            },
                            {
                                "range": [75, 100],
                                "color": "#1b293e",
                            },
                        ],
                    },
                )
            )

            gauge.update_layout(
                height=280,
                margin=dict(
                    l=20,
                    r=20,
                    t=30,
                    b=20,
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
            )

            st.plotly_chart(
                gauge,
                use_container_width=True,
            )

            st.markdown(
                f"**Assessment:** {score_label}"
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with score_right:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("### 📈 Score Breakdown")

            st.progress(
                min(skill_match / 100, 1.0)
            )

            st.write(
                f"**Skill Match:** {skill_match:.1f}%"
            )

            st.progress(
                min(resume_job_similarity / 100, 1.0)
            )

            st.write(
                f"**ML Text Similarity:** "
                f"{resume_job_similarity:.1f}%"
            )

            st.progress(
                min(resume_quality_score / 100, 1.0)
            )

            st.write(
                f"**Resume Quality:** "
                f"{resume_quality_score:.1f}%"
            )

            st.markdown(
                f"""
                <div class="info-card">
                    <b>Target Role:</b> {target_job or job_category}<br>
                    <b>Industry:</b> {job_category}<br>
                    <b>Candidate Level:</b> {candidate_level}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # SKILLS
        # ----------------------------------------------------

        st.markdown("### 🧠 Skill Intelligence")

        skill_left, skill_right = st.columns(2)

        with skill_left:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("#### 🟢 Matched Skills")

            if matched_skills:

                for skill in matched_skills:

                    st.markdown(
                        f'<span class="skill-badge matched-badge">'
                        f'{skill}'
                        f'</span>',
                        unsafe_allow_html=True,
                    )

            else:

                st.info("No matching skills detected.")

            st.markdown("</div>", unsafe_allow_html=True)

        with skill_right:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("#### 🟡 Skill Gaps")

            if missing_skills:

                for skill in missing_skills:

                    st.markdown(
                        f'<span class="skill-badge missing-badge">'
                        f'{skill}'
                        f'</span>',
                        unsafe_allow_html=True,
                    )

            else:

                st.success(
                    "No major skill gaps detected."
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # QUALITY
        # ----------------------------------------------------

        st.markdown("### 📋 Resume Quality")

        quality_left, quality_right = st.columns(2)

        with quality_left:

            st.metric(
                "Resume Quality",
                f"{resume_quality_score:.0f}/100",
                quality_label,
            )

            st.progress(
                min(resume_quality_score / 100, 1.0)
            )

        with quality_right:

            check_items = list(
                quality_checks.items()
            )

            if check_items:

                midpoint = (
                    len(check_items) + 1
                ) // 2

                check_col1, check_col2 = st.columns(2)

                with check_col1:

                    for name, present in check_items[
                        :midpoint
                    ]:

                        if present:
                            st.write(
                                f"✅ {name}"
                            )
                        else:
                            st.write(
                                f"❌ {name}"
                            )

                with check_col2:

                    for name, present in check_items[
                        midpoint:
                    ]:

                        if present:
                            st.write(
                                f"✅ {name}"
                            )
                        else:
                            st.write(
                                f"❌ {name}"
                            )

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        st.divider()

        if "pdf_data" not in st.session_state:
            st.session_state.pdf_data = None

        if st.button("📄 Generate Analysis Report", key="generate_pdf"):

            analysis_data = {
                "Overall ATS Score": f"{overall_score:.0f}/100",
                "Resume Quality": f"{resume_quality_score:.0f}/100",
                "Job Category": job_category,
                "Detected Skills": ", ".join(detected_skills),
                "Matched Skills": ", ".join(matched_skills),
                "Missing Skills": ", ".join(missing_skills),
            }

            with st.spinner("Generating PDF report..."):
                try:
                    pdf_path = generate_analysis_pdf(analysis_data)

                    with open(pdf_path, "rb") as pdf_file:
                        st.session_state.pdf_data = pdf_file.read()

                except Exception as error:
                    st.error(f"PDF generation failed: {error}")


        if st.session_state.pdf_data:

            st.download_button(
                label="⬇️ Download Analysis Report",
                data=st.session_state.pdf_data,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                key="dashboard_pdf",
            )

# ========================================================
# TAB 2 - ATS
# ========================================================

elif selected_tab == "🎯 ATS Analysis":

    if not has_analysis:
        render_pending_card("ATS Analysis")
    else:
        st.markdown(
            '<div class="section-heading">🎯 ATS Analysis</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="section-description">
                Understand how your resume matches the target role.
            </div>
            """,
            unsafe_allow_html=True,
        )

        ats1, ats2, ats3, ats4 = st.columns(4)

        with ats1:
            st.metric(
                "Overall Score",
                f"{overall_score:.0f}%",
            )

        with ats2:
            st.metric(
                "Skill Match",
                f"{skill_match:.0f}%",
            )

        with ats3:
            st.metric(
                "Matched Skills",
                len(matched_skills),
            )

        with ats4:
            st.metric(
                "Missing Skills",
                len(missing_skills),
            )

        st.markdown("### 🔍 Match Analysis")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("#### Required Skills")

            for skill in job_skills:

                st.markdown(
                    f'<span class="skill-badge">'
                    f'{skill}'
                    f'</span>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown("#### Resume Skills")

            for skill in detected_skills:

                badge_class = (
                    "matched-badge"
                    if skill in matched_skills
                    else ""
                )

                st.markdown(
                    f'<span class="skill-badge {badge_class}">'
                    f'{skill}'
                    f'</span>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 🏢 Job Classification")

        category1, category2, category3 = st.columns(3)

        with category1:
            st.metric(
                "Role / Industry",
                job_category,
            )

        with category2:
            st.metric(
                "Classification Confidence",
                f"{job_confidence:.0f}%",
            )

        with category3:
            st.metric(
                "Candidate Level",
                candidate_level,
            )

        st.markdown("### 📊 ATS Optimization")

        estimated_score = ats_result.get(
            "estimated_score",
            overall_score,
        )

        st.metric(
            "Potential Match",
            f"{estimated_score:.0f}%",
        )

        st.progress(
            min(estimated_score / 100, 1.0)
        )

        st.markdown("#### 🔥 Priority Actions")

        priority_actions = ats_result.get(
            "priority_actions",
            [],
        )

        if priority_actions:

            for action in priority_actions:

                priority = action.get(
                    "priority",
                    "Low",
                )

                message = action.get(
                    "message",
                    "",
                )

                if priority == "High":
                    st.error(
                        f"🔴 {message}"
                    )

                elif priority == "Medium":
                    st.warning(
                        f"🟡 {message}"
                    )

                else:
                    st.info(
                        f"🔵 {message}"
                    )

        else:

            st.success(
                "No priority actions returned."
            )

        st.markdown("#### 💡 General ATS Tips")

        for suggestion in ats_result.get(
            "general_suggestions",
            [],
        ):

            st.info(suggestion)

    # ========================================================
    # TAB 3 - SKILL GAP ANALYSIS
    # ========================================================

elif selected_tab == "🧠 Skill Gap Analysis":
    render_skill_gap_tab(data if has_analysis else None)

    # ========================================================
    # TAB 4 - CAREER ROADMAP
    # ========================================================

elif selected_tab == "🚀 Career Roadmap":
    render_career_roadmap_tab(data if has_analysis else None)

    # ========================================================
    # TAB 5 - AI REVIEW
    # ========================================================

elif selected_tab == "🤖 AI Review":

    if not has_analysis:
        render_pending_card("AI Review")
    else:
        ai_review = data.get("ai_review")
        if not ai_review or not isinstance(ai_review, dict):
            ai_review = generate_personalized_ai_review(
                data,
                job_description=data.get("job_description", ""),
                target_job=data.get("target_job", "Target Position"),
            )
            st.session_state.analysis["ai_review"] = ai_review
            
        render_ai_review_tab(ai_review, target_job=data.get("target_job", "Target Position"))

    # ========================================================
    # TAB 4 - INTERVIEW
    # ========================================================

elif selected_tab == "🎤 Interview":

    if not has_analysis:
        render_interview_tab(None)
    else:
        render_interview_tab(data, resume_id=st.session_state.get("uploaded_resume_id"))

    # ========================================================
    # TAB 5 - RESUME REWRITE
    # ========================================================

elif selected_tab == "✍️ Resume Rewrite":

    if not has_analysis:
        render_resume_rewrite_tab(None)
    else:
        render_resume_rewrite_tab(data, resume_id=st.session_state.get("uploaded_resume_id"))

    # ========================================================
    # TAB 6 - PROFILE
    # ========================================================

elif selected_tab == "👤 Profile":

    if not has_analysis:
        render_pending_card("Profile & Career Roadmap")
    else:
        st.markdown("## 👤 Candidate Profile")

        profile_data = {
            "name": "Not available",
            "job_category": job_category,
            "candidate_level": candidate_level,
            "target_job": target_job or job_category,
            "email": contact_info.get("email", "Not available"),
            "phone": contact_info.get("phone", "Not available"),
            "linkedin": contact_info.get("linkedin", "Not available"),
            "github": contact_info.get("github", "Not available"),
            "skills": detected_skills,
            "resume_sections": resume_sections,
        }

        name = profile_data.get("name", "Not available")
        email = profile_data.get("email", "Not available")
        phone = profile_data.get("phone", "Not available")
        linkedin = profile_data.get("linkedin", "Not available")
        github = profile_data.get("github", "Not available")

        profile_left, profile_right = st.columns(2)

        with profile_left:
            st.markdown("### 👤 Profile Information")
            st.write(f"### {name}")
            st.caption(profile_data["job_category"])

            st.divider()
            st.markdown("**CAREER LEVEL**")
            st.write(profile_data["candidate_level"])
            st.markdown("**TARGET POSITION**")
            st.write(profile_data["target_job"])

        with profile_right:
            st.markdown("### 📞 Contact Information")
            st.divider()
            st.write(f"📧 **Email:** {email}")
            st.write(f"📱 **Phone:** {phone}")
            st.write(f"🔗 **LinkedIn:** {linkedin}")
            st.write(f"💻 **GitHub:** {github}")

        st.markdown("### 🧠 Detected Skills")
        if detected_skills:
            skills_text = " • ".join(detected_skills)
            st.write(skills_text)
        else:
            st.info("No skills detected.")

        st.markdown("### 🎓 Resume Sections")
        if resume_sections:
            section_columns = st.columns(min(len(resume_sections), 4))
            for index, section in enumerate(resume_sections.keys()):
                with section_columns[index % len(section_columns)]:
                    st.success(f"✅ {section}")

        st.markdown("### 📊 Candidate Snapshot")
        p1, p2, p3, p4 = st.columns(4)

        with p1:
            st.metric("Overall Score", f"{overall_score:.0f}%")

        with p2:
            st.metric("Resume Quality", f"{resume_quality_score:.0f}%")

        with p3:
            st.metric("Skill Match", f"{skill_match:.0f}%")

        with p4:
            st.metric("ML Similarity", f"{resume_job_similarity:.0f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-card">
                <h3 style="margin-top:0; color:#fff;">🗺️ Career Development Roadmap</h3>
                <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap; text-align:center; padding:15px 0;">
                    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:14px 16px; flex:1; min-width:130px;">
                        <div style="color:#ff5a64; font-size:10px; font-weight:800; text-transform:uppercase;">01 CURRENT LEVEL</div>
                        <div style="color:#fff; font-weight:800; margin-top:6px; font-size:13px;">{candidate_level}</div>
                    </div>
                    <div style="color:#ff4b58; font-size:18px; font-weight:900;">→</div>
                    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:14px 16px; flex:1; min-width:130px;">
                        <div style="color:#ff5a64; font-size:10px; font-weight:800; text-transform:uppercase;">02 TARGET ROLE</div>
                        <div style="color:#fff; font-weight:800; margin-top:6px; font-size:13px;">{target_job or job_category}</div>
                    </div>
                    <div style="color:#ff4b58; font-size:18px; font-weight:900;">→</div>
                    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:14px 16px; flex:1; min-width:130px;">
                        <div style="color:#ff5a64; font-size:10px; font-weight:800; text-transform:uppercase;">03 SKILL GAPS</div>
                        <div style="color:#fff; font-weight:800; margin-top:6px; font-size:13px;">{len(missing_skills)} Gaps</div>
                    </div>
                    <div style="color:#ff4b58; font-size:18px; font-weight:900;">→</div>
                    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:14px 16px; flex:1; min-width:130px;">
                        <div style="color:#ff5a64; font-size:10px; font-weight:800; text-transform:uppercase;">04 OPPORTUNITIES</div>
                        <div style="color:#fff; font-weight:800; margin-top:6px; font-size:13px;">Adzuna Live Search</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # TAB 7 - JOB VACANCIES
    # ========================================================

elif selected_tab == "💼 Job Vacancies":
    render_job_vacancies_tab(data if has_analysis else None)

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br><br>

    <div style="
        text-align:center;
        color:#667386;
        font-size:12px;
        padding:25px 0;
        border-top:1px solid #1f2937;
    ">

        NEXORA
        &nbsp;•&nbsp;
        AI-Powered Career Intelligence Platform

    </div>
    """,
    unsafe_allow_html=True,
) 