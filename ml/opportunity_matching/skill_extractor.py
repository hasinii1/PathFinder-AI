import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SKILLS_FILE = (
    BASE_DIR
    / "data"
    / "skills"
    / "skills.csv"
)


def load_skills():
    """
    Load the shared skill database used by the project.
    """
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


def normalize_text(text):
    """
    Normalize text for skill matching.
    """
    if not text:
        return ""

    text = str(text).lower()

    # Normalize common symbols
    text = text.replace("&", " and ")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def skill_found(text, skill):
    """
    Check whether a skill appears as a meaningful term
    in the job description.
    """

    text = normalize_text(text)
    skill = normalize_text(skill)

    if not text or not skill:
        return False

    # ---------------------------------------------------------
    # Special handling for one-character skills such as R and C
    # ---------------------------------------------------------
    #
    # A single letter can occur naturally in normal sentences.
    # Therefore, simply searching for standalone "R" or "C"
    # creates many false positives.
    #
    # Only accept the skill when it appears in a context that
    # strongly suggests it is being mentioned as a skill.
    #
    if len(skill) == 1:

        patterns = [
            rf"\b{re.escape(skill)}\s+programming\b",
            rf"\b{re.escape(skill)}\s+language\b",
            rf"\busing\s+{re.escape(skill)}\b",
            rf"\bwith\s+{re.escape(skill)}\b",
            rf"\bexperience\s+(?:in|with)\s+{re.escape(skill)}\b",
            rf"\b{re.escape(skill)}\s+skills?\b",
            rf"\b{re.escape(skill)}\s+software\b",
            rf"\b{re.escape(skill)}\s+development\b",
        ]

        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )

    # ---------------------------------------------------------
    # Normal skills
    # ---------------------------------------------------------
    #
    # Use word boundaries so that a skill such as SQL does not
    # accidentally match inside another word.
    #
    # re.escape() also protects special characters such as
    # + in C++.
    #
    pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

    return re.search(
        pattern,
        text,
        re.IGNORECASE
    ) is not None


def extract_skills(text):
    """
    Extract skills from job description using the shared
    skills.csv knowledge base.
    """

    if not text or not str(text).strip():
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


def extract_skill_names(text):
    """
    Return only skill names.
    """

    detected = extract_skills(text)

    return [
        item["skill"]
        for item in detected
    ]


def extract_opportunity_skills(text):
    """
    Extract skills from a live job/opportunity description.

    Returns a list of skill names so that the existing
    opportunity collector can use the function directly.
    """

    detected = extract_skills(text)

    return [
        item["skill"]
        for item in detected
    ]


if __name__ == "__main__":

    test_text = """
    We are looking for a Data Analyst with experience
    in Python, SQL, Pandas, Power BI and Microsoft Excel.
    Experience with R is also required.
    """

    print("Detected skills:")

    for skill in extract_skill_names(test_text):
        print("-", skill)

