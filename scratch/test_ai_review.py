import os
import sys
import json

sys.path.append(os.path.abspath("."))

from src.resume_parser import extract_resume_text
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

resume_text_A = """
John Doe
Email: john.doe@example.com | Phone: +91 9876543210
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Results-driven Python Backend Developer with 2 years of experience building scalable web applications, REST APIs, and database systems.

SKILLS
Python, Django, Flask, PostgreSQL, MySQL, Redis, REST APIs, Docker, Git

EXPERIENCE
Software Engineer | ABC Tech Solutions (2022 - Present)
- Developed RESTful microservices using Python and Django, reducing API response times by 30%.
- Designed and optimized PostgreSQL database queries for high-throughput transaction processing.
- Containerized backend services using Docker and deployed CI/CD pipelines.

PROJECTS
Smart Resume Analyzer
- Built a web application using Python, Django, and PostgreSQL to parse and analyze resumes.
- Integrated AI models to match resume skills with job descriptions.

E-Commerce API Service
- Developed secure payment gateway APIs using Flask and Redis for session management.

EDUCATION
B.Tech in Computer Science & Engineering | XYZ University (2018 - 2022)
"""

resume_text_B = """
Priya Sharma
Email: priya.s@example.com | Phone: +91 9123456789

OBJECTIVE
Motivated Java Developer looking for an entry-level position in enterprise software development.

TECHNICAL SKILLS
Java, Spring Boot, Hibernate, MySQL, HTML, CSS, JavaScript, React, Git

EDUCATION
B.E. in Information Technology | ABC Institute of Technology (2020 - 2024)

PROJECTS
Employee Management System
- Developed a full-stack web application using Java, Spring Boot, MySQL, and React.
- Implemented JWT authentication and role-based access control.

Online Bookstore
- Created a frontend web application using React, HTML, CSS, and JavaScript.

CERTIFICATIONS
Oracle Certified Associate, Java SE Programmer
"""

def analyze_mock(resume_text, target_job, jd):
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
    
    return {
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

data_A = analyze_mock(resume_text_A, "Python Backend Developer", "Looking for Python, Django, PostgreSQL, AWS Developer.")
data_B = analyze_mock(resume_text_B, "Java Full Stack Developer", "Looking for Java, Spring Boot, React, MySQL Developer.")

review_A = generate_personalized_ai_review(data_A, "Looking for Python, Django, PostgreSQL, AWS Developer.", "Python Backend Developer")
review_B = generate_personalized_ai_review(data_B, "Looking for Java, Spring Boot, React, MySQL Developer.", "Java Full Stack Developer")

print("=== REVIEW A (PYTHON DEVELOPER) ===")
print("Candidate Name:", review_A["candidate_name"])
print("Executive Summary:", review_A["executive_summary"])
print("Strengths:", [s["title"] for s in review_A["strengths"]])
print("Projects:", [p["name"] for p in review_A["project_analysis"]["items"]])
print("Scores:", review_A["scores"])

print("\n=== REVIEW B (JAVA DEVELOPER) ===")
print("Candidate Name:", review_B["candidate_name"])
print("Executive Summary:", review_B["executive_summary"])
print("Strengths:", [s["title"] for s in review_B["strengths"]])
print("Projects:", [p["name"] for p in review_B["project_analysis"]["items"]])
print("Scores:", review_B["scores"])
