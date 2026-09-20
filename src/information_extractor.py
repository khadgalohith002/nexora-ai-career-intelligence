import re


def extract_email(text):
    """Extract the first email address found in the resume."""

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return None


def extract_phone(text):
    """Extract a likely phone number from the resume."""

    patterns = [
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return None


def extract_linkedin(text):
    """Extract LinkedIn profile URL."""

    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(0)

    return None


def extract_github(text):
    """Extract GitHub profile URL."""

    pattern = r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+/?"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(0)

    return None


def extract_contact_information(text):
    """Return extracted contact information."""

    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
    }
