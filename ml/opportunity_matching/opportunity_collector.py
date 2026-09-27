import csv
import json
from pathlib import Path

from .sources.greenhouse import (
    fetch_greenhouse_jobs,
    normalize_greenhouse_job
)

from .sources.lever import (
    fetch_lever_jobs,
    normalize_lever_job
)

from .sources.ashby import (
    fetch_ashby_jobs,
    normalize_ashby_job
)

from .sources.smartrecruiters import (
    fetch_smartrecruiters_jobs,
    normalize_smartrecruiters_job
)

from .skill_extractor import extract_opportunity_skills


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCES_FILE = BASE_DIR / "data" / "opportunities" / "opportunity_sources.csv"
CACHE_FILE = BASE_DIR / "data" / "opportunities" / "opportunities_cache.json"


def load_sources():
    sources = []

    with open(SOURCES_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row.get("enabled", "").lower() == "true":
                sources.append(row)

    return sources


def add_required_skills(opportunity):
    required_skills = extract_opportunity_skills(opportunity)
    opportunity["required_skills"] = required_skills

    return opportunity


def collect_opportunities():
    opportunities = []

    sources = load_sources()

    for source in sources:

        source_type = source.get("source_type", "").strip().lower()
        company = source.get("company", "").strip()
        identifier = source.get("identifier", "").strip()

        try:

            # -------------------------
            # GREENHOUSE
            # -------------------------
            if source_type == "greenhouse":

                jobs = fetch_greenhouse_jobs(identifier)

                for job in jobs:

                    normalized = normalize_greenhouse_job(
                        job,
                        company
                    )

                    if normalized is not None:
                        normalized = add_required_skills(normalized)
                        opportunities.append(normalized)

            # -------------------------
            # LEVER
            # -------------------------
            elif source_type == "lever":

                jobs = fetch_lever_jobs(identifier)

                for job in jobs:

                    normalized = normalize_lever_job(
                        job,
                        company
                    )

                    if normalized is not None:
                        normalized = add_required_skills(normalized)
                        opportunities.append(normalized)

            # -------------------------
            # ASHBY
            # -------------------------
            elif source_type == "ashby":

                jobs = fetch_ashby_jobs(identifier)

                for job in jobs:

                    normalized = normalize_ashby_job(
                        job,
                        company
                    )

                    if normalized is not None:
                        normalized = add_required_skills(normalized)
                        opportunities.append(normalized)

            # -------------------------
            # SMARTRECRUITERS
            # -------------------------
            elif source_type == "smartrecruiters":

                jobs = fetch_smartrecruiters_jobs(identifier)

                for job in jobs:

                    normalized = normalize_smartrecruiters_job(
                        job,
                        company
                    )

                    if normalized is not None:
                        normalized = add_required_skills(normalized)
                        opportunities.append(normalized)

        except Exception as error:

            print(
                f"Failed to fetch {company} "
                f"({source_type}): {error}"
            )

    return opportunities


def deduplicate_opportunities(opportunities):

    unique = {}

    for opportunity in opportunities:

        source = str(
            opportunity.get("source", "")
        ).strip()

        external_id = str(
            opportunity.get("external_id", "")
        ).strip()

        company = str(
            opportunity.get("company", "")
        ).strip()

        title = str(
            opportunity.get("title", "")
        ).strip()

        location = str(
            opportunity.get("location", "")
        ).strip()

        # Primary unique identifier
        if source and external_id:

            key = f"{source}:{external_id}"

        # Fallback identifier
        else:

            key = f"{company}:{title}:{location}"

        if key not in unique:

            unique[key] = opportunity

    return list(unique.values())


def save_cache(opportunities):

    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "opportunities": opportunities
            },
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    opportunities = collect_opportunities()

    opportunities = deduplicate_opportunities(
        opportunities
    )

    save_cache(opportunities)

    print(
        f"Collected {len(opportunities)} live opportunities."
    )

    print(
        f"Saved to: {CACHE_FILE}"
    )


if __name__ == "__main__":
    main()