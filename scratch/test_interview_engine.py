import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath("."))

from src.text_preprocessor import preprocess_resume
from src.information_extractor import extract_contact_information
from src.skill_extractor import extract_skills
from src.section_extractor import extract_sections
from src.job_analyzer import analyze_job_description, compare_skills
from src.interview_engine import (
    generate_personalized_interview,
    evaluate_user_answer,
    generate_final_interview_report
)

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

q_A = generate_personalized_interview(data_A, "Python Cloud Architect")
q_B = generate_personalized_interview(data_B, "Frontend React Developer")

print("=== INTERVIEW QUESTIONS TEST ===")
print("Questions Count A:", len(q_A))
print("Questions Count B:", len(q_B))

print("\nSample Q4 Resume A (Project):", q_A[3]["question"])
print("Sample Q4 Resume B (Project):", q_B[3]["question"])

assert "PyData Pipeline Engine" in q_A[3]["question"], "Expected PyData Pipeline Engine in Q4 A"
assert "UI Component Library" in q_B[3]["question"], "Expected UI Component Library in Q4 B"
assert q_A[3]["question"] != q_B[3]["question"], "Questions must be different for Resume A and B"

# Test answer evaluation
eval_A = evaluate_user_answer(
    q_A[3],
    "I built the PyData Pipeline Engine using Python and PostgreSQL, implementing chunked batch processing and indexing.",
    "Python Cloud Architect",
    data_A
)

print("\n=== ANSWER EVALUATION TEST ===")
print("What did well:", eval_A["what_did_well"])
print("Scores:", eval_A["scores"])
print("Adaptive Follow-Up:", eval_A["follow_up_question"])

assert eval_A["scores"]["technical_depth"] > 0, "Expected valid score"
assert "follow_up_question" in eval_A, "Expected follow-up question"

print("\nALL INTERVIEW ENGINE TESTS PASSED SUCCESSFULLY!")
