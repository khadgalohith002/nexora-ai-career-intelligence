from src.skill_extractor import extract_skills
from src.text_preprocessor import preprocess_resume


def analyze_job_description(job_description):
    """
    Analyze a job description and extract useful information.
    """

    if not job_description:
        return {"cleaned_text": "", "normalized_text": "", "required_skills": []}

    processed_job = preprocess_resume(job_description)

    cleaned_text = processed_job["cleaned_text"]
    normalized_text = processed_job["normalized_text"]

    required_skills = extract_skills(cleaned_text)

    return {
        "cleaned_text": cleaned_text,
        "normalized_text": normalized_text,
        "required_skills": required_skills,
    }


def compare_skills(resume_skills, job_skills):
    """
    Compare resume skills with job-description skills.
    """

    resume_set = {skill.lower(): skill for skill in resume_skills}

    job_set = {skill.lower(): skill for skill in job_skills}

    matched_skills = []

    missing_skills = []

    for normalized_skill, original_skill in job_set.items():

        if normalized_skill in resume_set:
            matched_skills.append(original_skill)

        else:
            missing_skills.append(original_skill)

    total_required = len(job_set)

    if total_required == 0:
        match_percentage = 0.0

    else:
        match_percentage = (len(matched_skills) / total_required) * 100

    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "skill_match_percentage": round(match_percentage, 2),
    }
