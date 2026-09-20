import re

SKILL_DATABASE = {
    # Programming
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "R",
    "SQL",
    # AI / ML
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "Natural Language Processing",
    "Computer Vision",
    "Generative AI",
    "LLM",
    "Large Language Models",
    # Data Science
    "Data Science",
    "Data Analysis",
    "Data Analytics",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    # Databases
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    # Development
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "Flask",
    "Django",
    "FastAPI",
    # Cloud / DevOps
    "AWS",
    "Azure",
    "Google Cloud",
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    # BI / Business
    "Excel",
    "Power BI",
    "Tableau",
    # Business
    "Marketing",
    "Digital Marketing",
    "Sales",
    "Finance",
    "Accounting",
    "Business Analysis",
    "Project Management",
    "Market Research",
    # HR
    "Recruitment",
    "Human Resources",
    "Talent Acquisition",
    # Soft / Professional
    "Communication",
    "Leadership",
    "Teamwork",
    "Problem Solving",
    "Time Management",
}


def extract_skills(text):

    if not text:
        return []

    detected_skills = []

    for skill in SKILL_DATABASE:

        pattern = r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])"

        if re.search(pattern, text, re.IGNORECASE):

            detected_skills.append(skill)

    return sorted(detected_skills)
