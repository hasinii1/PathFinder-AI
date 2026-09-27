import re
import pandas as pd
from pathlib import Path


SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills" / "skills.csv"


def load_skills() -> pd.DataFrame:
    """Load the skill knowledge base."""

    if not SKILLS_FILE.exists():
        raise FileNotFoundError(
            f"Skills file not found: {SKILLS_FILE}"
        )

    skills_df = pd.read_csv(SKILLS_FILE)

    required_columns = {"skill", "category"}

    if not required_columns.issubset(skills_df.columns):
        raise ValueError(
            "skills.csv must contain 'skill' and 'category' columns."
        )

    return skills_df


def skill_found(text: str, skill: str) -> bool:
    """
    Check whether a skill appears in the resume text.
    """

    # Normalize whitespace
    normalized_text = re.sub(r"\s+", " ", text.lower()).strip()
    normalized_skill = re.sub(r"\s+", " ", skill.lower()).strip()

    # Escape special regex characters in the skill name
    pattern = re.escape(normalized_skill)

    # Word-boundary matching for safer detection
    return re.search(rf"(?<!\w){pattern}(?!\w)", normalized_text) is not None


def extract_skills(text: str) -> list[dict]:
    """
    Extract skills from resume text using the skill knowledge base.
    """

    if not text or not text.strip():
        return []

    skills_df = load_skills()

    detected_skills = []

    for _, row in skills_df.iterrows():
        skill = str(row["skill"]).strip()
        category = str(row["category"]).strip()

        if skill_found(text, skill):
            detected_skills.append(
                {
                    "skill": skill,
                    "category": category
                }
            )

    return detected_skills


def get_skills_by_category(detected_skills: list[dict]) -> dict:
    """
    Group detected skills by category.
    """

    categorized = {}

    for item in detected_skills:
        category = item["category"]
        skill = item["skill"]

        if category not in categorized:
            categorized[category] = []

        categorized[category].append(skill)

    return categorized


if __name__ == "__main__":
    print("Skill extraction module is ready.")