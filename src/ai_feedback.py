def generate_ai_feedback(
    overall_score,
    resume_quality_score,
    matched_skills,
    missing_skills,
    quality_checks,
):
    """
    Generate human-readable AI feedback.
    """

    strengths = []
    weaknesses = []
    recommendations = []

    # -----------------------------
    # Strengths
    # -----------------------------

    if overall_score >= 80:
        strengths.append("Excellent overall resume-job match.")

    elif overall_score >= 60:
        strengths.append("Good alignment with the job description.")

    if resume_quality_score >= 75:
        strengths.append("Resume is well structured.")

    if len(matched_skills) >= 5:
        strengths.append("Strong technical skill coverage.")

    # -----------------------------
    # Weaknesses
    # -----------------------------

    if missing_skills:
        weaknesses.append(f"{len(missing_skills)} important skills are missing.")

    for section, present in quality_checks.items():

        if not present:

            weaknesses.append(f"{section} section is missing.")

    # -----------------------------
    # Recommendations
    # -----------------------------

    for skill in missing_skills[:5]:

        recommendations.append(f"Add or demonstrate experience with {skill}.")

    for section, present in quality_checks.items():

        if not present:

            recommendations.append(f"Include a strong {section} section.")

    if overall_score < 70:

        recommendations.append(
            "Tailor your resume more closely to the target job description."
        )

    # -----------------------------
    # Hiring Decision
    # -----------------------------

    if overall_score >= 85:

        decision = "Highly Recommended"

    elif overall_score >= 70:

        decision = "Recommended"

    elif overall_score >= 55:

        decision = "Consider After Improvements"

    else:

        decision = "Needs Significant Improvement"

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "decision": decision,
    }
