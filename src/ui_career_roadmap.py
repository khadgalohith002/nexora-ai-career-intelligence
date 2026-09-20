import streamlit as st
from src.roadmap_engine import generate_career_roadmap, ROLE_REQUIRED_SKILLS


def render_career_roadmap_tab(analysis_data=None):
    """
    Renders the Candidate-Specific Career Roadmap UI component.
    """
    # ---------------------------------------------------------------------
    # 18. EMPTY STATE
    # ---------------------------------------------------------------------
    if not analysis_data or not isinstance(analysis_data, dict):
        st.markdown(
            """
            <div style="background: rgba(22, 10, 14, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 40px 24px; text-align: center; margin: 20px 0;">
                <div style="font-size: 42px; margin-bottom: 12px;">🚀</div>
                <h3 style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; margin-bottom: 8px; font-weight: 700;">Career Roadmap Pending</h3>
                <p style="color: #b8abad; font-size: 15px; max-width: 550px; margin: 0 auto 20px;">Upload your resume to generate your personalized career development roadmap from your current profile to your target role.</p>
                <div style="display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 12px; color: #ff4d58; font-weight: 700; margin-top: 15px;">
                    <span>📄 Resume</span> <span>➔</span>
                    <span>👤 Profile Analysis</span> <span>➔</span>
                    <span>🧠 Skill Gaps</span> <span>➔</span>
                    <span>🎯 Target Role</span> <span>➔</span>
                    <span>🚀 Career Roadmap</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # ---------------------------------------------------------------------
    # 1. HEADER
    # ---------------------------------------------------------------------
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(20, 9, 13, 0.98) 0%, rgba(10, 5, 8, 0.99) 100%); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <span style="font-size: 28px;">🚀</span>
                <h2 style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 800; margin: 0; letter-spacing: -0.5px;">CAREER ROADMAP</h2>
            </div>
            <p style="color: #b8abad; font-size: 14px; margin: 0; line-height: 1.5;">Your personalized path from your current profile to your target career.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Target Role Selection
    default_role = (
        analysis_data.get("target_role")
        or analysis_data.get("target_job")
        or analysis_data.get("job_category")
        or "Software Engineer"
    )

    role_opts = sorted(list(ROLE_REQUIRED_SKILLS.keys()))
    if default_role not in role_opts:
        role_opts.insert(0, default_role)

    cr_col1, cr_col2 = st.columns([1.5, 1], gap="medium")
    with cr_col1:
        sel_role = st.selectbox(
            "🎯 Select Target Role for Roadmap",
            options=role_opts,
            index=role_opts.index(default_role) if default_role in role_opts else 0,
            key="rm_target_role_select"
        )
    with cr_col2:
        custom_role = st.text_input("✍️ Or Custom Role", placeholder="e.g. Lead AI Engineer", key="rm_custom_role_input")

    active_role = custom_role.strip() if custom_role.strip() else sel_role

    # Live job results from session state if available
    live_jobs_data = st.session_state.get("job_search_results", {}).get("jobs", []) if st.session_state.get("job_search_results") else None

    # Generate Roadmap
    roadmap = generate_career_roadmap(
        analysis_data=analysis_data,
        selected_target_role=active_role,
        live_job_results=live_jobs_data
    )

    if not roadmap:
        st.error("Unable to generate career roadmap.")
        return

    # Track resume changes to reset interactive progress
    current_resume_id = st.session_state.get("uploaded_resume_id", "no_resume")
    if st.session_state.get("roadmap_current_resume_id") != current_resume_id:
        st.session_state["roadmap_current_resume_id"] = current_resume_id
        st.session_state["roadmap_progress_states"] = {}

    # Initialize progress states if not present
    if "roadmap_progress_states" not in st.session_state:
        st.session_state.roadmap_progress_states = {}

    # ---------------------------------------------------------------------
    # 2. CURRENT PROFILE & READINESS SCORE
    # ---------------------------------------------------------------------
    readiness = roadmap["readiness_score"]
    s_match = roadmap["skill_match_score"]
    ats_score = roadmap["overall_score"]
    skill_cnt = roadmap["detected_skills_count"]
    exp_summary = roadmap["candidate_level"]

    p_col1, p_col2 = st.columns([1, 1.4], gap="large")

    with p_col1:
        if readiness is not None:
            st.markdown(
                f"""
                <div style="background: rgba(18, 9, 12, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 22px; text-align: center;">
                    <div style="font-size: 11px; color: #ff4d58; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">CAREER READINESS SCORE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 48px; font-weight: 900; color: #ffffff; line-height: 1;">{readiness}%</div>
                    <div style="margin-top: 14px;">
                        <div style="background: rgba(255,255,255,0.08); border-radius: 999px; height: 10px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #ff2d3c, #10b981); width: {min(100, max(0, readiness))}%; height: 100%; border-radius: 999px;"></div>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 10px;">Target: <strong>{active_role}</strong></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Insufficient data to calculate readiness.")

    with p_col2:
        st.markdown(
            f"""
            <div style="background: rgba(18, 9, 12, 0.85); border: 1px solid rgba(255, 45, 60, 0.2); border-radius: 12px; padding: 20px;">
                <div style="font-size: 13px; font-weight: 800; color: #ff4d58; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">CURRENT PROFILE OVERVIEW</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
                    <div><span style="color:#94a3b8;">Target Role:</span><br><strong style="color:#fff;">{active_role}</strong></div>
                    <div><span style="color:#94a3b8;">Skill Match:</span><br><strong style="color:#fff;">{f"{s_match:.0f}%" if s_match is not None else "Not available"}</strong></div>
                    <div><span style="color:#94a3b8;">ATS Score:</span><br><strong style="color:#fff;">{f"{ats_score:.0f}%" if ats_score is not None else "Not available"}</strong></div>
                    <div><span style="color:#94a3b8;">Detected Skills:</span><br><strong style="color:#fff;">{skill_cnt} Skills</strong></div>
                    <div><span style="color:#94a3b8;">Experience:</span><br><strong style="color:#fff;">{exp_summary}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 3. CAREER GAP OVERVIEW (WHERE YOU ARE NOW -> WHERE YOU WANT TO BE)
    # ---------------------------------------------------------------------
    gaps_summary = roadmap["key_gaps_summary"]
    gaps_badges_html = "".join([f'<span style="background:rgba(255,45,60,0.15); color:#ff4d58; border:1px solid rgba(255,45,60,0.3); padding:4px 12px; border-radius:16px; font-size:12px; font-weight:700;">{g}</span>' for g in gaps_summary]) if gaps_summary else '<span style="color:#10b981; font-size:12px;">No critical gaps</span>'

    st.markdown(
        f"""
        <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 12px; padding: 22px; margin-bottom: 24px;">
            <div style="font-size: 13px; font-weight: 800; color: #ff4d58; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px;">CAREER TRANSITION OVERVIEW</div>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; text-align: center;">
                <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px 20px; flex: 1; min-width: 150px;">
                    <div style="font-size: 10px; color: #94a3b8; font-weight: 800; text-transform: uppercase;">WHERE YOU ARE NOW</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #ffffff; margin-top: 4px;">{exp_summary}</div>
                </div>
                <div style="font-size: 24px; color: #ff4d58;">➔</div>
                <div style="background: rgba(255,45,60,0.1); border: 1px solid rgba(255,45,60,0.3); border-radius: 8px; padding: 14px 20px; flex: 1; min-width: 150px;">
                    <div style="font-size: 10px; color: #ff4d58; font-weight: 800; text-transform: uppercase;">WHERE YOU WANT TO BE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #ffffff; margin-top: 4px;">{active_role}</div>
                </div>
            </div>
            <div style="margin-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 14px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <strong style="color: #ffffff; font-size: 12px; text-transform: uppercase;">KEY GAPS TO CLOSE:</strong>
                {gaps_badges_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------------------
    # 5. PRIORITY SKILLS ("WHAT TO LEARN NEXT")
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>🔥 WHAT TO LEARN NEXT (PRIORITY SKILLS)</h3>", unsafe_allow_html=True)

    if roadmap["priority_skills"]:
        for p_item in roadmap["priority_skills"]:
            p_color = "#ef4444" if "HIGH" in p_item["priority"] else ("#f59e0b" if "MEDIUM" in p_item["priority"] else "#94a3b8")
            st.markdown(
                f"""
                <div style="background: rgba(18, 9, 12, 0.9); border: 1px solid rgba(255, 45, 60, 0.2); border-radius: 10px; padding: 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 800; color: #ffffff;">{p_item['skill']}</span>
                        <span style="background: rgba(255,255,255,0.05); color: {p_color}; border: 1px solid {p_color}44; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 16px;">{p_item['priority']}</span>
                    </div>
                    <div style="font-size: 12px; color: #fca5a5; margin-bottom: 4px;">⚠ Status: {p_item['status']}</div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;"><strong>Why:</strong> {p_item['reason']}</div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;"><strong>Action:</strong> {p_item['action']}</div>
                    <div style="font-size: 13px; color: #10b981;"><strong>Outcome:</strong> {p_item['outcome']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("No priority skill gaps identified! Your profile strongly covers this target role.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 6. ROADMAP 4 PHASES & PROGRESS TRACKER
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>🗺️ 4-PHASE DEVELOPMENT ROADMAP</h3>", unsafe_allow_html=True)

    phase_cols = st.columns(4, gap="medium")
    for idx, ph in enumerate(roadmap["phases"]):
        with phase_cols[idx]:
            st.markdown(
                f"""
                <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 10px; padding: 16px; min-height: 210px;">
                    <div style="background: rgba(255, 45, 60, 0.2); color: #ff4d58; border: 1px solid rgba(255, 45, 60, 0.4); font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 10px; display: inline-block; margin-bottom: 8px;">{ph['phase']}</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">{ph['title']}</div>
                    <div style="font-size: 11px; color: #ff4d58; font-weight: 700; margin-bottom: 8px;">{ph['focus']}</div>
                    <div style="font-size: 11px; color: #cbd5e1; line-height: 1.4; margin-bottom: 10px;">{ph['description']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Interactive Progress State for Phase
            p_key = f"roadmap_phase_{idx}_{active_role}"
            cur_p = st.session_state.roadmap_progress_states.get(p_key, "○ Not Started")
            new_p = st.selectbox(
                "Status:",
                options=["○ Not Started", "◐ In Progress", "✓ Completed"],
                index=["○ Not Started", "◐ In Progress", "✓ Completed"].index(cur_p),
                key=p_key,
                label_visibility="collapsed"
            )
            st.session_state.roadmap_progress_states[p_key] = new_p

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 8. PROJECT RECOMMENDATIONS ("BUILD TO PROVE YOUR SKILLS")
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>🛠️ BUILD TO PROVE YOUR SKILLS (RECOMMENDED PROJECTS)</h3>", unsafe_allow_html=True)

    proj_cols = st.columns(len(roadmap["recommended_projects"]))
    for idx, proj in enumerate(roadmap["recommended_projects"]):
        with proj_cols[idx]:
            st.markdown(
                f"""
                <div style="background: rgba(18, 9, 12, 0.9); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 10px; padding: 18px; min-height: 170px;">
                    <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 10px;">Recommended Project</span>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 800; color: #ffffff; margin: 8px 0 6px 0;">{proj['title']}</div>
                    <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px; line-height: 1.4;">{proj['description']}</div>
                    <div style="font-size: 11px; color: #6ee7b7;"><strong>Expected Outcome:</strong> {proj['outcome']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 9, 10, 11. CONNECTIONS TO RESUME REWRITE, JOB MARKET, & INTERVIEW
    # ---------------------------------------------------------------------
    conn_col1, conn_col2, conn_col3 = st.columns(3, gap="medium")

    with conn_col1:
        st.markdown(
            """
            <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 10px; padding: 18px; text-align: center; min-height: 170px;">
                <div style="font-size: 24px; margin-bottom: 6px;">✍️</div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">RESUME REWRITE</div>
                <p style="font-size: 11px; color: #b8abad; margin-bottom: 12px;">Once you complete these skills/projects, update your resume to reflect the new evidence.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("✨ OPEN RESUME REWRITE", key="btn_rm_goto_rewrite", use_container_width=True):
            st.session_state["pending_tab"] = "✍️ Resume Rewrite"
            st.rerun()

    with conn_col2:
        st.markdown(
            """
            <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 10px; padding: 18px; text-align: center; min-height: 170px;">
                <div style="font-size: 24px; margin-bottom: 6px;">💼</div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">LIVE JOB MATCHING</div>
                <p style="font-size: 11px; color: #b8abad; margin-bottom: 12px;">Discover live Adzuna opportunities matching your updated skillset.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("💼 VIEW MATCHING JOBS", key="btn_rm_goto_jobs", use_container_width=True):
            st.session_state["pending_tab"] = "💼 Job Vacancies"
            st.rerun()

    with conn_col3:
        st.markdown(
            """
            <div style="background: rgba(20, 9, 13, 0.95); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 10px; padding: 18px; text-align: center; min-height: 170px;">
                <div style="font-size: 24px; margin-bottom: 6px;">🎤</div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">INTERVIEW PREPARATION</div>
                <p style="font-size: 11px; color: #b8abad; margin-bottom: 12px;">Prepare for technical interview questions covering your target role.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🎯 VIEW INTERVIEW QUESTIONS", key="btn_rm_goto_interview", use_container_width=True):
            st.session_state["pending_tab"] = "🎤 Interview"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 10. JOB MARKET CONNECTION ("WHAT EMPLOYERS ARE LOOKING FOR")
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>📊 WHAT EMPLOYERS ARE LOOKING FOR (JOB MARKET DEMAND)</h3>", unsafe_allow_html=True)

    if roadmap["market_demand"]:
        st.caption("Skills demand analyzed from retrieved live Adzuna vacancies vs your resume evidence.")
        m_cols = st.columns(len(roadmap["market_demand"]))
        for idx, m_item in enumerate(roadmap["market_demand"]):
            with m_cols[idx]:
                ev_color = "#10b981" if m_item["evidence"] == "Strong" else "#ef4444"
                st.markdown(
                    f"""
                    <div style="background: rgba(18, 9, 12, 0.9); border: 1px solid rgba(255, 45, 60, 0.2); border-radius: 8px; padding: 12px; text-align: center;">
                        <div style="font-weight: 800; color: #ffffff; font-size: 13px; margin-bottom: 4px;">{m_item['skill']}</div>
                        <div style="font-size: 11px; color: #94a3b8;">Job Demand: <strong>{m_item['demand']}</strong></div>
                        <div style="font-size: 11px; color: {ev_color}; margin-top: 4px;">Resume: <strong>{m_item['evidence']}</strong></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No live job market data available. Perform a job search in the **Job Vacancies** tab to unlock live employer demand comparison.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # 12 & 13. REALISTIC TIMELINE & PERSONALIZED ACTION PLAN
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:700;'>📋 YOUR NEXT 5 ACTIONS</h3>", unsafe_allow_html=True)

    for action in roadmap["next_actions"]:
        st.markdown(
            f"""
            <div style="background: rgba(18, 9, 12, 0.85); border: 1px solid rgba(255, 45, 60, 0.2); border-radius: 8px; padding: 12px 18px; margin-bottom: 8px; color: #ffffff; font-size: 13px; font-weight: 600;">
                {action}
            </div>
            """,
            unsafe_allow_html=True
        )
