import datetime
import time
from src.adzuna_jobs import search_jobs
from src.job_service import (
    search_live_jobs_uncached,
    parse_created_timestamp,
    get_relative_posted_date,
    is_job_within_age,
    calculate_advanced_job_match,
)

def run_tests():
    print("==================================================")
    print("RUNNING LIVE JOB SEARCH FRESHNESS VERIFICATION TESTS")
    print("==================================================")

    # TEST 1: Date Parser
    print("\n[TEST 1] Date Parsing & Relative Posted Date")
    sample_dates = [
        "2026-09-19T20:00:00Z",
        "2026-09-18T12:00:00Z",
        "2026-09-15T10:00:00Z",
        "2026-09-10T08:00:00Z",
        "2026-08-01T00:00:00Z"
    ]
    for d_str in sample_dates:
        parsed = parse_created_timestamp(d_str)
        rel_str = get_relative_posted_date(d_str)
        print(f"  ISO: {d_str} -> Parsed: {parsed} -> {rel_str}")
        assert parsed.year > 1, f"Failed to parse {d_str}"

    # TEST 2: Maximum Job Age Filter
    print("\n[TEST 2] Maximum Job Age Filter")
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    t_today = now_utc.isoformat()
    t_2d = (now_utc - datetime.timedelta(days=2)).isoformat()
    t_5d = (now_utc - datetime.timedelta(days=5)).isoformat()
    t_20d = (now_utc - datetime.timedelta(days=20)).isoformat()
    t_40d = (now_utc - datetime.timedelta(days=40)).isoformat()

    assert is_job_within_age(t_today, 1) == True, "Today should be within 1 day (24h)"
    assert is_job_within_age(t_2d, 1) == False, "2 days old should not be within 1 day"
    assert is_job_within_age(t_2d, 3) == True, "2 days old should be within 3 days"
    assert is_job_within_age(t_5d, 3) == False, "5 days old should not be within 3 days"
    assert is_job_within_age(t_5d, 7) == True, "5 days old should be within 7 days"
    assert is_job_within_age(t_20d, 30) == True, "20 days old should be within 30 days"
    assert is_job_within_age(t_40d, 30) == False, "40 days old should not be within 30 days"
    assert is_job_within_age(t_40d, None) == True, "Any age should return True"
    print("  [OK] All Maximum Job Age filter assertions passed!")

    # TEST 3: Uncached Live Search API Calls Across 4 Searches
    searches = [
        ("Site Engineer", "India"),
        ("Python Developer", "India"),
        ("Machine Learning Engineer", "India"),
        ("Data Scientist", "Bangalore")
    ]

    for idx, (kw, loc) in enumerate(searches, 1):
        print(f"\n[TEST 3.{idx}] Live Search: '{kw}' in '{loc}'")
        res = search_live_jobs_uncached(keyword=kw, location=loc, results_per_page=50)
        assert res.get("error") is None, f"Search failed with error: {res.get('error')}"
        jobs = res.get("jobs", [])
        fetch_time = res.get("timestamp")
        print(f"  - Request completed at: {fetch_time}")
        print(f"  - Returned {len(jobs)} jobs (Total count available in Adzuna: {res.get('count')})")
        assert len(jobs) > 0, f"Expected jobs for {kw} in {loc}"
        
        # Verify deduplication by ID
        job_ids = [j.get("id") for j in jobs if j.get("id")]
        assert len(job_ids) == len(set(job_ids)), "Duplicate job IDs found in response!"
        print(f"  [OK] Deduplication verified: {len(job_ids)} unique Adzuna job IDs")

        # Verify Newest -> Oldest sorting
        timestamps = [j["parsed_dt"] for j in jobs]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i+1], f"Jobs not sorted newest -> oldest at index {i}!"
        print(f"  [OK] Newest -> Oldest sorting verified")

        # Sample output
        top_job = jobs[0]
        print(f"  - Top Job: '{top_job.get('title')}' @ '{top_job.get('company')}'")
        print(f"    Posted: {top_job.get('posted_date_str')} (Created: {top_job.get('created')}) | ID: {top_job.get('id')}")

        # TEST 4: Resume Match Calculation
        mock_analysis = {
            "detected_skills": ["Python", "Machine Learning", "PyTorch", "SQL", "Git"],
            "target_role": kw,
            "candidate_level": "Mid-Level"
        }
        match_res = calculate_advanced_job_match(top_job, mock_analysis)
        print(f"    Match Score: {match_res['match_score']}% | Matching Skills: {match_res['matching_skills'][:3]}")

    print("\n==================================================")
    print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
