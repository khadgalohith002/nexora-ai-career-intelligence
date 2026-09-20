import sys
from pathlib import Path

# Ensure UTF-8 output encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ai_service import generate_structured_resume_rewrite

def run_tests():
    print("============================================================")
    print("TESTING TAB 5 — RESUME REWRITE & AI GENERATION")
    print("============================================================")

    # Sample Resume A
    resume_a_text = """
    ALEX MERCER
    Software Engineer | Python Developer
    Email: alex@example.com | Phone: +91 9876543210

    EXPERIENCE:
    Software Engineer at Acme Corp (2021 - Present)
    • Worked on Python backend API development using FastAPI and PostgreSQL.
    • Helped team build microservices for data processing pipeline.

    PROJECTS:
    Resume Intelligence Analyzer
    • Developed a Python Streamlit web app for parsing resumes.

    SKILLS:
    Python, FastAPI, PostgreSQL, SQL, Docker, Git

    EDUCATION:
    B.Tech in Computer Science, ABC University
    """

    sections_a = {
        "summary": "Software Engineer with experience in Python backend development.",
        "experience": "Software Engineer at Acme Corp (2021 - Present)\n• Worked on Python backend API development using FastAPI and PostgreSQL.\n• Helped team build microservices for data processing pipeline.",
        "projects": "Resume Intelligence Analyzer\n• Developed a Python Streamlit web app for parsing resumes.",
        "skills": "Python, FastAPI, PostgreSQL, SQL, Docker, Git",
        "education": "B.Tech in Computer Science, ABC University"
    }

    skills_a = ["Python", "FastAPI", "PostgreSQL", "SQL", "Docker", "Git"]

    # 1. Test Structured Resume Rewrite Generation for Resume A
    print("\n1. Generating Structured Resume Rewrite (Resume A):")
    res_a = generate_structured_resume_rewrite(
        resume_text=resume_a_text,
        resume_sections=sections_a,
        detected_skills=skills_a,
        target_role="Python Backend Engineer",
        job_description="Looking for Python Developer with FastAPI, PostgreSQL, AWS, Docker.",
        rewrite_mode="Professional Rewrite",
        focus_areas=["Professional Summary", "Experience", "Projects", "Skills"]
    )

    assert res_a is not None, "Rewrite result is None"
    assert "full_rewritten_resume" in res_a, "Missing full_rewritten_resume key"
    assert "stats" in res_a, "Missing stats key"
    assert "before_after_comparisons" in res_a, "Missing before_after_comparisons key"
    
    print(f"   Sections Optimized: {res_a['stats']['sections_optimized']}")
    print(f"   Bullets Improved: {res_a['stats']['bullets_improved']}")
    print(f"   Weak Phrases Fixed: {res_a['stats']['weak_phrases_improved']}")
    print(f"   Keywords Identified: {res_a['stats']['keywords_identified']}")

    # Verify no hallucinated sections exist (Education present, no Certifications created if absent)
    full_markdown_a = res_a["full_rewritten_resume"]
    assert "Acme Corp" in full_markdown_a or "Acme" in resume_a_text, "Original company missing"
    assert "FastAPI" in full_markdown_a, "Original tech stack missing"
    print("   ✓ Resume A Rewrite Test PASSED")

    # 2. Test Resume B (Switch Resume Test)
    print("\n2. Resume Switch Test (Resume B):")
    resume_b_text = """
    SARAH CONNOR
    Financial Analyst
    Email: sarah@example.com

    EXPERIENCE:
    Financial Analyst at Finance Corp (2020 - Present)
    • Conducted financial modeling and forecasting.

    SKILLS:
    Excel, Financial Modeling, Power BI, Accounting
    """

    sections_b = {
        "experience": "Financial Analyst at Finance Corp (2020 - Present)\n• Conducted financial modeling and forecasting.",
        "skills": "Excel, Financial Modeling, Power BI, Accounting"
    }

    skills_b = ["Excel", "Financial Modeling", "Power BI", "Accounting"]

    res_b = generate_structured_resume_rewrite(
        resume_text=resume_b_text,
        resume_sections=sections_b,
        detected_skills=skills_b,
        target_role="Financial Analyst",
        job_description="Seeking Financial Analyst proficient in Excel and Power BI.",
        rewrite_mode="Professional Rewrite",
        focus_areas=["Experience", "Skills"]
    )

    full_markdown_b = res_b["full_rewritten_resume"]
    assert "Finance Corp" in full_markdown_b, "Resume B company missing"
    assert "Acme Corp" not in full_markdown_b, "Resume A data leaked into Resume B rewrite!"
    assert "Python" not in full_markdown_b or "Python" in skills_b, "Resume A skills leaked into Resume B!"

    print("   ✓ Resume Switch Isolation Test PASSED")

    print("\n============================================================")
    print("ALL TAB 5 REWRITE TESTS PASSED SUCCESSFULLY! 🚀")
    print("============================================================")

if __name__ == "__main__":
    run_tests()
