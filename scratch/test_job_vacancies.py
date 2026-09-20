import sys
import os
from pathlib import Path

# Ensure UTF-8 output encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.adzuna_jobs import search_jobs
from src.job_service import get_jobs, infer_target_role, calculate_resume_match

def run_tests():
    print("============================================================")
    print("TESTING TAB 7 — LIVE ADZUNA JOBS & RESUME-AWARE MATCHING")
    print("============================================================")

    # 1. Test Target Role Inference
    sample_resume_text = """
    JOHN DOE
    Senior Python Developer & Backend Engineer
    Experience: 5 years building scalable web services with Python, Django, FastAPI, SQL, and AWS.
    """
    sample_skills = ["Python", "FastAPI", "SQL", "Django", "Git"]
    inferred_role = infer_target_role(sample_resume_text, sample_skills, "Software Development")
    print(f"\n1. Target Role Inference:")
    print(f"   Inferred Role: '{inferred_role}'")
    assert inferred_role in ["Senior Python Developer  Backend Engineer", "Python Developer"], f"Unexpected role: {inferred_role}"
    print("   ✓ Target Role Inference PASSED")

    # 2. Test Live Adzuna API Search
    print(f"\n2. Live Adzuna API Search:")
    res = search_jobs(keyword="Python Developer", location="India", results_per_page=5)
    assert res["error"] is None, f"API Error: {res['error']}"
    assert len(res["jobs"]) > 0, "No jobs returned from live Adzuna API"
    assert res["count"] > 0, "Count is 0"
    print(f"   Successfully fetched {len(res['jobs'])} live jobs out of {res['count']} available.")
    for j in res['jobs'][:2]:
        print(f"   - {j['title']} | {j['company']} | {j['location']} | {j['url']}")
        assert j['url'].startswith("http"), f"Invalid redirect_url: {j['url']}"
    print("   ✓ Live Adzuna API Search PASSED")

    # 3. Test Resume Match Calculation (WITH RESUME)
    print(f"\n3. Resume-Aware Match Calculation (WITH RESUME):")
    sample_job = res["jobs"][0]
    match_result = calculate_resume_match(
        job_title=sample_job["title"],
        job_description=sample_job["description"],
        resume_skills=sample_skills,
        target_job="Python Developer",
        has_resume=True
    )
    print(f"   Match Score: {match_result['match_score']}%")
    print(f"   Matching Skills: {match_result['matching_skills']}")
    print(f"   Skill Gaps: {match_result['skill_gaps']}")
    print(f"   Why Matches: {match_result['why_matches']}")
    assert match_result["match_score"] is not None and match_result["match_score"] >= 40, "Invalid match score"
    print("   ✓ Resume-Aware Match Calculation (WITH RESUME) PASSED")

    # 4. Test Resume Match Calculation (WITHOUT RESUME)
    print(f"\n4. Resume Match Calculation (WITHOUT RESUME):")
    no_resume_result = calculate_resume_match(
        job_title=sample_job["title"],
        job_description=sample_job["description"],
        resume_skills=[],
        target_job="",
        has_resume=False
    )
    print(f"   Match Score: {no_resume_result['match_score']}")
    print(f"   Why Matches: {no_resume_result['why_matches']}")
    assert no_resume_result["match_score"] is None, "Score should be None when no resume is uploaded!"
    assert "Upload a resume to unlock personalized matching" in no_resume_result["why_matches"], "Unexpected prompt"
    print("   ✓ No Resume Case PASSED (No fake score generated)")

    # 5. Test Resume Switch (RESUME A vs RESUME B)
    print(f"\n5. Resume Switch Match Calculation:")
    resume_a_skills = ["Python", "Django", "SQL"]
    match_a = calculate_resume_match(
        job_title="Python Developer",
        job_description="We need a Python developer skilled in Python, Django, SQL, and AWS.",
        resume_skills=resume_a_skills,
        target_job="Python Developer",
        has_resume=True
    )

    resume_b_skills = ["Java", "Spring Boot", "React"]
    match_b = calculate_resume_match(
        job_title="Python Developer",
        job_description="We need a Python developer skilled in Python, Django, SQL, and AWS.",
        resume_skills=resume_b_skills,
        target_job="Java Developer",
        has_resume=True
    )
    print(f"   Resume A Match Score: {match_a['match_score']}% | Matching: {match_a['matching_skills']}")
    print(f"   Resume B Match Score: {match_b['match_score']}% | Matching: {match_b['matching_skills']}")
    assert match_a["match_score"] > match_b["match_score"], "Resume A should have a higher match score for Python job"
    print("   ✓ Resume Switch Test PASSED")

    print("\n============================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! 🚀")
    print("============================================================")

if __name__ == "__main__":
    run_tests()
