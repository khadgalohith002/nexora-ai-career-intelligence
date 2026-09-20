import datetime
import streamlit as st
from src.job_service import (
    search_live_jobs_uncached,
    infer_target_role,
    calculate_advanced_job_match,
    get_relative_posted_date,
    is_job_within_age,
    parse_created_timestamp,
)


def render_job_vacancies_tab(analysis_data=None):
    """
    Renders the Real-Time, Resume-Aware Job Vacancies & Job Matching tab.
    Guarantees fresh, uncached Adzuna API job searches on every explicit search or refresh.
    """
    st.markdown(
        '<div style="background: linear-gradient(135deg, rgba(20, 9, 13, 0.98) 0%, rgba(10, 5, 8, 0.99) 100%); border: 1px solid rgba(255, 45, 60, 0.3); border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"><div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;"><div style="display: flex; align-items: center; gap: 12px;"><span style="font-size: 28px;">💼</span><div><h2 style="color: #ffffff; font-family: \'Space Grotesk\', sans-serif; font-size: 26px; font-weight: 800; margin: 0; letter-spacing: -0.5px;">LIVE JOB SEARCH</h2><p style="color: #b8abad; font-size: 14px; margin: 4px 0 0 0;">Latest listings returned by Adzuna across India, matched against your resume.</p></div></div><div style="font-size: 11px; color: #64748b; background: rgba(255,255,255,0.05); padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">Source: <strong>Adzuna</strong></div></div></div>',
        unsafe_allow_html=True
    )

    has_analysis = bool(analysis_data and isinstance(analysis_data, dict) and analysis_data.get("detected_skills"))

    # Resume-aware default target role suggestion
    suggested_role = ""
    if has_analysis:
        suggested_role = (
            analysis_data.get("target_role")
            or analysis_data.get("target_job")
            or infer_target_role(
                resume_text=analysis_data.get("resume_text", ""),
                detected_skills=analysis_data.get("detected_skills", []),
                job_category=analysis_data.get("job_category")
            )
        )
    else:
        suggested_role = "Python Developer"

    # Track resume changes to invalidate old matching cache if resume ID changes
    current_resume_id = st.session_state.get("uploaded_resume_id", "no_resume")
    if st.session_state.get("job_current_resume_id") != current_resume_id:
        st.session_state["job_current_resume_id"] = current_resume_id
        if "job_search_results" in st.session_state and st.session_state.job_search_results:
            st.session_state.job_search_results["matched_jobs"] = None

    # Initialize job search state variables
    if "job_search_results" not in st.session_state:
        st.session_state.job_search_results = None

    # ============================================================
    # SEARCH CONTROLS
    # ============================================================
    st.markdown("<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:17px; font-weight:700;'>🔎 LIVE JOB SEARCH CONTROLS</h3>", unsafe_allow_html=True)

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2.2, 1.5, 1.8, 1], gap="medium")

    with ctrl_col1:
        target_role_input = st.text_input(
            "🎯 Target Role / Job Title",
            value=suggested_role,
            placeholder="e.g. Machine Learning Engineer, Python Developer",
            key="jv_target_role"
        )

    with ctrl_col2:
        locations_list = ["India", "Bangalore", "Hyderabad", "Chennai", "Mumbai", "Pune", "Delhi", "Remote"]
        location_input = st.selectbox(
            "📍 Location",
            options=locations_list,
            index=0,
            key="jv_location"
        )

    with ctrl_col3:
        keywords_input = st.text_input(
            "⚡ Additional Keywords (optional)",
            placeholder="e.g. PyTorch, Docker, FastAPI",
            key="jv_keywords"
        )

    with ctrl_col4:
        results_per_page = st.selectbox(
            "🔢 Display Limit",
            options=[10, 20, 30, 50],
            index=1,
            key="jv_results_count"
        )

    btn_col1, btn_col2 = st.columns([2, 1], gap="medium")

    with btn_col1:
        trigger_search = st.button("🔎 SEARCH LIVE JOBS", key="btn_search_live_jobs", type="primary", use_container_width=True)
    with btn_col2:
        trigger_refresh = st.button("↻ REFRESH LIVE JOBS", key="btn_refresh_live_jobs", use_container_width=True)

    # Combine search query string
    search_keyword = target_role_input.strip()
    if keywords_input.strip():
        search_keyword = f"{search_keyword} {keywords_input.strip()}".strip()

    # Track search parameter changes
    current_search_params = (search_keyword, location_input.strip() if location_input else "India")
    last_search_params = st.session_state.get("job_last_search_params")

    # ============================================================
    # EXPLICIT UNCACHED SEARCH / REFRESH API EXECUTION
    # ============================================================
    should_execute_api = (
        trigger_search
        or trigger_refresh
        or (st.session_state.job_search_results is None and search_keyword)
    )

    if should_execute_api:
        if not search_keyword:
            st.warning("Please enter a target role or job title to search live jobs.")
        else:
            with st.spinner("🔄 Fetching fresh opportunities from Adzuna API..."):
                # Clear previous displayed jobs before fresh search to guarantee no stale results
                previous_results = st.session_state.get("job_search_results")
                
                res_payload = search_live_jobs_uncached(
                    keyword=search_keyword,
                    location=location_input.strip() if location_input else "India",
                    results_per_page=50  # Request larger pool (50) from Adzuna API
                )

                fetch_time = datetime.datetime.now().strftime("%H:%M:%S")

                if res_payload.get("error"):
                    st.error("❌ Unable to fetch fresh job listings right now.")
                    if previous_results and previous_results.get("jobs"):
                        # Keep previous results clearly marked as un-refreshed fallback
                        st.warning("⚠️ Previous successful results — refresh failed.")
                        st.session_state.job_search_results["fetch_failed"] = True
                    else:
                        st.session_state.job_search_results = {
                            "jobs": [],
                            "error": "Unable to fetch fresh job listings right now.",
                            "count": 0,
                            "timestamp": fetch_time,
                            "fetch_failed": True
                        }
                else:
                    res_payload["timestamp"] = fetch_time
                    res_payload["fetch_failed"] = False
                    st.session_state.job_search_results = res_payload
                    st.session_state.job_last_search_params = current_search_params
                    st.toast("🔴 FRESH SEARCH completed!", icon="🎉")

    # Retrieve current search results payload
    res_data = st.session_state.get("job_search_results")

    if res_data is None:
        st.info("Click **SEARCH LIVE JOBS** to query real-time job vacancies.")
        return

    fetch_failed = res_data.get("fetch_failed", False)
    error_msg = res_data.get("error")
    jobs_list = res_data.get("jobs", [])
    total_count = res_data.get("count", len(jobs_list))
    fetch_time = res_data.get("timestamp", datetime.datetime.now().strftime("%H:%M:%S"))

    if error_msg and not jobs_list:
        st.error(f"❌ Unable to fetch fresh job listings right now.")
        if st.button("🔄 Retry Search", key="btn_retry_search"):
            st.rerun()
        return

    # ============================================================
    # LIVE STATUS BADGE & COUNTER
    # ============================================================
    if fetch_failed:
        status_html = (
            f'<div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); padding: 6px 14px; border-radius: 20px;">'
            f'<span style="color: #f59e0b; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;">⚠️ PREVIOUS RESULTS — REFRESH FAILED</span>'
            f'<span style="color: #fbbf24; font-size: 11px;">• Last fetched: {fetch_time}</span>'
            f'<span style="color: #94a3b8; font-size: 11px;">• Source: Adzuna</span>'
            f'</div>'
        )
    else:
        status_html = (
            f'<div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); padding: 6px 14px; border-radius: 20px;">'
            f'<span style="color: #ef4444; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;">🔴 FRESH SEARCH</span>'
            f'<span style="color: #fca5a5; font-size: 11px;">• Fetched: {fetch_time}</span>'
            f'<span style="color: #cbd5e1; font-size: 11px;">• Source: Adzuna</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin: 18px 0 14px;">'
        f'{status_html}'
        f'<div style="color: #cbd5e1; font-size: 13px; font-weight: 600;">{len(jobs_list)} total listings returned by Adzuna.</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not jobs_list:
        st.info("No matching jobs were returned by Adzuna for this search.")
        return

    # ============================================================
    # ADVANCED RESUME-TO-JOB MATCHING CALCULATIONS
    # ============================================================
    for job in jobs_list:
        match_data = calculate_advanced_job_match(job, analysis_data if has_analysis else None)
        job["match_score"] = match_data.get("match_score")
        job["matching_skills"] = match_data.get("matching_skills", [])
        job["partial_matches"] = match_data.get("partial_matches", [])
        job["skill_gaps"] = match_data.get("skill_gaps", [])
        job["why_matches"] = match_data.get("why_matches", [])

    # ============================================================
    # LOCAL FILTERS & SORTING (ZERO API CALLS)
    # ============================================================
    with st.expander("🛠️ Local Filters & Sorting (No API calls)", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.2, 1.2, 1.2], gap="medium")

        with f_col1:
            sort_options = [
                "📅 Newest",
                "🎯 Best Resume Match" if has_analysis else "📅 Newest",
                "💰 Highest Salary",
                "💰 Lowest Salary"
            ]
            # Remove duplicate options
            sort_options = list(dict.fromkeys(sort_options))
            sort_selection = st.selectbox("Sort by:", options=sort_options, index=0, key="jv_sort_sel")

        with f_col2:
            age_filter_map = {
                "30 days": 30,
                "24 hours": 1,
                "3 days": 3,
                "7 days": 7,
                "14 days": 14,
                "Any": None
            }
            age_selection = st.selectbox(
                "Maximum Job Age",
                options=list(age_filter_map.keys()),
                index=0,
                key="jv_max_age_filter"
            )
            max_age_days = age_filter_map[age_selection]

        with f_col3:
            min_match_filter = st.slider(
                "Min Match %",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                key="jv_min_match_slider"
            )

        all_cats = sorted(list(set(j.get("category", "General") for j in jobs_list if j.get("category"))))
        all_companies = sorted(list(set(j.get("company", "") for j in jobs_list if j.get("company"))))

        with f_col4:
            cat_filter = st.multiselect("Category", options=all_cats, key="jv_cat_filter")
            comp_filter = st.multiselect("Company", options=all_companies, key="jv_comp_filter")

    # 1. Apply Freshness Filter (Maximum Job Age)
    fresh_jobs = [j for j in jobs_list if is_job_within_age(j.get("created", ""), max_age_days)]

    if not fresh_jobs:
        st.warning("No listings matching this freshness filter were returned.")
        return

    # 2. Apply Local Category, Company, Min Match Filters
    filtered_jobs = fresh_jobs[:]

    if min_match_filter > 0 and has_analysis:
        filtered_jobs = [j for j in filtered_jobs if (j.get("match_score") or 0) >= min_match_filter]

    if cat_filter:
        filtered_jobs = [j for j in filtered_jobs if j.get("category") in cat_filter]

    if comp_filter:
        filtered_jobs = [j for j in filtered_jobs if j.get("company") in comp_filter]

    if not filtered_jobs:
        st.warning("No live jobs match your local filter criteria. Try adjusting the filters above.")
        return

    # 3. Apply Local Sorting
    if sort_selection == "📅 Newest":
        filtered_jobs.sort(key=lambda j: j.get("parsed_dt") or parse_created_timestamp(j.get("created", "")), reverse=True)
    elif "Best Resume Match" in sort_selection and has_analysis:
        filtered_jobs.sort(key=lambda j: j.get("match_score") or 0, reverse=True)
    elif sort_selection == "💰 Highest Salary":
        filtered_jobs.sort(key=lambda j: j.get("salary_max") or j.get("salary_min") or 0, reverse=True)
    elif sort_selection == "💰 Lowest Salary":
        filtered_jobs.sort(key=lambda j: j.get("salary_min") or j.get("salary_max") or float('inf'))

    # Limit displayed pool to results_per_page
    displayed_jobs = filtered_jobs[:results_per_page]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#ffffff; font-family:\"Space Grotesk\", sans-serif; font-size:18px; font-weight:800;'>🏆 LATEST JOB OPPORTUNITIES ({len(displayed_jobs)} displayed)</h3>", unsafe_allow_html=True)

    # ============================================================
    # PREMIUM LIVE JOB CARDS
    # ============================================================
    for idx, job in enumerate(displayed_jobs):
        j_title = job.get("title", "Untitled Position")
        j_company = job.get("company", "Company not specified")
        j_location = job.get("location", location_input)
        j_salary = job.get("salary", "Salary not disclosed")
        j_category = job.get("category", "General")
        j_created = job.get("created", "")
        j_url = job.get("url", "")
        j_match = job.get("match_score")
        j_desc = job.get("description", "")
        j_why = job.get("why_matches", [])
        j_matching_skills = job.get("matching_skills", [])
        j_partial_matches = job.get("partial_matches", [])
        j_skill_gaps = job.get("skill_gaps", [])

        posted_date_str = job.get("posted_date_str") or get_relative_posted_date(j_created)

        # Single-line Match Badge HTML
        if has_analysis and j_match is not None:
            match_badge_html = f'<div style="background: rgba(255, 45, 60, 0.15); border: 1px solid rgba(255, 45, 60, 0.4); color: #ff4d58; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 13px; font-family: \'Space Grotesk\', sans-serif;">🎯 RESUME MATCH: {j_match}%</div>'
        else:
            match_badge_html = '<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); color: #94a3b8; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 12px;">💡 Upload a resume to unlock match score</div>'

        clean_desc = j_desc[:320] + ('...' if len(j_desc) > 320 else '')

        # Construct single-line card HTML to avoid Streamlit code block parsing
        card_html = (
            f'<div style="background: rgba(18, 9, 12, 0.95); border: 1px solid rgba(255, 45, 60, 0.25); border-radius: 12px; padding: 22px; margin-bottom: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">'
            f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">'
            f'<div><div style="font-family: \'Space Grotesk\', sans-serif; font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">💼 {j_title}</div><div style="color: #ff4d58; font-size: 14px; font-weight: 700;">🏢 {j_company}</div></div>'
            f'{match_badge_html}'
            f'</div>'
            f'<div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 14px; font-size: 12px; color: #cbd5e1;">'
            f'<span>📍 {j_location}</span><span>💰 {j_salary}</span><span>📅 {posted_date_str}</span><span>Source: Adzuna</span><span>🏷️ {j_category}</span>'
            f'</div>'
            f'<div style="color: #b8abad; font-size: 13px; line-height: 1.6; margin-bottom: 14px;">{clean_desc}</div>'
            f'</div>'
        )

        st.markdown(card_html, unsafe_allow_html=True)

        # Match Explanations & Skills Detail
        if has_analysis:
            exp_col, skills_col = st.columns([1, 1], gap="medium")

            with exp_col:
                st.markdown("<div style='font-size:12px; font-weight:700; color:#ff4d58; text-transform:uppercase; margin-bottom:6px;'>WHY THIS JOB MATCHES YOU</div>", unsafe_allow_html=True)
                for why in j_why[:3]:
                    st.markdown(f"<div style='font-size:11px; color:#e2e8f0; margin-bottom:4px;'>✓ {why}</div>", unsafe_allow_html=True)

            with skills_col:
                if j_matching_skills:
                    m_chips = "".join([f'<span style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:2px 8px; font-size:10px; font-weight:700; margin-right:4px; margin-bottom:4px; display:inline-block;">✓ {s}</span>' for s in j_matching_skills[:5]])
                    st.markdown(f"<div style='margin-bottom:6px;'><b style='color:#10b981; font-size:11px;'>MATCHING SKILLS:</b><br>{m_chips}</div>", unsafe_allow_html=True)

                if j_partial_matches:
                    p_chips = "".join([f'<span style="background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); border-radius:12px; padding:2px 8px; font-size:10px; font-weight:700; margin-right:4px; margin-bottom:4px; display:inline-block;">⚠ {p["skill"]}</span>' for p in j_partial_matches[:3]])
                    st.markdown(f"<div style='margin-bottom:6px;'><b style='color:#f59e0b; font-size:11px;'>PARTIAL MATCHES:</b><br>{p_chips}</div>", unsafe_allow_html=True)

                if j_skill_gaps:
                    g_chips = "".join([f'<span style="background:rgba(239,68,68,0.15); color:#fca5a5; border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:2px 8px; font-size:10px; font-weight:700; margin-right:4px; margin-bottom:4px; display:inline-block;">{g["priority"]} {g["skill"]}</span>' for g in j_skill_gaps[:4]])
                    st.markdown(f"<div style='margin-bottom:6px;'><b style='color:#ef4444; font-size:11px;'>SKILL GAPS:</b><br>{g_chips}</div>", unsafe_allow_html=True)

        # Real Adzuna redirect URL link button
        if j_url:
            st.link_button(
                "VIEW JOB →",
                j_url,
                key=f"btn_apply_job_{job.get('id', idx)}_{idx}"
            )

        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin:18px 0;'>", unsafe_allow_html=True)
