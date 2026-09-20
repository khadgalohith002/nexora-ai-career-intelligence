import re


def detect_candidate_level(job_description):
    """
    Detect the expected candidate experience level
    from a job description.
    """

    if not job_description:
        return {"level": "Unknown", "years_required": None, "confidence": 0}

    text = job_description.lower()

    # -----------------------------------
    # Extract years of experience
    # -----------------------------------

    year_patterns = [
        r"(\d+)\s*\+?\s*years?",
        r"(\d+)\s*-\s*(\d+)\s*years?",
        r"(\d+)\s*to\s*(\d+)\s*years?",
    ]

    years_required = None

    for pattern in year_patterns:

        match = re.search(pattern, text)

        if match:

            numbers = [int(number) for number in match.groups() if number is not None]

            if numbers:
                years_required = min(numbers)

            break

    # -----------------------------------
    # Internship detection
    # -----------------------------------

    internship_keywords = [
        "internship",
        "intern",
        "student intern",
        "summer intern",
        "graduate intern",
    ]

    if any(keyword in text for keyword in internship_keywords):
        return {
            "level": "Internship",
            "years_required": years_required,
            "confidence": 95,
        }

    # -----------------------------------
    # Fresher detection
    # -----------------------------------

    fresher_keywords = [
        "fresher",
        "fresh graduate",
        "recent graduate",
        "graduate trainee",
        "campus hire",
        "no experience required",
    ]

    if any(keyword in text for keyword in fresher_keywords):
        return {"level": "Fresher", "years_required": years_required, "confidence": 90}

    # -----------------------------------
    # Determine from experience
    # -----------------------------------

    if years_required is not None:

        if years_required == 0:

            level = "Fresher"

        elif years_required <= 2:

            level = "Entry Level"

        elif years_required <= 5:

            level = "Mid Level"

        else:

            level = "Senior Level"

        return {"level": level, "years_required": years_required, "confidence": 85}

    # -----------------------------------
    # Senior role keywords
    # -----------------------------------

    senior_keywords = ["senior", "lead", "principal", "manager", "architect", "head of"]

    if any(keyword in text for keyword in senior_keywords):
        return {"level": "Senior Level", "years_required": None, "confidence": 70}

    # -----------------------------------
    # Entry-level keywords
    # -----------------------------------

    entry_keywords = ["entry level", "entry-level", "junior", "associate", "trainee"]

    if any(keyword in text for keyword in entry_keywords):
        return {"level": "Entry Level", "years_required": None, "confidence": 70}

    return {"level": "Not Specified", "years_required": None, "confidence": 40}
