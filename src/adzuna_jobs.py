import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# ============================================================
# API CONSTANTS
# ============================================================

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# ============================================================
# SEARCH JOBS
# ============================================================

def search_jobs(keyword, location="India", results_per_page=50):
    """
    Search live job vacancies using the real Adzuna API for India.
    
    Returns a dictionary:
    {
        "jobs": [...],
        "error": None or "Error Message",
        "count": total_jobs_found
    }
    """
    # Check credentials safely
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[Adzuna API Error] Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in environment.")
        return {
            "jobs": [],
            "error": "Adzuna authentication failed. Check your ADZUNA_APP_ID and ADZUNA_APP_KEY configuration.",
            "count": 0,
        }

    # Fetch larger pool (up to 50 max allowed by Adzuna API per page)
    fetch_results_count = max(20, min(50, results_per_page if results_per_page >= 50 else 50))

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": fetch_results_count,
        "what": keyword,
        "where": location,
        "sort_by": "date",
        "content-type": "application/json",
    }

    try:
        # Console debug (never log secrets)
        safe_keyword = keyword if keyword else "All"
        safe_loc = location if location else "India"
        print(f"\nSearching jobs...")
        print(f"Keyword: {safe_keyword}")
        print(f"Location: {safe_loc}")

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )

        status_code = response.status_code
        print(f"Status Code: {status_code}")

        if status_code in (401, 403):
            return {
                "jobs": [],
                "error": "Adzuna authentication failed. Check your ADZUNA_APP_ID and ADZUNA_APP_KEY configuration.",
                "count": 0,
            }
        elif status_code == 429:
            return {
                "jobs": [],
                "error": "Adzuna request limit reached. Please try again later.",
                "count": 0,
            }
        elif status_code != 200:
            return {
                "jobs": [],
                "error": f"Adzuna API request failed with status code {status_code}.",
                "count": 0,
            }

        data = response.json()
        total_count = data.get("count", 0)
        raw_results = data.get("results", [])
        print(f"Found {len(raw_results)} jobs (Total available: {total_count})")

    except requests.exceptions.Timeout:
        print("[Adzuna API Error] Request timed out after 10s.")
        return {
            "jobs": [],
            "error": "Live job search timed out. Please try again.",
            "count": 0,
        }
    except requests.exceptions.RequestException as e:
        print(f"[Adzuna API Error] Network/Request error: {e}")
        return {
            "jobs": [],
            "error": "Unable to connect to the live job service.",
            "count": 0,
        }
    except ValueError:
        print("[Adzuna API Error] Failed to parse JSON response.")
        return {
            "jobs": [],
            "error": "Invalid response received from the job service.",
            "count": 0,
        }

    jobs = []
    for job in raw_results:
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        # Formatting salary strictly without None/null/₹0
        if salary_min is not None and salary_max is not None and (salary_min > 0 or salary_max > 0):
            salary = f"₹{salary_min:,.0f} - ₹{salary_max:,.0f}"
        elif salary_min is not None and salary_min > 0:
            salary = f"From ₹{salary_min:,.0f}"
        elif salary_max is not None and salary_max > 0:
            salary = f"Up to ₹{salary_max:,.0f}"
        else:
            salary = "Salary not disclosed"

        company_name = job.get("company", {}).get("display_name", "Company not specified")
        loc_name = job.get("location", {}).get("display_name", location)
        cat_name = job.get("category", {}).get("label", "General")
        redirect_url = job.get("redirect_url", "")

        jobs.append({
            "id": job.get("id", ""),
            "title": job.get("title", "Untitled Position"),
            "company": company_name,
            "location": loc_name,
            "description": job.get("description", ""),
            "url": redirect_url,
            "created": job.get("created", ""),
            "category": cat_name,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary": salary,
        })

    return {
        "jobs": jobs,
        "error": None,
        "count": total_count,
    }

if __name__ == "__main__":
    res = search_jobs(keyword="Python Developer", location="Bangalore", results_per_page=10)
    if res["error"]:
        print(f"Error: {res['error']}")
    else:
        print(f"Successfully retrieved {len(res['jobs'])} jobs. Total available: {res['count']}")
        for j in res['jobs'][:3]:
            print(f"- {j['title']} @ {j['company']} ({j['location']}) | {j['salary']} | {j['url']}")