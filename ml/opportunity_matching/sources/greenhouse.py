import requests
from datetime import datetime, timezone


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


# --------------------------------------------------
# FETCH GREENHOUSE JOBS
# --------------------------------------------------

def fetch_greenhouse_jobs(board_token):
    """
    Fetch currently available jobs from a Greenhouse board.

    board_token must be the real Greenhouse board token.
    Never invent a board token.
    """

    if not board_token:
        raise ValueError(
            "Greenhouse board_token is required."
        )

    board_token = str(board_token).strip()

    if not board_token:
        raise ValueError(
            "Greenhouse board_token cannot be empty."
        )

    url = f"{BASE_URL}/{board_token}/jobs"

    response = requests.get(
        url,
        params={"content": "true"},
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    jobs = data.get("jobs", [])

    if not isinstance(jobs, list):
        return []

    return jobs


# --------------------------------------------------
# NORMALIZE GREENHOUSE JOB
# --------------------------------------------------

def normalize_greenhouse_job(job, company):
    """
    Convert a Greenhouse job into PathFinder's
    common opportunity format.

    Skill extraction is intentionally NOT done here.
    skill_extractor.py will handle that.
    """

    if not isinstance(job, dict):
        return None

    company = str(company or "").strip()

    external_id = str(
        job.get("id", "")
    ).strip()

    title = str(
        job.get("title", "")
    ).strip()

    location_data = job.get(
        "location",
        {}
    )

    if isinstance(location_data, dict):
        location = str(
            location_data.get(
                "name",
                ""
            )
        ).strip()
    else:
        location = str(
            location_data or ""
        ).strip()

    description = str(
        job.get("content", "")
    ).strip()

    url = str(
        job.get("absolute_url", "")
    ).strip()

    updated_at = str(
        job.get("updated_at", "")
    ).strip()

    # --------------------------------------------------
    # Do not create fake opportunities
    # --------------------------------------------------

    if not external_id:
        return None

    if not title:
        return None

    if not url:
        return None

    # --------------------------------------------------
    # Current fetch timestamp
    # --------------------------------------------------

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------
    # Greenhouse does not always expose a clean
    # job type field. Keep it empty rather than
    # guessing.
    # --------------------------------------------------

    job_type = ""

    return {
        "source": "Greenhouse",

        "company": company,

        "external_id": external_id,

        "title": title,

        "location": location,

        "job_type": job_type,

        "description": description,

        # IMPORTANT:
        # Use the actual Greenhouse URL.
        # Never construct or modify it.
        "url": url,

        "updated_at": updated_at,

        "fetched_at": fetched_at,

        # This will be filled by skill_extractor.py
        "required_skills": []
    }


# --------------------------------------------------
# FETCH + NORMALIZE
# --------------------------------------------------

def get_greenhouse_opportunities(
    board_token,
    company
):
    """
    Fetch and normalize Greenhouse jobs.

    If an individual job is malformed, skip it
    instead of crashing the complete source.
    """

    jobs = fetch_greenhouse_jobs(
        board_token
    )

    opportunities = []

    for job in jobs:

        normalized = normalize_greenhouse_job(
            job,
            company
        )

        if normalized is not None:
            opportunities.append(
                normalized
            )
    return opportunities