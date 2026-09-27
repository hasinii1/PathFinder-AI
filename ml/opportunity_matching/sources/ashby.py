import requests
from datetime import datetime, timezone

BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"


def fetch_ashby_jobs(board_name):
    if not board_name:
        raise ValueError("Ashby board_name is required.")

    board_name = str(board_name).strip()

    if not board_name:
        raise ValueError("Ashby board_name cannot be empty.")

    url = f"{BASE_URL}/{board_name}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    jobs = data.get("jobs", [])

    if not isinstance(jobs, list):
        return []

    return jobs


def normalize_ashby_job(job, company):
    if not isinstance(job, dict):
        return None

    company = str(company or "").strip()

    external_id = str(
        job.get("id") or job.get("jobId") or ""
    ).strip()

    title = str(
        job.get("title") or ""
    ).strip()

    location = str(
        job.get("location") or ""
    ).strip()

    description = str(
        job.get("descriptionPlain")
        or job.get("description")
        or ""
    ).strip()

    url = str(
        job.get("jobUrl")
        or job.get("applyUrl")
        or ""
    ).strip()

    if not external_id or not title or not url:
        return None

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "source": "Ashby",
        "company": company,
        "external_id": external_id,
        "title": title,
        "location": location,
        "job_type": "",
        "description": description,
        "url": url,
        "updated_at": "",
        "fetched_at": fetched_at,
        "required_skills": []
    }


def get_ashby_opportunities(board_name, company):
    jobs = fetch_ashby_jobs(board_name)

    opportunities = []

    for job in jobs:
        normalized = normalize_ashby_job(job, company)

        if normalized is not None:
            opportunities.append(normalized)

    return opportunities