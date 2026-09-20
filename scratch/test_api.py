import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output encoding for console
sys.stdout.reconfigure(encoding='utf-8')

from src.adzuna_jobs import search_jobs

tests = [
    ("Python Developer", "Bangalore"),
    ("Software Engineer", "India"),
    ("Data Scientist", "Hyderabad"),
]

results_summary = []

for title, location in tests:
    print("=" * 60)
    print(f"TEST: {title} in {location}")
    print("=" * 60)
    res = search_jobs(keyword=title, location=location, results_per_page=10)
    if res["error"]:
        print(f"FAILED: {res['error']}")
    else:
        jobs = res["jobs"]
        count = res["count"]
        print(f"Found {len(jobs)} jobs (Total available in Adzuna: {count})")
        results_summary.append({
            "title": title,
            "location": location,
            "returned_jobs": len(jobs),
            "total_count": count,
            "sample_job": jobs[0] if jobs else None
        })

print("\n" + "=" * 60)
print("SUMMARY OF REAL ADZUNA API TESTS:")
print("=" * 60)
for item in results_summary:
    print(f"Keyword: {item['title']} | Location: {item['location']} | Returned: {item['returned_jobs']} | Available: {item['total_count']}")
    if item['sample_job']:
        print(f"  -> Sample: '{item['sample_job']['title']}' @ '{item['sample_job']['company']}' ({item['sample_job']['location']}) | {item['sample_job']['salary']}")
        print(f"  -> Redirect URL: {item['sample_job']['url']}")
