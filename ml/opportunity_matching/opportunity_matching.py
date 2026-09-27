import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SKILL_GAP_FILE = (
    BASE_DIR
    / "data"
    / "students"
    / "skill_gap_output.json"
)

OPPORTUNITIES_FILE = (
    BASE_DIR
    / "data"
    / "opportunities"
    / "opportunities_cache.json"
)

CAREERS_FILE = (
    BASE_DIR
    / "data"
    / "careers"
    / "careers.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "students"
    / "opportunity_results.json"
)


# Minimum career relevance required for recommendation
MIN_CAREER_RELEVANCE = 30.0


SKILL_ALIASES = {
    "github": "git",
    "git hub": "git",
    "ms excel": "microsoft excel",
    "excel": "microsoft excel",
    "microsoft excel": "microsoft excel",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "powerbi": "power bi",
    "power bi": "power bi",
    "vs code": "vs code",
    "visual studio code": "vs code"
}


def normalize_skill(skill):

    skill = skill.strip().lower()

    return SKILL_ALIASES.get(
        skill,
        skill
    )


def load_skill_gap():

    with open(
        SKILL_GAP_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_opportunities():

    with open(
        OPPORTUNITIES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return data.get(
            "opportunities",
            []
        )

    return []


def load_career_skills():

    careers = {}

    with open(
        CAREERS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            career = row.get(
                "career",
                ""
            ).strip()

            required_skills_text = row.get(
                "required_skills",
                ""
            ).strip()

            if not career:
                continue

            skills = set()

            for skill in required_skills_text.split("|"):

                if skill.strip():

                    skills.add(
                        normalize_skill(skill)
                    )

            careers[
                career.lower()
            ] = skills

    return careers


def get_student_skills(skill_gap_data):

    analysis = skill_gap_data.get(
        "skill_gap_analysis",
        {}
    )

    strong_skills = {
        normalize_skill(
            item.get("skill", "")
        )
        for item in analysis.get(
            "strong_skills",
            []
        )
        if item.get("skill")
    }

    developing_skills = {
        normalize_skill(
            item.get("skill", "")
        )
        for item in analysis.get(
            "developing_skills",
            []
        )
        if item.get("skill")
    }

    missing_skills = {
        normalize_skill(
            item.get("skill", "")
        )
        for item in analysis.get(
            "missing_skills",
            []
        )
        if item.get("skill")
    }

    return (
        strong_skills,
        developing_skills,
        missing_skills
    )


def get_opportunity_skills(opportunity):

    skills = opportunity.get(
        "required_skills",
        []
    )

    if not isinstance(skills, list):
        return set()

    return {
        normalize_skill(skill)
        for skill in skills
        if skill
    }


def calculate_career_relevance(
    job_skills,
    career_skills
):

    if not career_skills:
        return 0

    matched = job_skills.intersection(
        career_skills
    )

    relevance = (
        len(matched)
        / len(career_skills)
    ) * 100

    return round(
        relevance,
        2
    )


def calculate_job_skill_coverage(
    job_skills,
    career_skills
):

    if not job_skills:
        return 0

    career_relevant_job_skills = (
        job_skills.intersection(
            career_skills
        )
    )

    coverage = (
        len(career_relevant_job_skills)
        / len(job_skills)
    ) * 100

    return round(
        coverage,
        2
    )


def calculate_student_match(
    required_skills,
    strong_skills,
    developing_skills
):

    if not required_skills:
        return 0

    strong_match = (
        required_skills
        .intersection(strong_skills)
    )

    developing_match = (
        required_skills
        .intersection(developing_skills)
    )

    score = (
        len(strong_match) * 1.0
        +
        len(developing_match) * 0.5
    )

    return round(
        (score / len(required_skills))
        * 100,
        2
    )


def calculate_final_match(
    career_relevance,
    job_skill_coverage,
    student_match
):

    final_score = (
        career_relevance * 0.50
        +
        job_skill_coverage * 0.20
        +
        student_match * 0.30
    )

    # Prevent low-career-relevance jobs
    # from receiving a misleading high match score.
    if career_relevance < 40:

        final_score = min(
            final_score,
            career_relevance
        )

    return round(
        final_score,
        2
    )


def create_opportunity_id(opportunity):

    external_id = str(
        opportunity.get(
            "external_id",
            ""
        )
    ).strip()

    source = str(
        opportunity.get(
            "source",
            ""
        )
    ).strip()

    if source and external_id:

        return (
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
        return opportunity_id

    company = str(
        opportunity.get(
            "company",
            ""
        )
    ).strip()

    title = str(
        opportunity.get(
            "title",
            ""
        )
    ).strip()

    location = str(
        opportunity.get(
            "location",
            ""
        )
    ).strip()

    return (
        f"{company}:"
        f"{title}:"
        f"{location}"
    )


def build_recommendation(
    career_relevance,
    job_skill_coverage,
    matched,
    developing,
    missing
):

    why_this_matches = []

    for skill in sorted(matched):

        why_this_matches.append(
            f"{skill} — Strong"
        )

    for skill in sorted(developing):

        why_this_matches.append(
            f"{skill} — Developing"
        )

    if career_relevance >= 70:

        why_this_matches.append(
            "High career relevance"
        )

    elif career_relevance >= 30:

        why_this_matches.append(
            "Relevant to target career"
        )

    if job_skill_coverage >= 70:

        why_this_matches.append(
            "Strong career-skill coverage"
        )

    elif job_skill_coverage >= 40:

        why_this_matches.append(
            "Moderate career-skill coverage"
        )

    return {
        "why_this_matches":
            why_this_matches,

        "skills_to_improve":
            sorted(
                developing.union(missing)
            )
    }


def match_opportunities(
    skill_gap_data,
    opportunities
):

    student_id = skill_gap_data.get(
        "student_id"
    )

    analysis = skill_gap_data.get(
        "skill_gap_analysis",
        {}
    )

    target_career = analysis.get(
        "target_career",
        ""
    ).strip()

    career_skills_map = (
        load_career_skills()
    )

    career_skills = career_skills_map.get(
        target_career.lower(),
        set()
    )

    (
        strong_skills,
        developing_skills,
        missing_student_skills
    ) = get_student_skills(
        skill_gap_data
    )

    results = []

    for opportunity in opportunities:

        required_skills = (
            get_opportunity_skills(
                opportunity
            )
        )

        # Ignore opportunities with no
        # extracted skill information.
        if not required_skills:
            continue

        career_relevance = (
            calculate_career_relevance(
                required_skills,
                career_skills
            )
        )

        # Exclude clearly irrelevant jobs.
        if (
            career_relevance
            < MIN_CAREER_RELEVANCE
        ):
            continue

        job_skill_coverage = (
            calculate_job_skill_coverage(
                required_skills,
                career_skills
            )
        )

        matched = (
            required_skills
            .intersection(
                strong_skills
            )
        )

        developing = (
            required_skills
            .intersection(
                developing_skills
            )
        )

        missing = (
            required_skills
            - strong_skills
            - developing_skills
        )

        student_match = (
            calculate_student_match(
                required_skills,
                strong_skills,
                developing_skills
            )
        )

        final_match = (
            calculate_final_match(
                career_relevance,
                job_skill_coverage,
                student_match
            )
        )

        recommendation = (
            build_recommendation(
                career_relevance,
                job_skill_coverage,
                matched,
                developing,
                missing
            )
        )

        results.append({

            "opportunity_id":
                create_opportunity_id(
                    opportunity
                ),

            "title":
                opportunity.get(
                    "title",
                    ""
                ),

            "company":
                opportunity.get(
                    "company",
                    ""
                ),

            "source":
                opportunity.get(
                    "source",
                    ""
                ),

            "location":
                opportunity.get(
                    "location",
                    ""
                ),

            "job_type":
                opportunity.get(
                    "job_type",
                    ""
                ),

            "url":
                opportunity.get(
                    "url",
                    ""
                ),

            "fetched_at":
                opportunity.get(
                    "fetched_at",
                    ""
                ),

            "updated_at":
                opportunity.get(
                    "updated_at",
                    ""
                ),

            "career":
                target_career,

            "career_relevance":
                career_relevance,

            "job_skill_coverage":
                job_skill_coverage,

            "required_skills":
                sorted(required_skills),

            "matched_skills":
                sorted(matched),

            "developing_skills":
                sorted(developing),

            "missing_skills":
                sorted(missing),

            "match_percentage":
                final_match,

            "recommendation":
                recommendation,

            "skills_to_improve":
                recommendation[
                    "skills_to_improve"
                ]
        })

    # Sort recommendations by the student's final match score first.
    # Higher match percentage = better placement in the results.
    # Career relevance and job skill coverage are used as tie-breakers.
    results.sort(
        key=lambda item: (
            item["match_percentage"],
            item["career_relevance"],
            item["job_skill_coverage"]
        ),
        reverse=True
    )
    if not results:

        return {
            "student_id":
                student_id,

            "target_career":
                target_career,

            "status":
                "no_results",

            "message":
                (
                    "No sufficiently relevant "
                    "live opportunities found "
                    f"for {target_career}"
                ),

            "opportunities": []
        }

    return {
        "student_id":
            student_id,

        "target_career":
            target_career,

        "status":
            "success",

        "opportunities":
            results
    }


def main():

    skill_gap_data = (
        load_skill_gap()
    )

    opportunities = (
        load_opportunities()
    )

    print(
        "LIVE OPPORTUNITIES LOADED:",
        len(opportunities)
    )

    if not opportunities:

        result = {

            "student_id":
                skill_gap_data.get(
                    "student_id"
                ),

            "target_career":
                skill_gap_data.get(
                    "skill_gap_analysis",
                    {}
                ).get(
                    "target_career",
                    ""
                ),

            "status":
                "no_results",

            "message":
                "No live opportunities available.",

            "opportunities":
                []
        }

    else:

        result = (
            match_opportunities(
                skill_gap_data,
                opportunities
            )
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Output saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()