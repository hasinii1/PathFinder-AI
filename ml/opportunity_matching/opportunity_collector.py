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

SOURCES_FILE = (
    BASE_DIR
    / "data"
    / "opportunities"
    / "opportunity_sources.csv"
)

CACHE_FILE = (
    BASE_DIR
    / "data"
    / "opportunities"
    / "opportunities_cache.json"
)


def load_sources():
    """
    Load all enabled opportunity sources.
    """

    sources = []

    with open(
        SOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row.get("enabled", "")
                .strip()
                .lower()
                == "true"
            ):

                sources.append(row)

    return sources


def add_required_skills(opportunity):
    """
    Extract skills from the opportunity
    and store them in required_skills.
    """

    required_skills = (
        extract_opportunity_skills(
            opportunity
        )
    )

    opportunity["required_skills"] = (
        required_skills
    )

    return opportunity


def normalize_jobs(
    source_type,
    jobs,
    company
):
    """
    Normalize jobs according to their source.
    """

    normalized_jobs = []

    for job in jobs:

        normalized = None

        if source_type == "greenhouse":

            normalized = (
                normalize_greenhouse_job(
                    job,
                    company
                )
            )

        elif source_type == "lever":

            normalized = (
                normalize_lever_job(
                    job,
                    company
                )
            )

        elif source_type == "ashby":

            normalized = (
                normalize_ashby_job(
                    job,
                    company
                )
            )

        elif source_type == "smartrecruiters":

            normalized = (
                normalize_smartrecruiters_job(
                    job,
                    company
                )
            )

        if normalized is not None:

            normalized_jobs.append(
                normalized
            )

    return normalized_jobs


def collect_opportunities():
    """
    Collect ALL live opportunities from
    every enabled source.

    No per-company job limit is applied.
    """

    opportunities = []

    sources = load_sources()

    print(
        f"Enabled sources: {len(sources)}"
    )

    print("=" * 70)

    for source in sources:

        source_type = (
            source
            .get("source_type", "")
            .strip()
            .lower()
        )

        company = (
            source
            .get("company", "")
            .strip()
        )

        identifier = (
            source
            .get("identifier", "")
            .strip()
        )

        print(
            f"Fetching: {company} "
            f"({source_type})"
        )

        try:

            # -------------------------------------------------
            # FETCH ALL LIVE JOBS
            # -------------------------------------------------

            if source_type == "greenhouse":

                jobs = (
                    fetch_greenhouse_jobs(
                        identifier
                    )
                )

            elif source_type == "lever":

                jobs = (
                    fetch_lever_jobs(
                        identifier
                    )
                )

            elif source_type == "ashby":

                jobs = (
                    fetch_ashby_jobs(
                        identifier
                    )
                )

            elif source_type == "smartrecruiters":

                jobs = (
                    fetch_smartrecruiters_jobs(
                        identifier
                    )
                )

            else:

                print(
                    f"Unsupported source type: "
                    f"{source_type}"
                )

                print("-" * 70)

                continue

            # -------------------------------------------------
            # SHOW TOTAL LIVE JOBS
            # -------------------------------------------------

            print(
                f"  Live jobs found: "
                f"{len(jobs)}"
            )

            # -------------------------------------------------
            # NORMALIZE ALL JOBS
            # -------------------------------------------------

            normalized_jobs = normalize_jobs(
                source_type,
                jobs,
                company
            )

            print(
                f"  Normalized jobs: "
                f"{len(normalized_jobs)}"
            )

            # -------------------------------------------------
            # EXTRACT SKILLS
            # -------------------------------------------------

            added = 0

            for opportunity in normalized_jobs:

                try:

                    opportunity = (
                        add_required_skills(
                            opportunity
                        )
                    )

                    opportunities.append(
                        opportunity
                    )

                    added += 1

                except Exception as error:

                    print(
                        f"  Skill extraction failed "
                        f"for {company}: {error}"
                    )

            print(
                f"  Added: {added}"
            )

        except Exception as error:

            print(
                f"Failed to fetch {company} "
                f"({source_type}): {error}"
            )

        print("-" * 70)

    return opportunities


def create_unique_key(opportunity):
    """
    Create a stable key for duplicate detection.

    Priority:
    1. source + external_id
    2. opportunity_id
    3. company + title + location + url
    4. company + title + location
    """

    source = str(
        opportunity.get(
            "source",
            ""
        )
    ).strip().lower()

    external_id = str(
        opportunity.get(
            "external_id",
            ""
        )
    ).strip()

    if source and external_id:

        return (
            "external:"
            f"{source}:"
            f"{external_id}"
        )

    opportunity_id = str(
        opportunity.get(
            "opportunity_id",
            ""
        )
    ).strip()

    if opportunity_id:

        return (
            "opportunity:"
            f"{opportunity_id}"
        )

    company = str(
        opportunity.get(
            "company",
            ""
        )
    ).strip().lower()

    title = str(
        opportunity.get(
            "title",
            ""
        )
    ).strip().lower()

    location = str(
        opportunity.get(
            "location",
            ""
        )
    ).strip().lower()

    url = str(
        opportunity.get(
            "url",
            ""
        )
    ).strip().lower()

    # If URL exists, use it because
    # it is usually more specific.
    if company and title and location and url:

        return (
            "fallback:"
            f"{company}|"
            f"{title}|"
            f"{location}|"
            f"{url}"
        )

    return (
        "fallback:"
        f"{company}|"
        f"{title}|"
        f"{location}"
    )


def deduplicate_opportunities(
    opportunities
):
    """
    Remove duplicate opportunities.

    The first occurrence is retained.
    """

    unique = {}

    duplicate_count = 0

    for opportunity in opportunities:

        key = create_unique_key(
            opportunity
        )

        if key in unique:

            duplicate_count += 1

            continue

        unique[key] = opportunity

    print(
        f"Duplicates removed: "
        f"{duplicate_count}"
    )

    return list(
        unique.values()
    )


def save_cache(opportunities):
    """
    Save opportunities in the same
    JSON structure expected by the
    matching system.
    """

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

    print("=" * 70)

    print(
        "PATHFINDER AI - LIVE OPPORTUNITY COLLECTOR"
    )

    print(
        "Collecting ALL live opportunities"
    )

    print("=" * 70)

    try:

        opportunities = (
            collect_opportunities()
        )

    except KeyboardInterrupt:

        print()

        print(
            "Collection stopped by user."
        )

        print(
            "Existing opportunities_cache.json "
            "was NOT modified."
        )

        return

    print()

    print(
        "=" * 70
    )

    print(
        "Removing duplicate opportunities..."
    )

    print(
        "=" * 70
    )

    original_count = len(
        opportunities
    )

    opportunities = (
        deduplicate_opportunities(
            opportunities
        )
    )

    final_count = len(
        opportunities
    )

    print(
        f"Opportunities collected: "
        f"{original_count}"
    )

    print(
        f"Unique opportunities: "
        f"{final_count}"
    )

    print(
        f"Duplicates removed: "
        f"{original_count - final_count}"
    )

    # ---------------------------------------------------------
    # SAVE ONLY AFTER COMPLETE COLLECTION
    # ---------------------------------------------------------

    save_cache(
        opportunities
    )

    print()

    print(
        "=" * 70
    )

    print(
        "Collection completed successfully."
    )

    print(
        f"Saved to: {CACHE_FILE}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()