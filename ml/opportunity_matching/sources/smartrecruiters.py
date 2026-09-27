import requests
from datetime import datetime, timezone

BASE_URL = "https://api.smartrecruiters.com/v1/companies"


def fetch_smartrecruiters_jobs(company_identifier):
    if not company_identifier:
        raise ValueError("SmartRecruiters company identifier is required.")

    company_identifier = str(company_identifier).strip()

    if not company_identifier:
        raise ValueError("SmartRecruiters company identifier cannot be empty.")

    url = f"{BASE_URL}/{company_identifier}/postings"

    response = requests.get(
        url,
        params={"limit": 100},
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    jobs = data.get("content", [])

    if not isinstance(jobs, list):
        return []

    return jobs


def normalize_smartrecruiters_job(job, company):
    if not isinstance(job, dict):
        return None

    company = str(company or "").strip()

    external_id = str(
        job.get("id") or ""
    ).strip()

    title = str(
        job.get("name") or ""
    ).strip()

    location_data = job.get("location", {})

    if isinstance(location_data, dict):
        city = str(
            location_data.get("city") or ""
        ).strip()

        region = str(
            location_data.get("region") or ""
        ).strip()

        country = str(
            location_data.get("country") or ""
        ).strip()

        location_parts = [
            value for value in [city, region, country]
            if value
        ]

        location = ", ".join(location_parts)

    else:
        location = str(location_data or "").strip()

    job_type = str(
        job.get("typeOfEmployment") or ""
    ).strip()

    description = str(
        job.get("jobAd", {}).get("sections", [{}])[0].get("text", "")
        if isinstance(job.get("jobAd"), dict)
        else ""
    ).strip()

    url = str(
        job.get("ref") or ""
    ).strip()

    if not external_id or not title or not url:
        return None

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "source": "SmartRecruiters",
        "company": company,
        "external_id": external_id,
        "title": title,
        "location": location,
        "job_type": job_type,
        "description": description,
        "url": url,
        "updated_at": "",
        "fetched_at": fetched_at,
        "required_skills": []
    }


def get_smartrecruiters_opportunities(
    company_identifier,
    company
):
    jobs = fetch_smartrecruiters_jobs(
        company_identifier
    )

    opportunities = []

    for job in jobs:

        normalized = normalize_smartrecruiters_job(
            job,
            company
        )

        if normalized is not None:
            opportunities.append(normalized)

    return opportunities