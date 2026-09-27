import requests
from datetime import datetime, timezone


BASE_URL = "https://api.lever.co/v0/postings"


def fetch_lever_jobs(site_name):

    url = f"{BASE_URL}/{site_name}"

    response = requests.get(
        url,
        params={"mode": "json"},
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def normalize_lever_job(job, company):

    categories = job.get(
        "categories",
        {}
    )

    if not isinstance(categories, dict):
        categories = {}

    job_type = (
        categories.get("commitment")
        or job.get("commitment")
        or ""
    )

    location = (
        categories.get("location")
        or ""
    )

    description = (
        job.get("descriptionPlain")
        or ""
    )

    title = (
        job.get("text")
        or ""
    )

    url = (
        job.get("hostedUrl")
        or ""
    )

    external_id = (
        job.get("id")
        or ""
    )

    fetched_at = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    return {
        "source": "Lever",
        "company": company,
        "external_id": external_id,
        "title": title,
        "location": location,
        "job_type": job_type,
        "description": description,
        "url": url,
        "apply_url": job.get(
            "applyUrl",
            ""
        ),
        "updated_at": "",
        "fetched_at": fetched_at,
        "required_skills": []
    }