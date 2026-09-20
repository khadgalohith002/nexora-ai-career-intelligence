from src.skill_gap_engine import analyze_skill_gap, categorize_skills, get_required_skills_for_role

def run_tests():
    print("==================================================")
    print("RUNNING SKILL GAP ANALYSIS UNIT TESTS")
    print("==================================================")

    # Test 1: Resume A (Backend / Python Developer)
    resume_a_data = {
        "detected_skills": ["Python", "Django", "SQL", "Git", "PostgreSQL"],
        "target_job": "Python Developer",
        "target_role": "Python Developer",
        "job_category": "Software Engineering",
        "resume_sections": {
            "projects": ["Built Python Django web application with PostgreSQL database."],
            "experience": ["Backend Engineer using Python, SQL and Git."]
        },
        "resume_text": "Experienced Python Developer skilled in Django, SQL, PostgreSQL, and Git."
    }

    result_a = analyze_skill_gap(resume_a_data)
    assert result_a is not None
    print(f"\n[Test 1] Resume A Target Role: {result_a['target_role']}")
    print(f"Detected Skills: {result_a['detected_skills']}")
    print(f"Skill Match Score: {result_a['skill_match_score']}%")
    print(f"Strong Matches: {[m['skill'] for m in result_a['strong_matches']]}")
    print(f"Partial Matches: {[m['skill'] for m in result_a['partial_matches']]}")
    print(f"Skill Gaps: {[g['skill'] for g in result_a['skill_gaps']]}")
    print(f"Categorized: {result_a['categorized_current_skills']}")

    assert "Python" in [m['skill'] for m in result_a['strong_matches']]
    assert "Django" in [m['skill'] for m in result_a['strong_matches']]

    # Test 2: Resume B (Data Scientist / AI Engineer)
    resume_b_data = {
        "detected_skills": ["Python", "Machine Learning", "PyTorch", "Pandas", "NumPy", "NLP", "Scikit-Learn"],
        "target_job": "AI Engineer",
        "target_role": "AI Engineer",
        "job_category": "Artificial Intelligence",
        "resume_sections": {
            "projects": ["Trained PyTorch NLP transformer model using Pandas and NumPy."],
            "experience": ["AI Research Assistant doing Machine Learning with Scikit-Learn."]
        },
        "resume_text": "AI Engineer skilled in Python, Machine Learning, PyTorch, Pandas, NumPy, NLP, Scikit-Learn."
    }

    result_b = analyze_skill_gap(resume_b_data)
    print(f"\n[Test 2] Resume B Target Role: {result_b['target_role']}")
    print(f"Detected Skills: {result_b['detected_skills']}")
    print(f"Skill Match Score: {result_b['skill_match_score']}%")
    print(f"Strong Matches: {[m['skill'] for m in result_b['strong_matches']]}")
    print(f"Skill Gaps: {[g['skill'] for g in result_b['skill_gaps']]}")

    assert "Python" in [m['skill'] for m in result_b['strong_matches']]
    assert "PyTorch" in [m['skill'] for m in result_b['strong_matches']]

    # Test 3: Job Description Mode
    jd_text = "We are seeking a DevOps Engineer with Docker, Kubernetes, AWS, Linux, and Python experience."
    result_jd = analyze_skill_gap(resume_a_data, custom_job_description=jd_text)
    print(f"\n[Test 3] JD Mode Active: {result_jd['is_jd_mode']}")
    print(f"JD Required Skills: {result_jd['required_skills']}")
    print(f"JD Strong Matches: {[m['skill'] for m in result_jd['strong_matches']]}")
    print(f"JD Skill Gaps: {[g['skill'] for g in result_jd['skill_gaps']]}")

    assert result_jd['is_jd_mode'] == True
    assert "Docker" in [g['skill'] for g in result_jd['skill_gaps']]

    print("\n==================================================")
    print("ALL SKILL GAP UNIT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
