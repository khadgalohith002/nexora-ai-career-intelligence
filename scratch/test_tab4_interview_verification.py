import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath("."))

from src.text_preprocessor import preprocess_resume
from src.information_extractor import extract_contact_information
from src.skill_extractor import extract_skills
from src.section_extractor import extract_sections
from src.job_analyzer import analyze_job_description, compare_skills
from src.interview_engine import generate_suggested_interview_questions

resume_A = """
Alex Mercer
alex.mercer@devmail.com | +1 555-0192 | github.com/alexm-py

SUMMARY
Senior Python Architect with 5 years experience designing distributed REST microservices, PostgreSQL databases, and AWS cloud infrastructure.

SKILLS
Python, Django, FastAPI, PostgreSQL, Redis, AWS, Docker, Kubernetes, GraphQL

EXPERIENCE
Lead Python Developer | CloudScale Systems (2021 - Present)
- Designed high-throughput microservices using FastAPI and Redis, handling 50k requests per second.

PROJECTS
PyData Pipeline Engine
- Built open-source ETL pipeline in Python and PostgreSQL processing 1TB daily data.
"""

resume_B = """
Sarah Chen
sarah.chen@webdev.io | +1 555-0184 | linkedin.com/in/schen-ui

SUMMARY
Frontend React Developer specializing in responsive web applications, TypeScript, and state management.

SKILLS
JavaScript, TypeScript, React, Next.js, Redux, HTML5, CSS3, Tailwind CSS, Jest

EXPERIENCE
Frontend Engineer | DesignCraft Studios (2022 - Present)
- Developed customer dashboards using React and TypeScript, improving user engagement by 40%.

PROJECTS
UI Component Library
- Created accessible React component library published to NPM with 10k monthly downloads.
"""

def prepare_mock_data(resume_text, target_job, jd):
    processed = preprocess_resume(resume_text)
    contact_info = extract_contact_information(processed["cleaned_text"])
    skills = extract_skills(processed["cleaned_text"])
    sections = extract_sections(processed["cleaned_text"])
    job_an = analyze_job_description(jd)
    comp = compare_skills(skills, job_an["required_skills"])
    
    return {
        "resume_text": resume_text,
        "cleaned_resume": processed["cleaned_text"],
        "contact_info": contact_info,
        "detected_skills": skills,
        "resume_sections": sections,
        "matched_skills": comp["matched_skills"],
        "missing_skills": comp["missing_skills"],
        "job_skills": job_an["required_skills"]
    }

data_A = prepare_mock_data(resume_A, "Python Cloud Architect", "Python FastAPI AWS")
data_B = prepare_mock_data(resume_B, "Frontend React Developer", "React TypeScript Redux")

q_A = generate_suggested_interview_questions(data_A, "Python Cloud Architect")
q_B = generate_suggested_interview_questions(data_B, "Frontend React Developer")

print("=== TAB 4 SUGGESTED INTERVIEW QUESTIONS VERIFICATION ===")
print("1. Total Questions A:", len(q_A))
print("2. Total Questions B:", len(q_B))

assert len(q_A) >= 12, "Expected at least 12 questions for A"
assert len(q_B) >= 12, "Expected at least 12 questions for B"

print("\nSample Q1 A:", q_A[0]["question"], "| Based on:", q_A[0]["based_on"])
print("Sample Q1 B:", q_B[0]["question"], "| Based on:", q_B[0]["based_on"])

# Check project questions
proj_q_A = [q for q in q_A if q["category"] == "PROJECTS"][0]
proj_q_B = [q for q in q_B if q["category"] == "PROJECTS"][0]

print("\nProject Q A:", proj_q_A["question"], "| Based on:", proj_q_A["based_on"])
print("Project Q B:", proj_q_B["question"], "| Based on:", proj_q_B["based_on"])

assert "PyData Pipeline Engine" in proj_q_A["based_on"], "Expected PyData Pipeline Engine"
assert "UI Component Library" in proj_q_B["based_on"], "Expected UI Component Library"

print("\n✓ ALL TAB 4 REDESIGN MASTER REQUIREMENTS PASSED!")
