import streamlit as st
from src.skill_gap_engine import analyze_skill_gap, ROLE_REQUIRED_SKILLS


def render_skill_gap_tab(analysis_data=None):
    """
    Renders the Skill Gap Analysis UI component.
    """
    # ---------------------------------------------------------------------
    # 12. NO RESUME STATE
    # ---------------------------------------------------------------------
    if not analysis_data or not isinstance(analysis_data, dict):
        st.markdown(
            """
            <div style="background: rgba(22, 10, 14, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 40px 24px; text-align: center; margin: 20px 0;">
                <div style="font-size: 42px; margin-bottom: 12px;">🧠</div>
                <h3 style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; margin-bottom: 8px; font-weight: 700;">Skill Gap Analysis Pending</h3>
                <p style="color: #b8abad; font-size: 15px; max-width: 500px; margin: 0 auto 20px;">Upload your resume to analyze your skill gaps and get a candidate-specific learning roadmap.</p>
                <div style="display: inline-block; background: rgba(255, 45, 60, 0.15); border: 1px solid rgba(255, 45, 60, 0.4); color: #ff4d58; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600;">
                    📄 Upload a PDF or DOCX resume to unlock analysis
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # ---------------------------------------------------------------------
    # 1. HEADER & SUBTITLE
    # ---------------------------------------------------------------------
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(20, 9, 13, 0.98) 0%, rgba(10, 5, 8, 0.99) 100%); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <span style="font-size: 28px;">🧠</span>
                <h2 style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 800; margin: 0; letter-spacing: -0.5px;">SKILL GAP ANALYSIS</h2>
            </div>
            <p style="color: #b8abad; font-size: 14px; margin: 0; line-height: 1.5;">Understand where you stand today and what skills you need to reach your target role.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------------------
    # 3. TARGET ROLE SELECTION & JD MODE
    # ---------------------------------------------------------------------
    default_role = (
        analysis_data.get("target_role")
        or analysis_data.get("target_job")
        or analysis_data.get("job_category")
        or "AI Engineer"
    )

    role_options = sorted(list(ROLE_REQUIRED_SKILLS.keys()))
    if default_role not in role_options:
        role_options.insert(0, default_role)

    col_role, col_custom = st.columns([1.5, 1], gap="medium")

    with col_role:
        selected_role = st.selectbox(
            "🎯 Select or Modify Target Role",
            options=role_options,
            index=role_options.index(default_role) if default_role in role_options else 0,
            key="sg_target_role_select"
        )

    with col_custom:
        custom_role_input = st.text_input(
            "✍️ Or Type Custom Target Role",
            placeholder="e.g. Lead MLOps Engineer",
            key="sg_custom_role_input"
        )

    active_target_role = custom_role_input.strip() if custom_role_input.strip() else selected_role

    # Run Skill Gap Engine
    custom_jd = analysis_data.get("job_description", "")
    sg_result = analyze_skill_gap(
        analysis_data=analysis_data,
        selected_target_role=active_target_role,
        custom_job_description=custom_jd
    )

    if not sg_result:
        st.error("Could not calculate skill gap analysis.")
        return

    # Job Description Mode Banner
    if sg_result["is_jd_mode"]:
        st.markdown(
            """
            <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; color: #60a5fa; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                <span>🎯</span> <strong>JOB DESCRIPTION MODE ACTIVE:</strong> Target skills are dynamically extracted from your supplied Job Description.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------------------------------------------------------------
    # 6. SKILL MATCH SCORE & SUMMARY METRICS
    # ---------------------------------------------------------------------
    score = sg_result["skill_match_score"]
    strong_count = len(sg_result["strong_matches"])
    partial_count = len(sg_result["partial_matches"])
    gap_count = len(sg_result["skill_gaps"])

    score_col, metrics_col = st.columns([1, 1.5], gap="large")

    with score_col:
        st.markdown(
            f"""
            <div style="background: rgba(18, 9, 12, 0.9); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 12px; color: #ff4d58; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">SKILL MATCH SCORE</div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 46px; font-weight: 900; color: #ffffff; line-height: 1;">{score:.0f}%</div>
                <div style="margin-top: 14px;">
                    <div style="background: rgba(255,255,255,0.08); border-radius: 999px; height: 10px; overflow: hidden; position: relative;">
                        <div style="background: linear-gradient(90deg, #ff2d3c, #ff6b75); width: {min(100.0, max(0.0, score))}%; height: 100%; border-radius: 999px;"></div>
                    </div>
                </div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 8px;">Role: <strong>{active_target_role}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metrics_col:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("🟢 Strong Matches", f"{strong_count}")
        with m2:
            st.metric("🟡 Partial Matches", f"{partial_count}")
        with m3:
            st.metric("🔴 Skill Gaps", f"{gap_count}")

        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px 16px; margin-top: 10px; font-size: 13px; color: #cbd5e1;">
                <strong>Resume Coverage:</strong> Demonstrated <strong>{strong_count}</strong> direct competencies and <strong>{partial_count}</strong> related skills out of <strong>{len(sg_result['required_skills'])}</strong> required competencies for <em>{active_target_role}</em>.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 2. CURRENT SKILLS (DETECTED FROM RESUME)
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>📄 DETECTED RESUME SKILLS</h3>", unsafe_allow_html=True)
    st.caption("Only skills explicitly supported by the uploaded resume are displayed below.")

    categorized = sg_result["categorized_current_skills"]

    if not categorized:
        st.info("No technical skills were explicitly detected in the uploaded resume.")
    else:
        cat_cols = st.columns(len(categorized))
        for idx, (cat_name, cat_skills) in enumerate(categorized.items()):
            with cat_cols[idx % len(cat_cols)]:
                st.markdown(
                    f"""
                    <div style="background: rgba(18, 9, 12, 0.85); border: 1px solid rgba(255, 45, 60, 0.2); border-radius: 10px; padding: 14px; min-height: 140px;">
                        <div style="font-size: 12px; font-weight: 700; color: #ff4d58; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">{cat_name}</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            {''.join([f'<span style="background:rgba(255,255,255,0.06); color:#f8fafc; border:1px solid rgba(255,255,255,0.12); padding:3px 9px; border-radius:6px; font-size:11px; font-weight:600;">{s}</span>' for s in cat_skills])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 5. SKILL MATCH MATRIX (STRONG MATCH vs PARTIAL MATCH vs SKILL GAP)
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>⚖️ COMPETENCY MATCH BREAKDOWN</h3>", unsafe_allow_html=True)

    col_strong, col_partial, col_gaps = st.columns(3, gap="medium")

    with col_strong:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 16px;">
                <div style="font-size: 14px; font-weight: 700; color: #10b981; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>🟢</span> STRONG MATCHES
                </div>
            """,
            unsafe_allow_html=True
        )

        if sg_result["strong_matches"]:
            for item in sg_result["strong_matches"]:
                ev_str = f"<div style='font-size:10px; color:#a7f3d0; margin-top:4px;'>✓ Demonstrated in: {', '.join(item['evidence'][:2]) if item['evidence'] else 'Resume Content'}</div>"
                st.markdown(
                    f"""
                    <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 8px 12px; margin-bottom: 8px;">
                        <div style="font-size: 13px; font-weight: 700; color: #ffffff;">{item['skill']}</div>
                        {ev_str}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<div style='font-size:12px; color:#94a3b8;'>No direct strong matches identified.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_partial:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 16px;">
                <div style="font-size: 14px; font-weight: 700; color: #f59e0b; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>🟡</span> PARTIAL MATCHES
                </div>
            """,
            unsafe_allow_html=True
        )

        if sg_result["partial_matches"]:
            for item in sg_result["partial_matches"]:
                st.markdown(
                    f"""
                    <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 8px 12px; margin-bottom: 8px;">
                        <div style="font-size: 13px; font-weight: 700; color: #ffffff;">{item['skill']}</div>
                        <div style="font-size: 10px; color: #fde68a; margin-top: 4px;">{item['reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<div style='font-size:12px; color:#94a3b8;'>No partial matches identified.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_gaps:
        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 16px;">
                <div style="font-size: 14px; font-weight: 700; color: #ef4444; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>🔴</span> SKILL GAPS
                </div>
            """,
            unsafe_allow_html=True
        )

        if sg_result["skill_gaps"]:
            for item in sg_result["skill_gaps"]:
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 6px; padding: 8px 12px; margin-bottom: 8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size: 13px; font-weight: 700; color: #ffffff;">{item['skill']}</span>
                            <span style="font-size: 9px; font-weight: 700; background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 2px 6px; border-radius: 4px;">{item['priority']}</span>
                        </div>
                        <div style="font-size: 10px; color: #fca5a5; margin-top: 4px;">⚠ Not demonstrated in resume</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<div style='font-size:12px; color:#10b981;'>No skill gaps identified! Excellent coverage.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 7. TOP SKILL GAPS & RECOMMENDATIONS
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>🔥 TOP SKILL GAPS & ACTIONABLE RECOMMENDATIONS</h3>", unsafe_allow_html=True)

    if sg_result["top_gaps"]:
        for gap in sg_result["top_gaps"]:
            p_color = "#ef4444" if gap["priority"] == "HIGH PRIORITY" else ("#f59e0b" if gap["priority"] == "MEDIUM PRIORITY" else "#94a3b8")
            st.markdown(
                f"""
                <div style="background: rgba(18, 9, 12, 0.9); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 10px; padding: 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 800; color: #ffffff;">{gap['skill']}</span>
                        <span style="background: rgba(255,255,255,0.06); color: {p_color}; border: 1px solid {p_color}44; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px;">{gap['priority']}</span>
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;">
                        <strong style="color: #ff4d58;">Reason:</strong> {gap['reason']}
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1;">
                        <strong style="color: #10b981;">Recommended Action:</strong> {gap['action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("Great job! Your resume demonstrates all key skills required for this target role.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 9. LEARNING ROADMAP
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>🗺️ WHAT SHOULD I LEARN NEXT?</h3>", unsafe_allow_html=True)
    st.caption("Sequential step-by-step learning progression designed for maximum career impact.")

    if sg_result["roadmap_steps"]:
        r_cols = st.columns(len(sg_result["roadmap_steps"]))
        for idx, step in enumerate(sg_result["roadmap_steps"]):
            with r_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 10px; padding: 16px; text-align: center; min-height: 180px;">
                        <div style="background: rgba(255, 45, 60, 0.2); color: #ff4d58; border: 1px solid rgba(255, 45, 60, 0.4); font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 12px; display: inline-block; margin-bottom: 10px;">{step['step']}</div>
                        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #ffffff; margin-bottom: 8px;">{step['skill']}</div>
                        <div style="font-size: 11px; color: #94a3b8; line-height: 1.4;">{step['action']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No learning steps required for current role coverage.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 22px; text-align: center; margin-top: 15px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">READY TO BUILD YOUR PERSONALIZED ROADMAP?</div>
            <p style="font-size: 13px; color: #b8abad; margin-bottom: 16px;">Turn these skill gaps into an actionable 4-phase career plan with proof projects.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🚀 VIEW FULL CAREER ROADMAP", key="btn_sg_goto_roadmap", use_container_width=True):
        st.session_state["pending_tab"] = "🚀 Career Roadmap"
        st.rerun()
