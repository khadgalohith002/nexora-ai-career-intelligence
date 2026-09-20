import re
from src.skill_gap_engine import analyze_skill_gap, ROLE_REQUIRED_SKILLS


def calculate_career_readiness(skill_match_score, overall_score, has_projects, candidate_level):
    """
    Calculates dynamic Career Readiness Score based on actual candidate evidence.
    Returns score int (0-100) or None if insufficient data.
    """
    if skill_match_score is None and overall_score is None:
        return None

    s_match = skill_match_score if skill_match_score is not None else 50.0
    o_score = overall_score if overall_score is not None else 50.0

    # Weighted calculation
    base_readiness = (s_match * 0.50) + (o_score * 0.35)

    if has_projects:
        base_readiness += 10.0

    if candidate_level in ["Senior-Level", "Executive"]:
        base_readiness += 5.0
    elif candidate_level in ["Mid-Level"]:
        base_readiness += 3.0

    return int(min(98, max(25, round(base_readiness))))


def get_recommended_projects_for_role(target_role, skill_gaps):
    """
    Generates personalized recommended projects based on target role and missing skill gaps.
    Labeled strictly as 'Recommended Project' (never claims user already built them).
    """
    role_lower = target_role.lower()
    gap_names = [g["skill"] if isinstance(g, dict) else g for g in skill_gaps]

    projects = []

    if any(kw in role_lower for kw in ["machine learning", "ml", "ai"]):
        gap_str = ", ".join(gap_names[:2]) if gap_names else "PyTorch & Docker"
        projects.append({
            "title": f"End-to-End AI/ML Model Serving Pipeline ({gap_str})",
            "description": f"Train a machine learning or NLP model and package it into a containerized REST API incorporating {gap_str}.",
            "outcome": "Demonstrates full MLOps pipeline lifecycle from model training to API deployment."
        })
        projects.append({
            "title": "RAG-Based Knowledge Search Application",
            "description": "Build a Retrieval-Augmented Generation (RAG) system with document vector embeddings, fast search indexing, and evaluation metrics.",
            "outcome": "Showcases modern Generative AI framework integration and vector database query handling."
        })
    elif any(kw in role_lower for kw in ["data scientist", "data analyst", "analytics"]):
        projects.append({
            "title": "Predictive Customer Analytics Dashboard",
            "description": "Analyze complex transactional datasets, engineer features, build predictive churn/classification models, and visualize key metrics.",
            "outcome": "Proves data wrangling, statistical modeling, and business insight delivery."
        })
        projects.append({
            "title": "Automated ETL Data Pipeline with SQL & Python",
            "description": "Construct an automated data ingestion and transformation pipeline feeding a structured relational data warehouse.",
            "outcome": "Validates robust backend data engineering and SQL query optimization skills."
        })
    elif any(kw in role_lower for kw in ["python", "backend", "software"]):
        projects.append({
            "title": "High-Performance Asynchronous REST API Service",
            "description": "Build a microservice backend using FastAPI/Django with relational database ORM, JWT authentication, and Docker containerization.",
            "outcome": "Demonstrates production-grade backend architecture, security, and API endpoint design."
        })
        projects.append({
            "title": "Distributed Task Queue System",
            "description": "Implement a distributed asynchronous background worker service for processing data jobs with logging and monitoring.",
            "outcome": "Proves system design capability and queue processing experience."
        })
    elif any(kw in role_lower for kw in ["devops", "cloud"]):
        projects.append({
            "title": "Automated Cloud CI/CD Infrastructure Pipeline",
            "description": "Configure infrastructure-as-code and automated CI/CD deployment pipelines deploying microservices to cloud container environments.",
            "outcome": "Demonstrates cloud automation, container orchestration, and CI/CD mastery."
        })
    else:
        projects.append({
            "title": f"Production-Grade {target_role} Showcase Application",
            "description": "Build a complete modular application solving a domain-specific problem with automated testing and clear README documentation.",
            "outcome": "Provides verifiable code proof on GitHub for hiring teams."
        })

    return projects[:2]


def generate_career_roadmap(analysis_data, selected_target_role=None, live_job_results=None):
    """
    Generates a personalized, candidate-specific Career Roadmap based on parsed resume data,
    skill gaps, target role, and optional live job market data.
    """
    if not analysis_data or not isinstance(analysis_data, dict):
        return None

    detected_skills = analysis_data.get("detected_skills", [])
    contact_info = analysis_data.get("contact_info", {})
    candidate_level = analysis_data.get("candidate_level", "Not available")
    overall_score = analysis_data.get("overall_score")
    resume_sections = analysis_data.get("resume_sections", {})
    has_projects = bool(resume_sections.get("projects"))

    target_role = (
        selected_target_role
        if selected_target_role and selected_target_role.strip()
        else (analysis_data.get("target_role") or analysis_data.get("target_job") or analysis_data.get("job_category") or "Software Engineer")
    )

    # 1. Run Skill Gap Engine to obtain candidate-specific gaps
    sg_result = analyze_skill_gap(analysis_data, selected_target_role=target_role)
    skill_match_score = sg_result.get("skill_match_score") if sg_result else None
    skill_gaps = sg_result.get("skill_gaps", []) if sg_result else []
    strong_matches = sg_result.get("strong_matches", []) if sg_result else []
    partial_matches = sg_result.get("partial_matches", []) if sg_result else []

    # 2. Dynamic Readiness Score
    readiness_score = calculate_career_readiness(
        skill_match_score=skill_match_score,
        overall_score=overall_score,
        has_projects=has_projects,
        candidate_level=candidate_level
    )

    # 3. Priority Skills Tiers
    priority_skills = []
    for idx, gap in enumerate(skill_gaps[:6]):
        p_tier = "🔴 HIGH PRIORITY" if idx < 2 else ("🟡 MEDIUM PRIORITY" if idx < 4 else "⚪ NICE TO HAVE")
        priority_skills.append({
            "skill": gap["skill"],
            "priority": p_tier,
            "reason": gap.get("reason", f"Important requirement for {target_role}."),
            "action": gap.get("action", f"Learn fundamentals of {gap['skill']} and build a proof project."),
            "outcome": f"Demonstrates verified competency in {gap['skill']} for candidate portfolio.",
            "status": "Not demonstrated in current resume"
        })

    # 4. Roadmap 4 Phases
    strong_names = [m["skill"] for m in strong_matches[:3]]
    gap_names = [g["skill"] for g in priority_skills[:3]]

    phases = [
        {
            "phase": "PHASE 1",
            "title": "STRENGTHEN",
            "focus": "Refine & highlight existing competencies",
            "description": f"Strengthen and quantify achievements using your core skills: {', '.join(strong_names) if strong_names else 'detected resume skills'}.",
            "action": "Add quantitative metrics (%, $, scale) to existing resume experience bullets."
        },
        {
            "phase": "PHASE 2",
            "title": "CLOSE SKILL GAPS",
            "focus": "Master core unDemonstrated skills",
            "description": f"Focus learning on top target gaps: {', '.join(gap_names) if gap_names else 'key target competencies'}.",
            "action": "Complete structured tutorials and practice core exercises for missing technical requirements."
        },
        {
            "phase": "PHASE 3",
            "title": "BUILD PROOF",
            "focus": "Develop verifiable project evidence",
            "description": "Construct hands-on portfolio projects showcasing your new skills on GitHub.",
            "action": "Build and document a recommended portfolio project incorporating Docker, APIs, or AI models."
        },
        {
            "phase": "PHASE 4",
            "title": "APPLY",
            "focus": "Optimize profile & target high-match jobs",
            "description": "Update your resume with new project evidence and apply to target vacancies.",
            "action": "Use Resume Rewrite to incorporate new achievements and apply to matching live opportunities."
        }
    ]

    # 5. Recommended Projects
    recommended_projects = get_recommended_projects_for_role(target_role, priority_skills)

    # 6. Job Market Connection (if live job results present in session state)
    market_demand = []
    if live_job_results and isinstance(live_job_results, list) and len(live_job_results) > 0:
        # Tally skill frequency across live job search results
        freq = {}
        for job in live_job_results:
            j_desc = (str(job.get("title", "")) + " " + str(job.get("description", ""))).lower()
            for skill in detected_skills + [g["skill"] for g in priority_skills]:
                if re.search(r'(?<![a-zA-Z0-9])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9])', j_desc):
                    freq[skill] = freq.get(skill, 0) + 1

        detected_set = {s.lower() for s in detected_skills}
        for skill_name, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]:
            demand_lvl = "High" if count >= 3 else "Medium"
            if skill_name.lower() in detected_set:
                ev_status = "Strong"
            else:
                ev_status = "Not demonstrated"
            market_demand.append({
                "skill": skill_name,
                "demand": demand_lvl,
                "evidence": ev_status
            })

    # 7. Personalized Next 5 Actions
    next_actions = [
        f"1. Quantify achievements in current resume sections using {strong_names[0] if strong_names else 'core skills'}.",
        f"2. Learn fundamentals of {priority_skills[0]['skill'] if priority_skills else 'target technical gap'}.",
        f"3. Build a recommended portfolio project demonstrating {priority_skills[0]['skill'] if priority_skills else 'key competencies'}.",
        "4. Open 'Resume Rewrite' tab to update resume bullet points with new project evidence.",
        f"5. Search live job opportunities for '{target_role}' and apply to high-match vacancies."
    ]

    return {
        "target_role": target_role,
        "candidate_level": candidate_level,
        "overall_score": overall_score,
        "skill_match_score": skill_match_score,
        "readiness_score": readiness_score,
        "detected_skills_count": len(detected_skills),
        "detected_skills": detected_skills,
        "contact_info": contact_info,
        "key_gaps_summary": [g["skill"] for g in priority_skills[:3]],
        "priority_skills": priority_skills,
        "phases": phases,
        "recommended_projects": recommended_projects,
        "market_demand": market_demand,
        "next_actions": next_actions
    }
