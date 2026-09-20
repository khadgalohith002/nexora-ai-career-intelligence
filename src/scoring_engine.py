def calculate_overall_score(skill_match, text_similarity):
    """
    Calculate an explainable overall resume-job match score.

    Current weights:
    Skill Match       = 60%
    Text Similarity   = 40%
    """

    skill_weight = 0.60
    similarity_weight = 0.40

    overall_score = skill_match * skill_weight + text_similarity * similarity_weight

    overall_score = round(overall_score, 2)

    return {
        "overall_score": overall_score,
        "skill_contribution": round(skill_match * skill_weight, 2),
        "similarity_contribution": round(text_similarity * similarity_weight, 2),
    }


def get_score_label(score):
    """
    Convert numerical score into a readable rating.
    """

    if score >= 85:
        return "Excellent Match"

    elif score >= 70:
        return "Strong Match"

    elif score >= 55:
        return "Moderate Match"

    elif score >= 40:
        return "Weak Match"

    else:
        return "Low Match"
