import re

# Different headings people commonly use in resumes
SECTION_ALIASES = {
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
        "educational background",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "internship experience",
        "internships",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "technical projects",
        "project experience",
        "key projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses and certifications",
        "professional certifications",
        "courses and certifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "competencies",
        "technical competencies",
    ],
    "summary": [
        "summary",
        "profile",
        "professional summary",
        "career summary",
        "objective",
        "career objective",
        "about me",
    ],
    "achievements": [
        "achievements",
        "awards",
        "awards and achievements",
        "honors",
        "accomplishments",
    ],
}


def normalize_heading(line):
    """
    Normalize a potential resume heading.
    """

    line = line.strip().lower()

    # Remove common heading punctuation
    line = re.sub(r"[:|•\-–—]+$", "", line)

    # Normalize whitespace
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def identify_section(line):
    """
    Determine whether a line is a known resume section heading.
    """

    normalized_line = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():

        if normalized_line in aliases:
            return section_name

    return None


def extract_sections(text):
    """
    Split resume text into structured sections.
    """

    sections = {
        "summary": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "skills": [],
        "achievements": [],
    }

    current_section = None

    lines = text.splitlines()

    for line in lines:

        stripped_line = line.strip()

        if not stripped_line:
            continue

        detected_section = identify_section(stripped_line)

        if detected_section:

            current_section = detected_section
            continue

        if current_section:

            sections[current_section].append(stripped_line)

    # Convert lists into text
    for section in sections:

        sections[section] = "\n".join(sections[section]).strip()

    return sections
