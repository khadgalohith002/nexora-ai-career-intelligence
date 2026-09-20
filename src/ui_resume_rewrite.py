import textwrap
import importlib
import streamlit as st
import src.ai_service

try:
    from src.ai_service import generate_structured_resume_rewrite
except ImportError:
    importlib.reload(src.ai_service)
    from src.ai_service import generate_structured_resume_rewrite


def render_resume_rewrite_tab(analysis_data, resume_id=None):
    """
    Renders the premium, resume-specific AI Resume Rewrite Tab (TAB 5).
    Driven 100% by the candidate's actual uploaded resume.
    """
    # ----------------------------------------------------
    # 1. EMPTY STATE: NO RESUME UPLOADED OR ANALYZED
    # ----------------------------------------------------
    if not analysis_data or not st.session_state.get("analysis_complete", False):
        empty_html = textwrap.dedent("""
        <div style="
            margin: 25px 0; padding: 40px 30px; text-align: center;
            background: linear-gradient(145deg, rgba(22, 11, 14, 0.95), rgba(12, 9, 10, 0.95));
            border: 1px dashed rgba(255, 45, 60, 0.35); border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        ">
            <div style="font-size: 42px; margin-bottom: 12px;">✍️</div>
            <h3 style="color:#ffffff; font-family:'Space Grotesk', sans-serif; font-size:24px; margin-bottom:10px;">
                Upload your resume to unlock AI-powered rewriting.
            </h3>
            <p style="color:#a89d9f; font-size:14px; max-width:620px; margin: 0 auto 25px; line-height:1.6;">
                Upload your PDF/DOCX resume in the <b>Resume Intelligence Workspace</b> above and click <b>ANALYZE MY RESUME</b> to generate a factually accurate, ATS-optimized rewrite.
            </p>
            <div style="display:flex; justify-content:center; gap:15px; flex-wrap:wrap; text-align:left; max-width:750px; margin:0 auto;">
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:12px 16px; border-radius:8px; flex:1; min-width:200px;">
                    <div style="color:#ff5a64; font-weight:800; font-size:11px;">01 ANALYZE</div>
                    <div style="color:#ddd; font-size:12px; margin-top:4px;">Extract skills, experience & sections</div>
                </div>
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:12px 16px; border-radius:8px; flex:1; min-width:200px;">
                    <div style="color:#ff5a64; font-weight:800; font-size:11px;">02 AUDIT</div>
                    <div style="color:#ddd; font-size:12px; margin-top:4px;">Identify weak phrases & ATS gaps</div>
                </div>
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:12px 16px; border-radius:8px; flex:1; min-width:200px;">
                    <div style="color:#ff5a64; font-weight:800; font-size:11px;">03 REWRITE</div>
                    <div style="color:#ddd; font-size:12px; margin-top:4px;">Enhance bullet points & keywords</div>
                </div>
            </div>
        </div>
        """).strip()
        st.markdown(empty_html, unsafe_allow_html=True)
        return

    # Extract actual candidate resume data
    resume_text = analysis_data.get("resume_text", "")
    resume_sections = analysis_data.get("resume_sections", {})
    detected_skills = analysis_data.get("detected_skills", [])
    job_description = analysis_data.get("job_description", "")
    target_role = analysis_data.get("target_role") or analysis_data.get("target_job") or analysis_data.get("job_category") or "Software Engineer"
    overall_score = analysis_data.get("overall_score", 70)
    score_label = analysis_data.get("score_label", "Good")
    
    present_sections = {k: v for k, v in (resume_sections or {}).items() if v and str(v).strip()}
    current_resume_id = resume_id or st.session_state.get("uploaded_resume_id")

    # ----------------------------------------------------
    # RESUME CHANGE DETECTION: RESET OLD REWRITE ON NEW RESUME
    # ----------------------------------------------------
    if st.session_state.get("rewrite_active_resume_id") != current_resume_id:
        st.session_state["rewrite_results"] = None
        st.session_state["rewrite_active_resume_id"] = current_resume_id

    # ----------------------------------------------------
    # 2. PREMIUM HEADER
    # ----------------------------------------------------
    header_html = textwrap.dedent("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 15, 20, 0.95), rgba(15, 10, 12, 0.95));
        border: 1px solid rgba(255, 45, 60, 0.35);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    ">
        <div style="
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
        ">AI RESUME REWRITER</div>
        <h2 style="font-family:'Space Grotesk', sans-serif; font-size:28px; font-weight:900; color:#ffffff; margin:0 0 6px 0;">
            Transform Your Resume into a Stronger, ATS-Friendly Resume
        </h2>
        <p style="color:#b8acae; font-size:14px; margin:0; line-height:1.5;">
            Reconstruct your resume using AI-driven action verbs, keyword optimization, and executive formatting based 100% on your real experience.
        </p>
    </div>
    """).strip()
    st.markdown(header_html, unsafe_allow_html=True)

    # Compact Resume Intelligence Cards
    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.metric("Current ATS Score", f"{overall_score:.0f}%", score_label)
    with ic2:
        st.metric("Target Role", target_role)
    with ic3:
        st.metric("Skills Detected", f"{len(detected_skills)} Skills")
    with ic4:
        st.metric("Resume Sections", f"{len(present_sections)} Sections")

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 3. REWRITE CONTROLS
    # ----------------------------------------------------
    st.markdown("### 🛠️ Rewrite Controls")
    
    with st.container():
        rc_col1, rc_col2 = st.columns([2, 1], gap="medium")
        
        with rc_col1:
            target_role_input = st.text_input(
                "🎯 Target Job Role",
                value=target_role,
                key="rw_control_target_role",
            )
            
        with rc_col2:
            rewrite_mode = st.selectbox(
                "⚡ Rewrite Mode",
                options=["Professional Rewrite", "Light Polish", "ATS Optimization"],
                index=0,
                key="rw_control_mode",
            )
            
        job_desc_input = st.text_area(
            "📋 Optional Target Job Description (For keyword matching)",
            value=job_description,
            placeholder="Paste target job description here to optimize ATS keyword density...",
            height=100,
            key="rw_control_job_desc",
        )
        
        available_focus = ["Professional Summary", "Experience", "Projects", "Skills", "Education", "Achievements"]
        focus_areas = st.multiselect(
            "🎯 Focus Sections to Optimize",
            options=available_focus,
            default=["Professional Summary", "Experience", "Projects", "Skills"],
            key="rw_control_focus_areas",
        )

        btn_generate = st.button(
            "🚀 GENERATE AI REWRITE",
            key="btn_generate_ai_rewrite",
            type="primary",
            use_container_width=True,
        )

    # Trigger Generation on Click
    if btn_generate:
        with st.spinner("🤖 AI is generating a factually accurate rewrite based on your uploaded resume..."):
            res_data = generate_structured_resume_rewrite(
                resume_text=resume_text,
                resume_sections=resume_sections,
                detected_skills=detected_skills,
                target_role=target_role_input.strip() if target_role_input.strip() else target_role,
                job_description=job_desc_input.strip(),
                rewrite_mode=rewrite_mode,
                focus_areas=focus_areas,
            )
            st.session_state["rewrite_results"] = res_data

    # ----------------------------------------------------
    # 4. RENDER REWRITE RESULTS IF PRESENT
    # ----------------------------------------------------
    results = st.session_state.get("rewrite_results")

    if results:
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
        st.success("✅ AI Resume Rewrite generated successfully based 100% on your uploaded experience!")

        # ----------------------------------------------------
        # IMPROVEMENT SUMMARY (DYNAMIC STATS)
        # ----------------------------------------------------
        st.markdown("### 📊 WHAT WAS IMPROVED")
        stats = results.get("stats", {})
        
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Bullets Improved", stats.get("bullets_improved", 0))
        with s2:
            st.metric("Sections Optimized", stats.get("sections_optimized", 0))
        with s3:
            st.metric("Weak Phrases Fixed", stats.get("weak_phrases_improved", 0))
        with s4:
            st.metric("Keywords Identified", stats.get("keywords_identified", 0))

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # BEFORE → AFTER COMPARISON SECTION
        # ----------------------------------------------------
        st.markdown("### 🔄 BEFORE → AFTER Section Comparisons")
        before_after_list = results.get("before_after_comparisons", [])
        
        if before_after_list:
            for idx, item in enumerate(before_after_list):
                sec_name = item.get("section", f"Section {idx+1}")
                b_text = item.get("before", "")
                a_text = item.get("after", "")
                rationale = item.get("improvement", "")

                with st.expander(f"📍 {sec_name} Comparison", expanded=(idx == 0)):
                    ba_col1, ba_col2 = st.columns(2, gap="medium")
                    with ba_col1:
                        st.markdown(f"<div style='color:#ef4444; font-weight:800; font-size:12px; margin-bottom:6px;'>ORIGINAL (BEFORE)</div>", unsafe_allow_html=True)
                        st.info(b_text if b_text else "No original text available.")
                    with ba_col2:
                        st.markdown(f"<div style='color:#10b981; font-weight:800; font-size:12px; margin-bottom:6px;'>AI-REWRITTEN (AFTER)</div>", unsafe_allow_html=True)
                        st.success(a_text if a_text else "No rewritten text available.")
                    
                    if rationale:
                        st.markdown(f"<div style='color:#a89d9f; font-size:12px; margin-top:4px;'>💡 <b>Key Improvement:</b> {rationale}</div>", unsafe_allow_html=True)
        else:
            st.info("No section comparison data available.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # ATS OPTIMIZATION SECTION
        # ----------------------------------------------------
        st.markdown("### 🎯 ATS OPTIMIZATION & KEYWORD ANALYSIS")
        ats_data = results.get("ats_optimization", {})
        strong_kw = ats_data.get("strong_keywords", [])
        missing_kw = ats_data.get("missing_keywords", [])
        weak_ph = ats_data.get("weak_phrases", [])
        improved_ph = ats_data.get("improved_wording", [])

        ats_col1, ats_col2 = st.columns(2, gap="medium")

        with ats_col1:
            st.markdown("<h4 style='color:#10b981; font-size:15px;'>✓ Strong Existing Keywords</h4>", unsafe_allow_html=True)
            if strong_kw:
                chips = "".join([f'<span style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:4px 12px; font-size:12px; font-weight:700; margin-right:6px; display:inline-block; margin-bottom:6px;">✓ {k}</span>' for k in strong_kw])
                st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)
            else:
                st.write("None identified")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#ef4444; font-size:15px;'>⚠ Weak Phrases Replaced</h4>", unsafe_allow_html=True)
            if weak_ph:
                for wp in weak_ph:
                    st.markdown(f"<div style='color:#fca5a5; font-size:13px; margin-bottom:4px;'>❌ <i>\"{wp}\"</i></div>", unsafe_allow_html=True)
            else:
                st.write("No weak phrases flagged.")

        with ats_col2:
            st.markdown("<h4 style='color:#f59e0b; font-size:15px;'>⚠ Missing Relevant Keywords (Recommended)</h4>", unsafe_allow_html=True)
            if missing_kw:
                m_chips = "".join([f'<span style="background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); border-radius:12px; padding:4px 12px; font-size:12px; font-weight:700; margin-right:6px; display:inline-block; margin-bottom:6px;">⚠ {k}</span>' for k in missing_kw])
                st.markdown(f"<div>{m_chips}</div>", unsafe_allow_html=True)
            else:
                st.write("✓ Excellent keyword coverage for target role!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#10b981; font-size:15px;'>✓ Improved ATS Wording Used</h4>", unsafe_allow_html=True)
            if improved_ph:
                for ip in improved_ph:
                    st.markdown(f"<div style='color:#6ee7b7; font-size:13px; margin-bottom:4px;'>✓ <b>\"{ip}\"</b></div>", unsafe_allow_html=True)
            else:
                st.write("Improved ATS wording integrated throughout.")

        # Breakdown legend
        st.markdown("""
        <div style="margin-top:15px; padding:10px 16px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; font-size:12px; color:#aaa;">
            <span style="color:#10b981; font-weight:700;">✓ Already Present</span>: Skills found in candidate resume &nbsp;•&nbsp;
            <span style="color:#f59e0b; font-weight:700;">⚠ Recommended</span>: Relevant role skills suggested for future addition &nbsp;•&nbsp;
            <span style="color:#ef4444; font-weight:700;">Not Demonstrated</span>: Non-verified skills kept off resume
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # AI-REWRITTEN RESUME DISPLAY
        # ----------------------------------------------------
        st.markdown("### ✨ COMPLETE AI-REWRITTEN RESUME")
        full_resume_text = results.get("full_rewritten_resume", "")

        card_html = textwrap.dedent("""
        <div style="
            background: rgba(18, 10, 14, 0.95);
            border: 1px solid rgba(255, 45, 60, 0.3);
            border-radius: 12px;
            padding: 24px 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        ">
        """).strip()
        st.markdown(card_html, unsafe_allow_html=True)
        st.markdown(full_resume_text)
        st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # ACTION BUTTONS
        # ----------------------------------------------------
        st.markdown("### 🛠️ Actions")
        act_col1, act_col2, act_col3, act_col4 = st.columns(4)

        with act_col1:
            with st.popover("📋 Copy Markdown"):
                st.code(full_resume_text, language="markdown")

        with act_col2:
            st.download_button(
                label="📄 Download Resume",
                data=full_resume_text,
                file_name=f"{analysis_data.get('resume_name', 'Resume')}_Rewritten.md",
                mime="text/markdown",
                key="btn_download_rewritten_resume",
                use_container_width=True,
            )

        with act_col3:
            if st.button("🔄 Rewrite Again", key="btn_rewrite_again_trigger", use_container_width=True):
                with st.spinner("🤖 Re-generating resume rewrite..."):
                    res_data = generate_structured_resume_rewrite(
                        resume_text=resume_text,
                        resume_sections=resume_sections,
                        detected_skills=detected_skills,
                        target_role=target_role_input.strip() if target_role_input.strip() else target_role,
                        job_description=job_desc_input.strip(),
                        rewrite_mode=rewrite_mode,
                        focus_areas=focus_areas,
                    )
                    st.session_state["rewrite_results"] = res_data
                    st.rerun()

        with act_col4:
            if st.button("↩ Restore Original", key="btn_restore_original_resume", use_container_width=True):
                st.session_state["rewrite_results"] = None
                st.rerun()
