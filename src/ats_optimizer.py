def generate_ats_suggestions(missing_skills, quality_checks, overall_score):
    """
    Generate ATS optimization suggestions.
    """

    suggestions = []

    priority = []

    # -----------------------------
    # Missing Skills
    # -----------------------------

    for skill in missing_skills:

        priority.append(
            {
                "priority": "High",
                "message": (f"Add experience or projects involving {skill}."),
            }
        )

    # -----------------------------
    # Resume Sections
    # -----------------------------

    for section, present in quality_checks.items():

        if not present:

            priority.append(
                {
                    "priority": "Medium",
                    "message": (f"Include a stronger {section} section."),
                }
            )

    # -----------------------------
    # Overall Resume Advice
    # -----------------------------

    if overall_score < 70:

        suggestions.append("Customize your resume for every job application.")

    if overall_score < 80:

        suggestions.append("Use more job-specific keywords.")

    suggestions.append("Quantify achievements with numbers whenever possible.")

    suggestions.append("Keep resume length between one and two pages.")

    # -----------------------------
    # Estimate improvement
    # -----------------------------

    estimated_score = overall_score

    estimated_score += min(len(missing_skills) * 3, 15)

    estimated_score += 5

    estimated_score = min(estimated_score, 100)

    return {
        "priority_actions": priority,
        "general_suggestions": suggestions,
        "estimated_score": estimated_score,
    }
