import re

CATEGORY_KEYWORDS = {
    "AI / Machine Learning": [
        "machine learning",
        "artificial intelligence",
        "deep learning",
        "neural network",
        "nlp",
        "natural language processing",
        "computer vision",
        "generative ai",
        "llm",
        "large language model",
        "tensorflow",
        "pytorch",
        "scikit-learn",
    ],
    "Data Science / Analytics": [
        "data science",
        "data scientist",
        "data analyst",
        "data analytics",
        "business intelligence",
        "power bi",
        "tableau",
        "pandas",
        "numpy",
        "statistics",
        "data visualization",
        "sql",
    ],
    "Software Development": [
        "software engineer",
        "software developer",
        "frontend",
        "backend",
        "full stack",
        "full-stack",
        "web developer",
        "java developer",
        "python developer",
        "react",
        "node.js",
        "django",
        "flask",
        "fastapi",
    ],
    "Cloud / DevOps": [
        "devops",
        "cloud engineer",
        "aws",
        "azure",
        "google cloud",
        "docker",
        "kubernetes",
        "ci/cd",
        "terraform",
        "jenkins",
    ],
    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "security analyst",
        "ethical hacking",
        "penetration testing",
        "network security",
        "vulnerability",
        "soc analyst",
        "siem",
    ],
    "Finance / Accounting": [
        "finance",
        "financial analysis",
        "accounting",
        "accountant",
        "financial analyst",
        "investment",
        "auditing",
        "taxation",
        "budgeting",
        "financial modeling",
    ],
    "Marketing": [
        "marketing",
        "digital marketing",
        "seo",
        "sem",
        "social media marketing",
        "content marketing",
        "brand management",
        "market research",
        "google analytics",
    ],
    "Human Resources": [
        "human resources",
        "hr",
        "recruitment",
        "recruiter",
        "talent acquisition",
        "employee engagement",
        "payroll",
        "hr operations",
    ],
    "Sales": [
        "sales",
        "business development",
        "lead generation",
        "customer acquisition",
        "sales executive",
        "sales manager",
        "crm",
    ],
    "Business / Management": [
        "business analyst",
        "business management",
        "project management",
        "product management",
        "strategy",
        "management",
        "business administration",
        "stakeholder management",
    ],
    "Operations": [
        "operations",
        "operations management",
        "supply chain",
        "logistics",
        "procurement",
        "inventory",
        "process improvement",
    ],
}


def _keyword_present(keyword, text):
    """
    Check whether a keyword/phrase appears in text.
    """

    pattern = r"(?<![A-Za-z0-9])" + re.escape(keyword) + r"(?![A-Za-z0-9])"

    return bool(re.search(pattern, text, re.IGNORECASE))


def classify_job(job_description):
    """
    Classify a job description into the most likely category.
    """

    if not job_description:
        return {"category": "Other", "confidence": 0.0, "scores": {}}

    text = job_description.lower()

    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if _keyword_present(keyword, text):
                score += 1

        category_scores[category] = score

    best_category = max(category_scores, key=category_scores.get)

    best_score = category_scores[best_category]

    if best_score == 0:
        return {"category": "Other", "confidence": 0.0, "scores": category_scores}

    total_score = sum(category_scores.values())

    confidence = best_score / total_score * 100 if total_score else 0

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "scores": category_scores,
    }
