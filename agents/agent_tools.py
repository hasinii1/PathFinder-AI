import json
from pathlib import Path


# ============================================================
# PATHFINDER AI - CAREER AGENT TOOLS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

STUDENT_DIR = BASE_DIR / "data" / "students"
OPPORTUNITIES_FILE = (
    BASE_DIR
    / "data"
    / "opportunities"
    / "opportunities_cache.json"
)


# ============================================================
# GENERIC JSON LOADER
# ============================================================

def _load_json(filename):
    path = STUDENT_DIR / filename

    if not path.exists():
        return {
            "status": "not_available",
            "message": f"{filename} was not found."
        }

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# ============================================================
# STUDENT DATA TOOLS
# ============================================================

def get_student_profile():
    """
    Returns the student's analyzed profile.
    """
    return _load_json("profile_output.json")


def get_skill_assessment():
    """
    Returns the student's skill assessment.
    """
    return _load_json("assessment_output.json")


def get_skill_gaps():
    """
    Returns the student's detected skill gaps.
    """
    return _load_json("skill_gap_output.json")


def get_opportunity_matches():
    """
    Returns the existing opportunity matching results.

    IMPORTANT:
    We do not send the entire live opportunity database
    to Gemini.
    """
    return _load_json("opportunity_results.json")


def get_roadmap():
    """
    Returns the personalized roadmap.
    """
    return _load_json("roadmap_output.json")


# ============================================================
# OPPORTUNITY DATABASE SUMMARY
# ============================================================

def get_opportunity_summary():
    """
    Provides a lightweight summary of the live opportunity
    database instead of sending thousands of jobs to Gemini.
    """

    if not OPPORTUNITIES_FILE.exists():
        return {
            "status": "not_available",
            "message": "Opportunity cache was not found."
        }

    try:
        with open(OPPORTUNITIES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        opportunities = data.get("opportunities", [])

        companies = {}

        for opportunity in opportunities:
            company = str(
                opportunity.get("company", "Unknown")
            ).strip()

            if not company:
                company = "Unknown"

            companies[company] = companies.get(company, 0) + 1

        top_companies = sorted(
            companies.items(),
            key=lambda item: item[1],
            reverse=True
        )[:15]

        return {
            "total_opportunities": len(opportunities),
            "unique_companies": len(companies),
            "top_companies": [
                {
                    "company": company,
                    "count": count
                }
                for company, count in top_companies
            ]
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


# ============================================================
# RELEVANT OPPORTUNITY RESULTS
# ============================================================

def get_relevant_opportunities(limit=10):
    """
    Returns only the highest-ranked opportunities from the
    existing matching results.

    This prevents the LLM from receiving thousands of jobs.
    """

    data = get_opportunity_matches()

    if not isinstance(data, dict):
        return []

    opportunities = data.get("opportunities", [])

    if not isinstance(opportunities, list):
        return []

    def get_score(item):
        try:
            return float(
                item.get("match_score", 0)
            )
        except Exception:
            return 0.0

    sorted_opportunities = sorted(
        opportunities,
        key=get_score,
        reverse=True
    )

    selected = []

    for opportunity in sorted_opportunities[:limit]:

        selected.append({
            "company": opportunity.get("company"),
            "title": opportunity.get("title"),
            "location": opportunity.get("location"),
            "match_score": opportunity.get("match_score"),
            "url": opportunity.get("url"),
            "recommendations": opportunity.get(
                "recommendations",
                []
            )
        })

    return selected


# ============================================================
# CAREER SIMULATOR DATA
# ============================================================

def get_career_simulator_data():
    """
    Provides the data required for career simulation.
    """

    return {
        "profile": get_student_profile(),
        "skill_assessment": get_skill_assessment(),
        "skill_gaps": get_skill_gaps(),
        "roadmap": get_roadmap()
    }


# ============================================================
# COMPLETE AGENT CONTEXT
# ============================================================

def get_all_student_context():
    """
    Builds a compact context package for the Career Navigator.

    Large opportunity datasets are deliberately excluded.
    """

    return {
        "profile": get_student_profile(),

        "skill_assessment": get_skill_assessment(),

        "skill_gaps": get_skill_gaps(),

        "top_opportunities": get_relevant_opportunities(
            limit=10
        ),

        "roadmap": get_roadmap(),

        "career_simulator": get_career_simulator_data(),

        "opportunity_summary": get_opportunity_summary()
    }