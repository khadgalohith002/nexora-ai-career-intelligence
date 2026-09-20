import streamlit as st

def render_ai_review_tab(ai_review, target_job="Target Role"):
    """
    Renders an executive-grade, 100% data-driven personalized AI Review UI.
    """
    if not ai_review or not isinstance(ai_review, dict):
        st.warning("⚠️ No AI Review data available. Please re-run resume analysis.")
        return

    candidate_name = ai_review.get("candidate_name", "Candidate")
    exec_summary = ai_review.get("executive_summary", "")
    strengths = ai_review.get("strengths", [])
    areas_to_improve = ai_review.get("areas_to_improve", [])
    skill_analysis = ai_review.get("skill_analysis", {})
    exp_analysis = ai_review.get("experience_analysis", {})
    proj_analysis = ai_review.get("project_analysis", {})
    keyword_insights = ai_review.get("ats_keyword_insights", {})
    career_positioning = ai_review.get("career_positioning", {})
    recommendations = ai_review.get("recommendations", {})
    action_plan = ai_review.get("action_plan", [])
    scores = ai_review.get("scores", {})

    target_role_display = career_positioning.get("target_role", target_job)

    # Custom CSS for AI Review UI
    st.markdown("""
        <style>
        .review-header-box {
            background: linear-gradient(135deg, rgba(30, 15, 20, 0.95), rgba(15, 10, 12, 0.95));
            border: 1px solid rgba(255, 45, 60, 0.35);
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,45,60,0.1);
        }
        .review-title-badge {
            display: inline-block;
            color: #ff4d58;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 3px;
            text-transform: uppercase;
            padding: 4px 14px;
            background: rgba(220, 25, 40, 0.15);
            border: 1px solid rgba(255, 60, 75, 0.35);
            border-radius: 999px;
            margin-bottom: 10px;
        }
        .candidate-hero-name {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(24px, 3vw, 34px);
            font-weight: 900;
            color: #ffffff;
            margin: 0 0 6px 0;
        }
        .target-role-sub {
            color: #b8acae;
            font-size: 14px;
            letter-spacing: 1px;
        }
        .score-card-main {
            background: linear-gradient(145deg, rgba(40, 18, 22, 0.9), rgba(20, 12, 14, 0.9));
            border: 1px solid rgba(255, 45, 60, 0.4);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .score-val-big {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 44px;
            font-weight: 900;
            color: #ff4d58;
            text-shadow: 0 0 20px rgba(255,77,88,0.6);
            line-height: 1.1;
        }
        .score-val-medium {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.1;
        }
        .score-lbl-sub {
            color: #a89d9f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 6px;
        }
        .evidence-card {
            background: rgba(22, 14, 16, 0.85);
            border-left: 3px solid #2ecc71;
            border-top: 1px solid rgba(255,255,255,0.06);
            border-right: 1px solid rgba(255,255,255,0.06);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .weakness-card {
            background: rgba(22, 14, 16, 0.85);
            border-left: 3px solid #f1c40f;
            border-top: 1px solid rgba(255,255,255,0.06);
            border-right: 1px solid rgba(255,255,255,0.06);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .card-item-title {
            font-weight: 800;
            font-size: 14px;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .card-item-body {
            font-size: 13px;
            color: #b8acae;
            line-height: 1.4;
        }
        .skill-pill-green {
            display: inline-block;
            background: rgba(46, 204, 113, 0.15);
            color: #2ecc71;
            border: 1px solid rgba(46, 204, 113, 0.35);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }
        .skill-pill-yellow {
            display: inline-block;
            background: rgba(241, 196, 15, 0.15);
            color: #f1c40f;
            border: 1px solid rgba(241, 196, 15, 0.35);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }
        .skill-pill-red {
            display: inline-block;
            background: rgba(231, 76, 60, 0.15);
            color: #e74c3c;
            border: 1px solid rgba(231, 76, 60, 0.35);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }
        .project-block-card {
            background: linear-gradient(145deg, rgba(26, 15, 18, 0.9), rgba(14, 10, 12, 0.9));
            border: 1px solid rgba(255, 45, 60, 0.25);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .proj-name-heading {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 16px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 8px;
        }
        .action-step-card {
            background: linear-gradient(145deg, rgba(28, 16, 19, 0.9), rgba(15, 11, 13, 0.9));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 12px;
        }
        .step-num-circle {
            background: rgba(220, 25, 40, 0.2);
            border: 1px solid rgba(255, 75, 88, 0.5);
            color: #ff4d58;
            font-weight: 900;
            font-size: 14px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # 1. HEADER BANNER
    # --------------------------------------------------------
    st.markdown(f"""
        <div class="review-header-box">
            <div class="review-title-badge">🤖 AI CAREER INTELLIGENCE</div>
            <div class="candidate-hero-name">{candidate_name}</div>
            <div class="target-role-sub">Personalized Resume & Career Analysis for <b>{target_role_display}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # 2. DYNAMIC SCORES GRID
    # --------------------------------------------------------
    sc_overall = scores.get("overall", 75)
    sc_skill = scores.get("skill_alignment", 75)
    sc_exp = scores.get("experience_alignment", 75)
    sc_proj = scores.get("project_relevance", 75)
    sc_kw = scores.get("keyword_alignment", 75)
    sc_qual = scores.get("resume_quality", 75)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-big">{int(round(float(sc_overall)))}%</div>
                <div class="score-lbl-sub">AI Profile Score</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-medium">{int(round(float(sc_skill)))}%</div>
                <div class="score-lbl-sub">Skill Alignment</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-medium">{int(round(float(sc_exp)))}%</div>
                <div class="score-lbl-sub">Experience</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-medium">{int(round(float(sc_proj)))}%</div>
                <div class="score-lbl-sub">Projects</div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-medium">{int(round(float(sc_kw)))}%</div>
                <div class="score-lbl-sub">ATS Keywords</div>
            </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
            <div class="score-card-main">
                <div class="score-val-medium">{int(round(float(sc_qual)))}%</div>
                <div class="score-lbl-sub">Resume Quality</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # 3. EXECUTIVE SUMMARY
    # --------------------------------------------------------
    st.markdown("### 📝 Executive Summary")
    st.info(exec_summary)

    st.divider()

    # --------------------------------------------------------
    # 4. SIDE-BY-SIDE STRENGTHS & AREAS TO IMPROVE
    # --------------------------------------------------------
    col_str, col_imp = st.columns(2, gap="large")

    with col_str:
        st.markdown("### 💪 Evidence-Based Strengths")
        if strengths:
            for s_item in strengths:
                st.markdown(f"""
                    <div class="evidence-card">
                        <div class="card-item-title">✓ {s_item.get('title', '')}</div>
                        <div class="card-item-body">"{s_item.get('evidence', '')}"</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Candidate demonstrates foundational qualifications.")

    with col_imp:
        st.markdown("### ⚠️ Areas to Improve")
        if areas_to_improve:
            for a_item in areas_to_improve:
                st.markdown(f"""
                    <div class="weakness-card">
                        <div class="card-item-title">⚠ {a_item.get('title', '')}</div>
                        <div class="card-item-body">{a_item.get('explanation', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No critical weakness areas detected.")

    st.divider()

    # --------------------------------------------------------
    # 5. SKILL ANALYSIS (STRONG, DEVELOPING, MISSING)
    # --------------------------------------------------------
    st.markdown("### 🧠 Comprehensive Skill Breakdown")
    sk_col1, sk_col2, sk_col3 = st.columns(3, gap="medium")

    with sk_col1:
        st.markdown("#### 🟢 Strong Skills (Evidence-Based)")
        strong_list = skill_analysis.get("strong_skills", [])
        if strong_list:
            pills = "".join([f'<span class="skill-pill-green">✓ {s}</span>' for s in strong_list])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No verified strong skills.")

    with sk_col2:
        st.markdown("#### 🟡 Developing Skills")
        dev_list = skill_analysis.get("developing_skills", [])
        if dev_list:
            pills = "".join([f'<span class="skill-pill-yellow">⚡ {s}</span>' for s in dev_list])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No developing skills specified.")

    with sk_col3:
        st.markdown("#### 🔴 Missing / Recommended Skills")
        miss_list = skill_analysis.get("missing_skills", [])
        if miss_list:
            pills = "".join([f'<span class="skill-pill-red">⚠ {s}</span>' for s in miss_list])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No missing target role skills detected.")

    st.divider()

    # --------------------------------------------------------
    # 6. EXPERIENCE ANALYSIS
    # --------------------------------------------------------
    st.markdown("### 💼 Experience Analysis")
    has_exp = exp_analysis.get("has_experience", True)
    exp_items = exp_analysis.get("items", [])
    exp_note = exp_analysis.get("general_note", "")

    if not has_exp or not exp_items:
        st.warning(f"ℹ️ {exp_note if exp_note else 'No professional experience was identified in the uploaded resume.'}")
    else:
        for exp in exp_items:
            with st.expander(f"📌 {exp.get('role_or_company', 'Work Experience')}", expanded=True):
                st.markdown(f"**✓ Strength:** {exp.get('strength', '')}")
                st.markdown(f"**💡 Recommendation:** {exp.get('improvement', '')}")

    st.divider()

    # --------------------------------------------------------
    # 7. PROJECT ANALYSIS
    # --------------------------------------------------------
    st.markdown("### 🛠️ Project Portfolio Analysis")
    has_proj = proj_analysis.get("has_projects", True)
    proj_items = proj_analysis.get("items", [])
    proj_note = proj_analysis.get("general_note", "")

    if not has_proj or not proj_items:
        st.warning(f"ℹ️ {proj_note if proj_note else 'No projects were identified in the uploaded resume.'}")
    else:
        for proj in proj_items:
            techs = proj.get("technologies", [])
            tech_badges = "".join([f'<span class="skill-pill-green">{t}</span>' for t in techs]) if techs else '<span style="color:#a89d9f;">Not specified</span>'
            
            st.markdown(f"""
                <div class="project-block-card">
                    <div class="proj-name-heading">🚀 {proj.get('name', 'Project')}</div>
                    <div style="margin-bottom:8px;"><b>Technologies:</b> {tech_badges}</div>
                    <div style="margin-bottom:6px; color:#e0e0e0;"><b>AI Assessment:</b> {proj.get('assessment', '')}</div>
                    <div style="margin-bottom:6px; color:#ffb74d;"><b>Improvement Area:</b> {proj.get('improvement', '')}</div>
                    <div style="color:#81c784;"><b>Resume Presentation Impact:</b> {proj.get('impact', '')}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --------------------------------------------------------
    # 8. ATS & KEYWORD INSIGHTS
    # --------------------------------------------------------
    st.markdown("### 🎯 ATS Keyword Insights")
    kw_present = keyword_insights.get("present_keywords", [])
    kw_missing = keyword_insights.get("missing_keywords", [])
    kw_improve = keyword_insights.get("improvement_keywords", [])

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown("#### ✓ Relevant Keywords Present")
        if kw_present:
            st.markdown("".join([f'<span class="skill-pill-green">✓ {k}</span>' for k in kw_present]), unsafe_allow_html=True)
        else:
            st.write("None identified.")
    with k2:
        st.markdown("#### ⚠ Keywords Missing")
        if kw_missing:
            st.markdown("".join([f'<span class="skill-pill-red">⚠ {k}</span>' for k in kw_missing]), unsafe_allow_html=True)
        else:
            st.write("No critical missing keywords.")
    with k3:
        st.markdown("#### 💡 Keywords to Better Demonstrate")
        if kw_improve:
            st.markdown("".join([f'<span class="skill-pill-yellow">💡 {k}</span>' for k in kw_improve]), unsafe_allow_html=True)
        else:
            st.write("Keywords are well demonstrated.")

    st.divider()

    # --------------------------------------------------------
    # 9. CAREER POSITIONING
    # --------------------------------------------------------
    st.markdown("### 🧭 Career Positioning")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f"**Current Profile**\n\n`{career_positioning.get('current_profile', 'Specialist')}`")
    with p2:
        st.markdown(f"**Target Role**\n\n`{career_positioning.get('target_role', target_role_display)}`")
    with p3:
        st.markdown(f"**Alignment**\n\n`{career_positioning.get('alignment', 'Moderate Alignment')}`")
    with p4:
        st.markdown(f"**Primary Gap**\n\n`{career_positioning.get('primary_gap', 'Skill alignment')}`")

    st.divider()

    # --------------------------------------------------------
    # 10. PRIORITIZED RECOMMENDATIONS
    # --------------------------------------------------------
    st.markdown("### 🚀 Personalized Prioritized Recommendations")
    high_recs = recommendations.get("high_priority", [])
    med_recs = recommendations.get("medium_priority", [])
    low_recs = recommendations.get("low_priority", [])

    if high_recs:
        st.error("🔴 **HIGH PRIORITY (Fix First)**")
        for r in high_recs:
            st.markdown(f"- {r}")

    if med_recs:
        st.warning("🟡 **MEDIUM PRIORITY (Improve Next)**")
        for r in med_recs:
            st.markdown(f"- {r}")

    if low_recs:
        st.info("🔵 **LOW PRIORITY (Polish Later)**")
        for r in low_recs:
            st.markdown(f"- {r}")

    st.divider()

    # --------------------------------------------------------
    # 11. 5-STEP ACTION PLAN
    # --------------------------------------------------------
    st.markdown("### 📋 5-Step Personalized Action Plan")
    if action_plan:
        for plan_step in action_plan:
            st.markdown(f"""
                <div class="action-step-card">
                    <div class="step-num-circle">{plan_step.get('step', '01')}</div>
                    <div>
                        <div style="font-weight:800; font-size:15px; color:#ffffff; margin-bottom:4px;">
                            {plan_step.get('title', 'Action Step')}
                        </div>
                        <div style="font-size:13px; color:#b8acae;">
                            {plan_step.get('description', '')}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
