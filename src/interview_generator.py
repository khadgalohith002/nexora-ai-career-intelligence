INTERVIEW_QUESTIONS = {
    "General HR": [
        "Tell me about yourself.",
        "Why do you want to join our company?",
        "What are your strengths?",
        "What is your biggest weakness?",
        "Describe a challenging situation and how you handled it.",
    ],
    "Python": [
        "Explain list vs tuple.",
        "What is a dictionary?",
        "Explain decorators.",
        "What is list comprehension?",
        "Explain generators.",
    ],
    "SQL": [
        "Difference between WHERE and HAVING?",
        "Explain JOIN types.",
        "What is normalization?",
        "Explain GROUP BY.",
        "What are indexes?",
    ],
    "Machine Learning": [
        "What is overfitting?",
        "Difference between supervised and unsupervised learning?",
        "Explain bias vs variance.",
        "What is cross validation?",
        "Explain gradient descent.",
    ],
    "AWS": [
        "Explain EC2.",
        "What is S3?",
        "Difference between EC2 and Lambda?",
        "Explain IAM.",
        "How do you secure AWS resources?",
    ],
    "Docker": [
        "What is Docker?",
        "Difference between Docker Image and Container?",
        "Explain Dockerfile.",
        "What is Docker Compose?",
    ],
    "Git": [
        "Difference between merge and rebase?",
        "Explain Git branching.",
        "How do you resolve merge conflicts?",
    ],
}


def generate_interview_questions(
    detected_skills, missing_skills, job_category, candidate_level
):
    """
    Generate interview questions based on the analysis.
    """

    result = {}

    # HR Questions
    result["HR"] = INTERVIEW_QUESTIONS["General HR"]

    # Skill-based questions
    for skill in detected_skills:

        if skill in INTERVIEW_QUESTIONS:

            result[skill] = INTERVIEW_QUESTIONS[skill]

    # Missing skills
    if missing_skills:

        result["Prepare These Topics"] = [
            f"Learn the basics of {skill}." for skill in missing_skills
        ]

    # Project discussion
    result["Project Discussion"] = [
        "Explain your favorite project.",
        "What problem did it solve?",
        "What challenges did you face?",
        "What would you improve if given more time?",
    ]

    # Role information
    result["Role"] = [
        f"Target Role: {job_category}",
        f"Candidate Level: {candidate_level}",
    ]

    return result
