import re
import datetime
import streamlit as st
from src.adzuna_jobs import search_jobs
from src.skill_extractor import extract_skills
from src.skill_gap_engine import RELATED_SKILL_MAP

COMMON_TECH_SKILLS = [
    "Python", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
    "JavaScript", "TypeScript", "React", "Angular", "Vue", "Next.js", "Node.js",
    "Django", "Flask", "FastAPI", "Spring Boot", "GraphQL", "REST API",
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "CI/CD",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka",
    "PyTorch", "TensorFlow", "Scikit-Learn", "Machine Learning", "Deep Learning", "NLP", "LLM", "Generative AI",
    "Git", "GitHub", "Linux", "Microservices", "Agile", "System Design", "Pandas", "NumPy"
]


def parse_created_timestamp(created_str):
    """
    Parses ISO created timestamp string from Adzuna into a UTC aware datetime object.
    Returns datetime.min (UTC) if parsing fails.
    """
    if not created_str or not isinstance(created_str, str):
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    try:
        clean = created_str.strip().replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        try:
            dt = datetime.datetime.strptime(created_str[:10], "%Y-%m-%d")
            return dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def get_relative_posted_date(created_str):
    """
    Calculates relative posted date string from actual Adzuna created timestamp.
    Examples:
    - 'Posted: Today'
    - 'Posted: 1 day ago'
    - 'Posted: 2 days ago'
    - 'Posted: 8 days ago'
    """
    dt = parse_created_timestamp(created_str)
    if dt.year <= 1:
        return "Posted: Date unknown"

    now = datetime.datetime.now(datetime.timezone.utc)
    diff_seconds = (now - dt).total_seconds()

    if diff_seconds < 86400 and dt.date() >= now.date():
        return "Posted: Today"

    days = max(1, int(diff_seconds // 86400))
    if days == 1:
        return "Posted: 1 day ago"
    return f"Posted: {days} days ago"


def is_job_within_age(created_str, max_age_days):
    """
    Checks if job created timestamp falls within maximum allowed age in days.
    If max_age_days is None (e.g. 'Any'), returns True.
    """
    if max_age_days is None:
        return True
    dt = parse_created_timestamp(created_str)
    if dt.year <= 1:
        return True
    now = datetime.datetime.now(datetime.timezone.utc)
    diff_seconds = (now - dt).total_seconds()
    if diff_seconds < 0:  # handle future clock skew
        return True
    return diff_seconds <= (max_age_days * 86400)


def search_live_jobs_uncached(keyword, location="India", results_per_page=50):
    """
    Executes a direct, uncached search request to Adzuna API.
    Guarantees every explicit 'Search' or 'Refresh' button click fetches fresh live data.
    Requests a larger result pool (50 results), deduplicates by actual job ID,
    sorts NEWEST → OLDEST, and attaches relative posted dates and fetch timestamp.
    """
    raw_response = search_jobs(
        keyword=keyword,
        location=location,
        results_per_page=50
    )

    if not raw_response or raw_response.get("error"):
        return {
            "jobs": [],
            "error": raw_response.get("error") if raw_response else "Unable to fetch fresh job listings right now.",
            "count": 0,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }

    raw_jobs = raw_response.get("jobs", [])

    # Deduplicate jobs strictly by actual Adzuna job ID while preserving order
    seen_ids = set()
    deduped_jobs = []

    for idx, job in enumerate(raw_jobs):
        job_id = str(job.get("id") or f"job_{idx}")
        if job_id not in seen_ids:
            seen_ids.add(job_id)
            job["posted_date_str"] = get_relative_posted_date(job.get("created", ""))
            job["parsed_dt"] = parse_created_timestamp(job.get("created", ""))
            deduped_jobs.append(job)

    # Sort jobs NEWEST → OLDEST by actual created timestamp
    deduped_jobs.sort(key=lambda j: j["parsed_dt"], reverse=True)

    return {
        "jobs": deduped_jobs,
        "error": None,
        "count": raw_response.get("count", len(deduped_jobs)),
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }


def get_jobs(keyword, location="India", results_per_page=50):
    """
    Backward-compatible job search wrapper.
    """
    return search_live_jobs_uncached(
        keyword=keyword,
        location=location,
        results_per_page=results_per_page
    )


def infer_target_role(resume_text="", detected_skills=None, job_category=None):
    """
    Infers candidate target role from resume text, detected skills, or job category.
    """
    if detected_skills is None:
        detected_skills = []

    if resume_text:
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()][:15]
        for line in lines:
            line_clean = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            if 3 <= len(line_clean.split()) <= 4 and any(kw in line_clean.lower() for kw in ["developer", "engineer", "analyst", "architect", "scientist", "specialist"]):
                return line_clean.title()

    skills_lower = [str(s).strip().lower() for s in detected_skills]

    role_rules = [
        ("Python Developer", ["python", "django", "fastapi", "flask"]),
        ("Data Scientist", ["pandas", "numpy", "scikit-learn", "data science", "statistics"]),
        ("Machine Learning Engineer", ["machine learning", "pytorch", "tensorflow", "deep learning", "llm", "nlp", "generative ai"]),
        ("Full Stack Developer", ["react", "node.js", "node", "express", "vue", "angular"]),
        ("Frontend Developer", ["frontend", "react", "vue", "angular", "css", "html"]),
        ("Backend Developer", ["backend", "microservices", "rest api", "spring boot", "postgresql"]),
        ("DevOps Engineer", ["devops", "docker", "kubernetes", "aws", "terraform", "ci/cd"]),
        ("Java Developer", ["java", "spring boot", "hibernate"]),
        ("Data Analyst", ["power bi", "tableau", "data analyst", "excel", "sql"]),
    ]

    for role_name, kws in role_rules:
        if any(kw in skills_lower for kw in kws):
            return role_name

    if job_category and job_category not in ["Other", "General"]:
        category_roles = {
            "AI / Machine Learning": "Machine Learning Engineer",
            "Data Science / Analytics": "Data Scientist",
            "Software Development": "Software Engineer",
            "Cloud / DevOps": "DevOps Engineer",
            "Cybersecurity": "Cybersecurity Analyst",
            "Finance / Accounting": "Financial Analyst",
            "Marketing": "Digital Marketing Specialist",
            "Business / Management": "Business Analyst",
        }
        return category_roles.get(job_category, f"{job_category} Professional")

    return "Software Engineer"


def calculate_advanced_job_match(job_item, analysis_data=None):
    """
    Calculates multi-dimensional Resume-to-Job Match %, Matching Skills,
    Partial Matches, Skill Gaps, and Evidence Explanations.
    
    Structure:
    - Technical Skills: 30%
    - Experience Alignment: 25%
    - Projects Evidence: 20%
    - Role/Title Alignment: 15%
    - Education/Certifications: 10%
    """
    if not analysis_data or not isinstance(analysis_data, dict) or not analysis_data.get("detected_skills"):
        return {
            "match_score": None,
            "matching_skills": [],
            "partial_matches": [],
            "skill_gaps": [],
            "why_matches": ["Upload a resume to unlock personalized match scoring and evidence explanations."]
        }

    job_title = str(job_item.get("title", "") or "")
    job_desc = str(job_item.get("description", "") or "")
    job_full_text = f"{job_title} {job_desc}".lower()

    detected_skills = [str(s).strip() for s in analysis_data.get("detected_skills", []) if str(s).strip()]
    candidate_skills_lower = {s.lower(): s for s in detected_skills}

    target_role = (
        analysis_data.get("target_role")
        or analysis_data.get("target_job")
        or analysis_data.get("job_category")
        or "Software Engineer"
    )

    resume_sections = analysis_data.get("resume_sections", {})
    candidate_level = analysis_data.get("candidate_level", "Mid-Level")

    # 1. TECHNICAL SKILLS MATCH (30 Points Max)
    job_req_skills = extract_skills(f"{job_title} {job_desc}")
    if not job_req_skills:
        job_req_skills = [s for s in COMMON_TECH_SKILLS if re.search(r'(?<![a-zA-Z0-9])' + re.escape(s.lower()) + r'(?![a-zA-Z0-9])', job_full_text)]

    matching_skills = []
    skill_gaps_raw = []

    for req_skill in job_req_skills:
        req_lower = req_skill.lower()
        if req_lower in candidate_skills_lower:
            matching_skills.append(candidate_skills_lower[req_lower])
        else:
            skill_gaps_raw.append(req_skill)

    matching_skills = list(dict.fromkeys(matching_skills))
    skill_gaps_raw = list(dict.fromkeys(skill_gaps_raw))

    # Partial Matches
    partial_matches = []
    for gap in skill_gaps_raw[:]:
        gap_lower = gap.lower()
        related = RELATED_SKILL_MAP.get(gap_lower, [])
        matched_rel = [r for r in related if r in candidate_skills_lower]
        if matched_rel:
            rel_original = [candidate_skills_lower[r] for r in matched_rel]
            partial_matches.append({
                "skill": gap,
                "reason": f"Candidate has related competency: {', '.join(rel_original[:2])}"
            })

    # Tech score calculation
    if job_req_skills:
        tech_ratio = (len(matching_skills) + 0.5 * len(partial_matches)) / max(1, len(job_req_skills))
        tech_score = min(30.0, tech_ratio * 30.0)
    else:
        tech_score = 20.0

    # 2. EXPERIENCE ALIGNMENT (25 Points Max)
    exp_score = 15.0
    if candidate_level in ["Senior-Level", "Executive"]:
        if any(kw in job_full_text for kw in ["senior", "lead", "principal", "architect", "5+", "7+"]):
            exp_score = 25.0
        else:
            exp_score = 20.0
    elif candidate_level in ["Mid-Level"]:
        exp_score = 20.0
    elif candidate_level in ["Entry-Level", "Junior"]:
        if any(kw in job_full_text for kw in ["junior", "entry", "intern", "associate", "0-2", "1-3"]):
            exp_score = 24.0
        else:
            exp_score = 14.0

    # 3. PROJECTS EVIDENCE (20 Points Max)
    proj_score = 10.0
    proj_text = str(resume_sections.get("projects", "") or "").lower()
    if proj_text:
        matched_proj_keywords = [s for s in matching_skills if s.lower() in proj_text]
        if len(matched_proj_keywords) >= 2:
            proj_score = 20.0
        elif len(matched_proj_keywords) >= 1:
            proj_score = 15.0

    # 4. ROLE & TITLE ALIGNMENT (15 Points Max)
    role_score = 5.0
    target_tokens = [t.lower() for t in re.findall(r'\w+', target_role) if len(t) > 2]
    if target_tokens:
        matches = sum(1 for token in target_tokens if token in job_title.lower())
        token_ratio = matches / len(target_tokens)
        role_score = min(15.0, token_ratio * 15.0)

    # 5. EDUCATION & CERTIFICATIONS (10 Points Max)
    edu_score = 8.0
    edu_text = str(resume_sections.get("education", "") or "") + " " + str(resume_sections.get("certifications", "") or "")
    if edu_text and len(edu_text.strip()) > 10:
        edu_score = 10.0

    total_score = tech_score + exp_score + proj_score + role_score + edu_score
    final_match_score = int(min(98.0, max(38.0, total_score)))

    why_matches = []
    if matching_skills:
        why_matches.append(f"Strong skill alignment with {len(matching_skills)} matching core competencies: {', '.join(matching_skills[:3])}")
    if role_score > 8.0:
        why_matches.append(f"Target role '{target_role}' closely aligns with job title '{job_title}'")
    if proj_score >= 15.0:
        why_matches.append("Candidate projects demonstrate hands-on experience relevant to job requirements")
    if exp_score >= 20.0:
        why_matches.append(f"Candidate experience level ({candidate_level}) matches role expectations")
    if not why_matches:
        why_matches.append("Role offers good domain relevance for candidate background")

    skill_gaps = []
    for idx, gap in enumerate(skill_gaps_raw[:6]):
        priority = "🔴 High Priority" if idx < 2 else ("🟡 Medium Priority" if idx < 4 else "⚪ Nice to Have")
        skill_gaps.append({
            "skill": gap,
            "priority": priority,
            "status": "Not demonstrated in resume"
        })

    return {
        "match_score": final_match_score,
        "matching_skills": matching_skills,
        "partial_matches": partial_matches,
        "skill_gaps": skill_gaps,
        "why_matches": why_matches
    }


def calculate_resume_match(job_title, job_description, resume_skills=None, target_job=None, has_resume=True):
    """
    Backward-compatible matching helper.
    """
    mock_job = {"title": job_title, "description": job_description}
    mock_analysis = {
        "detected_skills": resume_skills if resume_skills else [],
        "target_role": target_job if target_job else "Software Engineer"
    } if has_resume else None

    res = calculate_advanced_job_match(mock_job, mock_analysis)
    return {
        "match_score": res["match_score"],
        "matching_skills": res["matching_skills"],
        "skill_gaps": [g["skill"] if isinstance(g, dict) else g for g in res["skill_gaps"]],
        "why_matches": res["why_matches"][0] if res["why_matches"] else "Relevant job opportunity."
    }