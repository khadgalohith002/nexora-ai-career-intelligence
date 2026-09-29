import streamlit as st
from src.interview_engine import generate_suggested_interview_questions, extract_candidate_name

def render_interview_tab(analysis_data, resume_id=None):
    """
    Renders a premium, clean, 100% candidate-specific SUGGESTED INTERVIEW QUESTIONS dashboard.
    No interactive interview session, no exam timers, no forced text inputs, no test scores.
    """
    if not analysis_data or not isinstance(analysis_data, dict):
        render_empty_interview_state()
        return

    target_job = analysis_data.get("target_job", "Target Position")
    cleaned_resume = analysis_data.get("cleaned_resume", "")
    contact_info = analysis_data.get("contact_info", {})
    candidate_name = extract_candidate_name(cleaned_resume, contact_info)

    current_resume_key = resume_id if resume_id else f"{analysis_data.get('resume_name', 'res')}_{len(cleaned_resume)}"
    
    # Generate questions ONCE per uploaded resume
    if "suggested_questions" not in st.session_state or st.session_state.get("suggested_resume_key") != current_resume_key:
        st.session_state.suggested_questions = generate_suggested_interview_questions(analysis_data, target_job, analysis_data.get("job_description", ""))
        st.session_state["suggested_resume_key"] = current_resume_key

    questions = st.session_state.suggested_questions
    if not questions or not isinstance(questions, list):
        st.warning("⚠️ No suggested questions generated yet. Please re-run resume analysis.")
        return

    # Custom Styling
    st.markdown("""
        <style>
        .suggested-header-card {
            background: #111827;
            border: 1px solid #263247;
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .ai-aware-badge {
            display: inline-block;
            color: #3B82F6;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 4px 14px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 999px;
            margin-bottom: 10px;
        }
        .suggested-main-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(24px, 3.2vw, 34px);
            font-weight: 800;
            color: #F8FAFC;
            margin: 0 0 6px 0;
        }
        .suggested-main-sub {
            color: #CBD5E1;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .info-pill-bar {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .info-pill-item {
            background: #172033;
            border: 1px solid #263247;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            color: #CBD5E1;
        }
        .info-pill-item b {
            color: #3B82F6;
        }
        .q-card-premium {
            background: #172033;
            border: 1px solid #263247;
            border-radius: 10px;
            padding: 20px 24px;
            margin-bottom: 14px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .q-card-premium:hover {
            transform: translateY(-2px);
            border-color: #3B82F6;
        }
        .q-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .q-number-lbl {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 800;
            color: #3B82F6;
            font-size: 16px;
        }
        .q-category-tag {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #3B82F6;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 999px;
        }
        .q-priority-tag {
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .q-body-text {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(15px, 1.8vw, 19px);
            font-weight: 700;
            color: #F8FAFC;
            line-height: 1.4;
            margin-bottom: 12px;
        }
        .based-on-footer {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #111827;
            border: 1px solid #263247;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 12px;
            color: #CBD5E1;
        }
        .based-on-footer b {
            color: #3B82F6;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. HEADER BANNER
    st.markdown(f"""
        <div class="suggested-header-card">
            <div class="ai-aware-badge">AI-POWERED • RESUME-AWARE</div>
            <div class="suggested-main-title">🎯 SUGGESTED INTERVIEW QUESTIONS</div>
            <div class="suggested-main-sub">Prepare for the questions most likely to be asked from your resume and target role.</div>
            <div class="info-pill-bar">
                <div class="info-pill-item"><b>TARGET ROLE:</b> {target_job}</div>
                <div class="info-pill-item"><b>CANDIDATE:</b> {candidate_name}</div>
                <div class="info-pill-item"><b>TOTAL QUESTIONS:</b> {len(questions)} Personalized Questions</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. LOCAL CATEGORY FILTERING
    categories_available = ["ALL"] + list(dict.fromkeys([q.get("category", "GENERAL") for q in questions]))
    
    selected_cat = st.radio(
        "Filter Category",
        options=categories_available,
        horizontal=True,
        key="suggested_cat_filter",
        label_visibility="collapsed"
    )

    # Filter questions locally
    if selected_cat != "ALL":
        filtered_questions = [q for q in questions if q.get("category") == selected_cat]
    else:
        filtered_questions = questions

    st.markdown("<br>", unsafe_allow_html=True)

    # Group filtered questions by Priority
    high_prio = [q for q in filtered_questions if "HIGH" in q.get("priority", "")]
    important_prio = [q for q in filtered_questions if "IMPORTANT" in q.get("priority", "")]
    other_prio = [q for q in filtered_questions if q not in high_prio and q not in important_prio]

    def render_question_list(q_list):
        for q in q_list:
            q_num = q.get("id", 1)
            q_cat = q.get("category", "TECHNICAL")
            q_text = q.get("question", "")
            q_prio = q.get("priority", "⭐ IMPORTANT")
            based_on = q.get("based_on", "Resume Analysis")

            st.markdown(f"""
                <div class="q-card-premium">
                    <div class="q-card-header">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span class="q-number-lbl">{q_num:02d}</span>
                            <span class="q-category-tag">{q_cat}</span>
                        </div>
                        <span class="q-priority-tag">{q_prio}</span>
                    </div>
                    <div class="q-body-text">"{q_text}"</div>
                    <div class="based-on-footer">
                        <span>Based on:</span> <b>{based_on}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if high_prio:
        st.markdown("### 🔥 HIGH PRIORITY")
        render_question_list(high_prio)

    if important_prio:
        st.markdown("### ⭐ IMPORTANT")
        render_question_list(important_prio)

    if other_prio:
        st.markdown("### ○ GOOD TO PREPARE")
        render_question_list(other_prio)

    st.divider()

    # 3. PREPARATION TIP BANNER
    st.info('💡 **PREPARATION TIP:** "Be prepared to explain every important technology, project, and achievement listed on your resume."')

    # 4. COPY / EXPORT QUESTIONS
    with st.expander("📋 Copy / Export Questions List"):
        copy_text = f"TARGET ROLE: {target_job}\nCANDIDATE: {candidate_name}\n" + "="*50 + "\n\n"
        for idx, q in enumerate(questions, 1):
            copy_text += f"{idx:02d}. [{q.get('category')}] ({q.get('priority')})\n"
            copy_text += f"Question: {q.get('question')}\n"
            copy_text += f"Based on: {q.get('based_on')}\n\n"
            
        st.text_area("Plaintext Questions List", value=copy_text, height=220, label_visibility="collapsed")


def render_empty_interview_state():
    """
    Renders empty state when no resume has been uploaded/analyzed.
    """
    st.markdown("""
        <div class="suggested-header-card">
            <div class="ai-aware-badge">AI-POWERED • RESUME-AWARE</div>
            <div class="suggested-main-title">🎯 SUGGESTED INTERVIEW QUESTIONS</div>
            <div class="suggested-main-sub">Upload and analyze your resume to generate personalized interview questions.</div>
        </div>
    """, unsafe_allow_html=True)

    st.info("""
    ### 🔓 What gets unlocked after uploading your resume:
    - **✓ Resume-Specific Questions**: Direct questions referencing your actual projects and work experience.
    - **✓ Technical Questions**: Questions tailored to your core technical tools and frameworks.
    - **✓ Project Deep Dives**: Architecture and trade-off questions for your projects.
    - **✓ Target-Role Questions**: Position-specific questions tailored to your target job.
    - **✓ Behavioral Questions**: Scenario questions based on your background.
    """)
