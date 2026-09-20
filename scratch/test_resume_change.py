import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath("."))

from src.text_preprocessor import preprocess_resume
from src.information_extractor import extract_contact_information
from src.skill_extractor import extract_skills
from src.section_extractor import extract_sections
from src.job_analyzer import analyze_job_description, compare_skills
from src.matching_engine import calculate_text_similarity
from src.job_classifier import classify_job
from src.scoring_engine import calculate_overall_score
from src.resume_quality import calculate_resume_quality
from src.candidate_level import detect_candidate_level
from src.ai_review_engine import generate_personalized_ai_review

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
- Managed AWS EKS clusters and Terraform IaC pipelines.

PROJECTS
PyData Pipeline Engine
- Built open-source ETL pipeline in Python and PostgreSQL processing 1TB daily data.

EDUCATION
B.S. Computer Science | MIT (2017 - 2021)
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

EDUCATION
B.A. Graphic & Web Design | NYU (2018 - 2022)
"""

def process_and_review(resume_text, target_job, jd):
    processed = preprocess_resume(resume_text)
    contact_info = extract_contact_information(processed["cleaned_text"])
    skills = extract_skills(processed["cleaned_text"])
    sections = extract_sections(processed["cleaned_text"])
    job_an = analyze_job_description(jd)
    comp = compare_skills(skills, job_an["required_skills"])
    sim = calculate_text_similarity(processed["normalized_text"], job_an["normalized_text"])
    score_res = calculate_overall_score(comp["skill_match_percentage"], sim)
    qual = calculate_resume_quality(contact_info, skills, sections)
    level = detect_candidate_level(jd)
    
    data = {
        "resume_text": resume_text,
        "cleaned_resume": processed["cleaned_text"],
        "contact_info": contact_info,
        "detected_skills": skills,
        "resume_sections": sections,
        "matched_skills": comp["matched_skills"],
        "missing_skills": comp["missing_skills"],
        "overall_score": score_res["overall_score"],
        "resume_quality_score": qual["quality_score"],
        "candidate_level": level["level"],
        "skill_match": comp["skill_match_percentage"],
        "resume_job_similarity": sim
    }
    
    return generate_personalized_ai_review(data, jd, target_job)

review_A = process_and_review(resume_A, "Python Cloud Architect", "Looking for Python, FastAPI, AWS, Kubernetes Engineer")
review_B = process_and_review(resume_B, "Frontend React Engineer", "Looking for React, TypeScript, Redux, Tailwind Developer")

print("VERIFYING RESUME A vs RESUME B REVIEWS:")

assert review_A["candidate_name"] == "Alex Mercer", f"Expected Alex Mercer, got {review_A['candidate_name']}"
assert review_B["candidate_name"] == "Sarah Chen", f"Expected Sarah Chen, got {review_B['candidate_name']}"
assert review_A["candidate_name"] != review_B["candidate_name"], "Names should be different"

print("✓ Candidate Name A:", review_A["candidate_name"])
print("✓ Candidate Name B:", review_B["candidate_name"])

print("\n--- STRENGTHS TEST ---")
str_A = [s["title"] for s in review_A["strengths"]]
str_B = [s["title"] for s in review_B["strengths"]]
print("Strengths A:", str_A)
print("Strengths B:", str_B)
assert str_A != str_B, "Strengths must be different"

print("\n--- SKILLS TEST ---")
skills_A = review_A["skill_analysis"]["strong_skills"]
skills_B = review_B["skill_analysis"]["strong_skills"]
print("Strong Skills A:", skills_A)
print("Strong Skills B:", skills_B)
assert skills_A != skills_B, "Skills must be different"

print("\n--- PROJECTS TEST ---")
proj_A = [p["name"] for p in review_A["project_analysis"]["items"]]
proj_B = [p["name"] for p in review_B["project_analysis"]["items"]]
print("Projects A:", proj_A)
print("Projects B:", proj_B)
assert proj_A != proj_B, "Projects must be different"
assert "PyData Pipeline Engine" in proj_A[0], "Expected PyData Pipeline Engine"
assert "UI Component Library" in proj_B[0], "Expected UI Component Library"

print("\n--- ACTION PLAN TEST ---")
plan_A = review_A["action_plan"][2]["description"]
plan_B = review_B["action_plan"][2]["description"]
print("Step 3 Plan A:", plan_A)
print("Step 3 Plan B:", plan_B)
assert plan_A != plan_B, "Action plan must be different"

print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
