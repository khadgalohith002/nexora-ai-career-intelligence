def calculate_resume_quality(contact_info, detected_skills, resume_sections):
    """
    Calculate resume completeness/quality score.

    Maximum score = 100
    """

    score = 0
    checks = {}

    # --------------------------------
    # Contact Information — 15 points
    # --------------------------------

    email_present = bool(contact_info.get("email"))

    phone_present = bool(contact_info.get("phone"))

    if email_present:
        score += 7.5

    if phone_present:
        score += 7.5

    checks["Contact Information"] = email_present and phone_present

    # --------------------------------
    # Skills — 20 points
    # --------------------------------

    skill_count = len(detected_skills)

    if skill_count >= 8:
        score += 20
        checks["Skills"] = True

    elif skill_count >= 5:
        score += 15
        checks["Skills"] = True

    elif skill_count >= 3:
        score += 10
        checks["Skills"] = True

    elif skill_count > 0:
        score += 5
        checks["Skills"] = True

    else:
        checks["Skills"] = False

    # --------------------------------
    # Education — 15 points
    # --------------------------------

    education_present = bool(resume_sections.get("education", "").strip())

    if education_present:
        score += 15

    checks["Education"] = education_present

    # --------------------------------
    # Experience — 15 points
    # --------------------------------

    experience_present = bool(resume_sections.get("experience", "").strip())

    if experience_present:
        score += 15

    checks["Experience"] = experience_present

    # --------------------------------
    # Projects — 15 points
    # --------------------------------

    projects_present = bool(resume_sections.get("projects", "").strip())

    if projects_present:
        score += 15

    checks["Projects"] = projects_present

    # --------------------------------
    # Summary — 10 points
    # --------------------------------

    summary_present = bool(resume_sections.get("summary", "").strip())

    if summary_present:
        score += 10

    checks["Summary / Objective"] = summary_present

    # --------------------------------
    # Certifications — 5 points
    # --------------------------------

    certifications_present = bool(resume_sections.get("certifications", "").strip())

    if certifications_present:
        score += 5

    checks["Certifications"] = certifications_present

    # --------------------------------
    # Achievements — 5 points
    # --------------------------------

    achievements_present = bool(resume_sections.get("achievements", "").strip())

    if achievements_present:
        score += 5

    checks["Achievements"] = achievements_present

    return {"quality_score": round(score, 2), "checks": checks}


def get_quality_label(score):

    if score >= 90:
        return "Excellent Resume"

    elif score >= 75:
        return "Strong Resume"

    elif score >= 60:
        return "Good Resume"

    elif score >= 40:
        return "Needs Improvement"

    else:
        return "Incomplete Resume"
