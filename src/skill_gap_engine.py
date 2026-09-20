import re
from src.skill_extractor import extract_skills

# Standard skill requirement mappings by target role
ROLE_REQUIRED_SKILLS = {
    "AI Engineer": [
        "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
        "NLP", "Generative AI", "LLM", "Docker", "Git", "SQL", "FastAPI"
    ],
    "Machine Learning Engineer": [
        "Python", "Machine Learning", "Scikit-Learn", "PyTorch", "TensorFlow",
        "Pandas", "NumPy", "Docker", "Git", "SQL", "Data Analysis", "FastAPI"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Data Analysis", "Pandas", "NumPy",
        "Machine Learning", "Matplotlib", "Scikit-Learn", "Power BI", "Tableau", "Git"
    ],
    "Python Developer": [
        "Python", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL",
        "MongoDB", "Git", "GitHub", "Docker", "Linux"
    ],
    "Software Engineer": [
        "Python", "Java", "C++", "C#", "SQL", "Git", "GitHub",
        "Problem Solving", "System Design", "Agile", "Docker", "Linux"
    ],
    "Backend Developer": [
        "Python", "Java", "Node.js", "SQL", "PostgreSQL", "MongoDB",
        "Docker", "Kubernetes", "FastAPI", "Git", "AWS", "Linux"
    ],
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "HTML", "CSS",
        "Python", "SQL", "MongoDB", "Git", "Docker", "GitHub"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "HTML", "CSS",
        "Git", "GitHub", "Communication", "Problem Solving"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud", "Linux",
        "Git", "GitHub", "Python", "CI/CD", "Problem Solving"
    ],
    "Prompt Engineer": [
        "Python", "Generative AI", "LLM", "NLP", "PyTorch",
        "Natural Language Processing", "Git", "Problem Solving", "Communication"
    ],
    "Data Engineer": [
        "Python", "SQL", "PostgreSQL", "MongoDB", "AWS", "Docker",
        "Git", "Pandas", "NumPy", "Data Analysis", "Linux"
    ],
    "Data Analyst": [
        "Excel", "SQL", "Power BI", "Tableau", "Python", "Data Analysis",
        "Pandas", "Communication", "Problem Solving"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Linux",
        "Python", "Git", "GitHub", "Problem Solving"
    ],
    "Cyber Security Engineer": [
        "Linux", "Python", "C++", "C", "SQL", "Git",
        "Problem Solving", "Communication"
    ],
    "Product Manager": [
        "Project Management", "Business Analysis", "Communication", "Leadership",
        "Agile", "Problem Solving", "Data Analysis", "Excel"
    ]
}

# Categorization rules for detected skills
SKILL_CATEGORIES = {
    "Programming": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "R", "SQL",
        "HTML", "CSS", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"
    ],
    "Data & AI": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "NLP",
        "Natural Language Processing", "Computer Vision", "Generative AI", "LLM",
        "Large Language Models", "Data Science", "Data Analysis", "Data Analytics",
        "Pandas", "NumPy", "Matplotlib", "Scikit-Learn", "TensorFlow", "PyTorch",
        "Prompt Engineering"
    ],
    "Tools & Platforms": [
        "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud",
        "MySQL", "PostgreSQL", "MongoDB", "Flask", "Django", "FastAPI", "React",
        "Node.js", "Excel", "Power BI", "Tableau", "Linux", "CI/CD"
    ],
    "Soft Skills & Methodologies": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management",
        "Project Management", "Business Analysis", "Marketing", "Digital Marketing",
        "Sales", "Finance", "Accounting", "Recruitment", "Human Resources",
        "Talent Acquisition", "Market Research", "Agile", "Scrum", "System Design"
    ]
}

# Related skills for partial match reasoning
RELATED_SKILL_MAP = {
    "pytorch": ["tensorflow"],
    "tensorflow": ["pytorch"],
    "django": ["flask", "fastapi"],
    "fastapi": ["flask", "django"],
    "flask": ["django", "fastapi"],
    "kubernetes": ["docker"],
    "docker": ["kubernetes"],
    "nlp": ["generative ai", "llm"],
    "generative ai": ["llm", "nlp"],
    "llm": ["generative ai", "nlp"],
    "postgresql": ["mysql"],
    "mysql": ["postgresql"],
    "power bi": ["tableau"],
    "tableau": ["power bi"],
    "aws": ["azure", "google cloud"],
    "azure": ["aws", "google cloud"],
    "google cloud": ["aws", "azure"]
}

# Context-rich reasons & recommendations for common missing skills
SKILL_GAP_REASONS = {
    "Docker": {
        "reason": "Frequently associated with containerized application deployment and reproducible environments for target technical roles.",
        "action": "Learn Docker basics, create containerized builds for existing resume projects, and document Dockerfile setup."
    },
    "Kubernetes": {
        "reason": "Commonly requested for managing microservices and container orchestration at enterprise scale.",
        "action": "Study Kubernetes architecture fundamentals and demonstrate deployment configs on local clusters (Minikube)."
    },
    "PyTorch": {
        "reason": "A leading deep learning framework widely used in research and production AI model development.",
        "action": "Build a machine learning or NLP model using PyTorch and include GitHub repository evidence."
    },
    "TensorFlow": {
        "reason": "Standard production deep learning library used across computer vision, NLP, and model serving.",
        "action": "Train a neural network using TensorFlow/Keras and showcase model metrics in a project."
    },
    "SQL": {
        "reason": "Essential data query language required for backend, data engineering, and analytics roles.",
        "action": "Practice complex SQL queries (joins, window functions) and highlight database project experience."
    },
    "Git": {
        "reason": "Industry-standard version control system for collaborative software development.",
        "action": "Publish projects on GitHub with structured commit history and clear README documentation."
    },
    "FastAPI": {
        "reason": "Modern high-performance Python framework for building asynchronous web APIs.",
        "action": "Develop a RESTful API service with FastAPI and document API endpoints."
    },
    "Django": {
        "reason": "Full-featured Python web framework widely used for enterprise web applications.",
        "action": "Build a full-stack Python application using Django with ORM database integration."
    },
    "Generative AI": {
        "reason": "High-demand skill set involving LLM integration, prompt engineering, and RAG architectures.",
        "action": "Build a GenAI wrapper or RAG pipeline using LangChain/OpenAI APIs and add it to your portfolio."
    },
    "LLM": {
        "reason": "Core AI paradigm powering current automated intelligence applications.",
        "action": "Fine-tune or integrate an open-weight LLM for a domain-specific task."
    },
    "NLP": {
        "reason": "Crucial domain for processing textual data, sentiment analysis, and text classification.",
        "action": "Implement a text processing pipeline (tokenization, embeddings, classification) in a Python project."
    },
    "AWS": {
        "reason": "Leading cloud provider for cloud computing, serverless architectures, and deployment.",
        "action": "Deploy a project on AWS (EC2, S3, or Lambda) and document cloud infrastructure."
    },
    "PostgreSQL": {
        "reason": "Robust relational database system preferred for production Python and enterprise backends.",
        "action": "Design a relational schema using PostgreSQL and integrate it with your backend API."
    },
    "MongoDB": {
        "reason": "Popular Document-oriented NoSQL database used for flexible data storage.",
        "action": "Implement NoSQL database storage for unstructured or JSON-based application data."
    },
    "React": {
        "reason": "Primary frontend UI library for modern web applications.",
        "action": "Build an interactive web frontend using React and connect it to backend services."
    },
    "Machine Learning": {
        "reason": "Core discipline for predictive modeling, feature engineering, and automated decision making.",
        "action": "Complete a end-to-end Machine Learning project covering data cleaning, training, and evaluation."
    }
}


def categorize_skills(skills_list):
    """
    Categorizes a list of skills into clean domain buckets.
    """
    categorized = {
        "Programming": [],
        "Data & AI": [],
        "Tools & Platforms": [],
        "Soft Skills & Methodologies": [],
        "Other Technical Skills": []
    }

    if not skills_list:
        return categorized

    for skill in sorted(list(set(skills_list))):
        assigned = False
        for category, cat_skills in SKILL_CATEGORIES.items():
            if any(s.lower() == skill.lower() for s in cat_skills):
                categorized[category].append(skill)
                assigned = True
                break
        if not assigned:
            categorized["Other Technical Skills"].append(skill)

    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def find_resume_evidence(skill, analysis_data):
    """
    Finds concrete evidence of a skill in the candidate's resume sections/text.
    """
    if not analysis_data or not isinstance(analysis_data, dict):
        return []

    evidence = []
    skill_lower = skill.lower()

    # Search in resume sections (Projects, Experience, Education, Certifications)
    resume_sections = analysis_data.get("resume_sections", {})
    if isinstance(resume_sections, dict):
        for section_name, section_content in resume_sections.items():
            if not section_content:
                continue

            section_str = ""
            if isinstance(section_content, list):
                section_str = " ".join([str(item) for item in section_content])
            else:
                section_str = str(section_content)

            pattern = r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])"
            if re.search(pattern, section_str, re.IGNORECASE):
                # Clean section title formatting
                clean_title = section_name.replace("_", " ").title()
                evidence.append(f"{clean_title} section")

    # Search raw text for specific project or experience bullet points if sections are sparse
    resume_text = analysis_data.get("resume_text", "")
    if resume_text and len(evidence) < 2:
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        for line in lines:
            pattern = r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])"
            if re.search(pattern, line, re.IGNORECASE):
                # Use concise line snippet if it looks like a bullet or project name
                if len(line) < 100 and ("project" in line.lower() or "worked" in line.lower() or "developed" in line.lower() or "using" in line.lower()):
                    evidence.append(line)
                    if len(evidence) >= 3:
                        break

    return list(dict.fromkeys(evidence))[:3]


def get_required_skills_for_role(target_role, job_description="", existing_job_skills=None):
    """
    Determines required skills for a target role or job description.
    """
    required = []

    # If Job Description is provided, extract skills directly from JD as primary source
    if job_description and job_description.strip():
        extracted_from_jd = extract_skills(job_description)
        if extracted_from_jd:
            required.extend(extracted_from_jd)

    # Match target role in ROLE_REQUIRED_SKILLS dictionary
    if target_role:
        for role_key, role_skills in ROLE_REQUIRED_SKILLS.items():
            if role_key.lower() in target_role.lower() or target_role.lower() in role_key.lower():
                required.extend(role_skills)
                break

    # Use existing application job skills if available
    if existing_job_skills and isinstance(existing_job_skills, list):
        required.extend(existing_job_skills)

    # Fallback to general professional skills if still empty
    if not required:
        required = ROLE_REQUIRED_SKILLS["Software Engineer"]

    # Remove duplicates preserving order
    unique_required = []
    for s in required:
        if s not in unique_required:
            unique_required.append(s)

    return unique_required[:12]


def analyze_skill_gap(analysis_data, selected_target_role=None, custom_job_description=None):
    """
    Performs complete, dynamic, resume-specific Skill Gap Analysis.
    Never invents skills or claims missing skills are known.
    """
    if not analysis_data or not isinstance(analysis_data, dict):
        return None

    # 1. Detected skills from resume
    detected_skills = analysis_data.get("detected_skills", [])
    if not isinstance(detected_skills, list):
        detected_skills = []

    resume_skills_set = {s.lower(): s for s in detected_skills}

    # 2. Determine target role and job description
    job_description = (
        custom_job_description
        if custom_job_description is not None
        else analysis_data.get("job_description", "")
    )
    is_jd_mode = bool(job_description and job_description.strip())

    target_role = (
        selected_target_role
        if selected_target_role and selected_target_role.strip()
        else (analysis_data.get("target_role") or analysis_data.get("target_job") or analysis_data.get("job_category") or "Target Role Not Specified")
    )

    # 3. Determine required skills
    required_skills = get_required_skills_for_role(
        target_role=target_role,
        job_description=job_description,
        existing_job_skills=analysis_data.get("job_skills")
    )

    # 4. Classify skills: Strong Match, Partial Match, Skill Gap
    strong_matches = []
    partial_matches = []
    skill_gaps = []

    for req_skill in required_skills:
        req_lower = req_skill.lower()

        # Check for Strong Match (Directly present in detected skills)
        if req_lower in resume_skills_set:
            evidence = find_resume_evidence(req_skill, analysis_data)
            strong_matches.append({
                "skill": req_skill,
                "status": "STRONG MATCH",
                "evidence": evidence
            })
            continue

        # Check for Partial Match (Related skill present in resume)
        related = RELATED_SKILL_MAP.get(req_lower, [])
        matched_related = [r_skill for r_skill in related if r_skill in resume_skills_set]

        if matched_related:
            original_matched_names = [resume_skills_set[r] for r in matched_related]
            partial_matches.append({
                "skill": req_skill,
                "status": "PARTIAL MATCH",
                "reason": f"Demonstrated related competency: {', '.join(original_matched_names[:2])}",
                "related_skills": original_matched_names
            })
        else:
            # Skill Gap (Not demonstrated in resume)
            priority = "HIGH PRIORITY" if len(skill_gaps) < 3 else ("MEDIUM PRIORITY" if len(skill_gaps) < 6 else "LOW PRIORITY")
            gap_info = SKILL_GAP_REASONS.get(req_skill, {
                "reason": f"Frequently required for competency in {target_role}.",
                "action": f"Gain foundational knowledge in {req_skill} and demonstrate it through a practical project."
            })
            skill_gaps.append({
                "skill": req_skill,
                "status": "SKILL GAP",
                "priority": priority,
                "reason": gap_info["reason"],
                "action": gap_info["action"]
            })

    # 5. Dynamic Skill Match Score
    total_req = max(1, len(required_skills))
    weighted_score = (len(strong_matches) * 1.0 + len(partial_matches) * 0.5) / total_req * 100
    skill_match_score = round(min(100.0, max(0.0, weighted_score)), 1)

    # 6. Categorized Current Skills
    categorized_current = categorize_skills(detected_skills)

    # 7. Learning Roadmap Generation
    roadmap_steps = []
    sorted_gaps = sorted(skill_gaps, key=lambda x: (0 if x["priority"] == "HIGH PRIORITY" else (1 if x["priority"] == "MEDIUM PRIORITY" else 2)))
    
    step_num = 1
    for gap in sorted_gaps[:4]:
        roadmap_steps.append({
            "step": f"STEP {step_num}",
            "skill": gap["skill"],
            "priority": gap["priority"],
            "action": gap["action"]
        })
        step_num += 1

    return {
        "target_role": target_role,
        "is_jd_mode": is_jd_mode,
        "job_description": job_description,
        "detected_skills": detected_skills,
        "categorized_current_skills": categorized_current,
        "required_skills": required_skills,
        "strong_matches": strong_matches,
        "partial_matches": partial_matches,
        "skill_gaps": skill_gaps,
        "skill_match_score": skill_match_score,
        "top_gaps": sorted_gaps[:5],
        "roadmap_steps": roadmap_steps
    }
