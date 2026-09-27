import json
import re
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROFILE_FILE = BASE_DIR / "data" / "students" / "profile_output.json"
ASSESSMENT_FILE = BASE_DIR / "data" / "students" / "assessment_output.json"
SKILLS_FILE = BASE_DIR / "data" / "skills" / "skills.csv"
CAREERS_FILE = BASE_DIR / "data" / "careers" / "careers.csv"
OUTPUT_FILE = BASE_DIR / "data" / "students" / "skill_gap_output.json"


# ============================================================
# SKILL NORMALIZATION
# ============================================================

def normalize_skill(skill: str) -> str:
    """
    Normalize skill names so that equivalent names are treated
    as the same skill.

    Important:
    Matplotlib, Plotly and Seaborn remain separate skills.
    """

    if not skill:
        return ""

    skill = str(skill).strip().lower()
    skill = re.sub(r"\s+", " ", skill)

    aliases = {
        # Git
        "github": "git",
        "git hub": "git",
        "git": "git",

        # Excel
        "microsoft excel": "excel",
        "ms excel": "excel",
        "excel": "excel",

        # Scikit-learn
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "scikit-learn": "scikit-learn",

        # Artificial Intelligence
        "ai": "artificial intelligence",
        "artificial intelligence": "artificial intelligence",
        "artificial-intelligence": "artificial intelligence",

        # Machine Learning
        "ml": "machine learning",
        "machine learning": "machine learning",
        "machine-learning": "machine learning",

        # NLP
        "nlp": "natural language processing",
        "natural language processing": "natural language processing",

        # OOP
        "oop": "object oriented programming",
        "object-oriented programming": "object oriented programming",
        "object oriented programming": "object oriented programming",

        # VS Code
        "vs code": "visual studio code",
        "visual studio code": "visual studio code",

        # Power BI
        "power bi": "power bi",

        # Keep visualization libraries separate
        "matplotlib": "matplotlib",
        "plotly": "plotly",
        "seaborn": "seaborn",

        # Data Visualization itself remains separate
        "data visualization": "data visualization",
    }

    return aliases.get(skill, skill)


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path: Path) -> dict:
    """Load JSON data from a file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# LOAD SKILLS KNOWLEDGE BASE
# ============================================================

def load_skills() -> pd.DataFrame:
    """
    Load the shared skills knowledge base.
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


# ============================================================
# LOAD CAREER KNOWLEDGE BASE
# ============================================================

def load_careers() -> pd.DataFrame:
    """
    Load career-specific required skills.
    """

    if not CAREERS_FILE.exists():
        raise FileNotFoundError(
            f"Careers file not found: {CAREERS_FILE}"
        )

    careers_df = pd.read_csv(CAREERS_FILE)

    required_columns = {"career", "required_skills"}

    if not required_columns.issubset(careers_df.columns):
        raise ValueError(
            "careers.csv must contain 'career' and 'required_skills' columns."
        )

    return careers_df


# ============================================================
# TARGET CAREER
# ============================================================

def get_target_career(profile: dict):
    """
    Get the student's explicitly selected target career.

    The target career should come from the profile/UI.
    It is NOT extracted from the resume career objective.
    """

    target_career = profile.get("target_career")

    if not target_career:
        return None

    return str(target_career).strip()


# ============================================================
# EXTRACT PROFILE SKILLS
# ============================================================

def extract_profile_skills(profile: dict) -> set:
    """
    Extract all skills from the student's profile.
    """

    profile_skills = set()

    skills_data = profile.get("skills", {})

    if isinstance(skills_data, dict):

        for skill_list in skills_data.values():

            if isinstance(skill_list, list):

                for skill in skill_list:

                    normalized = normalize_skill(skill)

                    if normalized:
                        profile_skills.add(normalized)

    elif isinstance(skills_data, list):

        for skill in skills_data:

            normalized = normalize_skill(skill)

            if normalized:
                profile_skills.add(normalized)

    return profile_skills


# ============================================================
# GET ASSESSMENT DATA
# ============================================================

def get_assessment(assessment: dict) -> dict:
    """
    Extract skill scores from assessment_output.json.
    """

    assessment_data = assessment.get(
        "skill_assessment",
        {}
    )

    normalized_assessment = {}

    if not isinstance(assessment_data, dict):
        return normalized_assessment

    for skill, details in assessment_data.items():

        normalized_skill = normalize_skill(skill)

        if not normalized_skill:
            continue

        if isinstance(details, dict):

            score = details.get("score", 0)

        else:

            score = details

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0

        normalized_assessment[normalized_skill] = {
            "score": score,
            "original_skill": skill,
            "details": details
        }

    return normalized_assessment


# ============================================================
# FIND CAREER
# ============================================================

def find_career(
    careers_df: pd.DataFrame,
    target_career: str
):
    """
    Find the selected career from careers.csv.
    """

    target_normalized = target_career.strip().lower()

    for _, row in careers_df.iterrows():

        career_name = str(row["career"]).strip()

        if career_name.lower() == target_normalized:
            return row

    return None


# ============================================================
# GET REQUIRED CAREER SKILLS
# ============================================================

def get_required_skills(career_row) -> list:
    """
    Get and normalize required skills for the target career.
    """

    raw_skills = str(
        career_row["required_skills"]
    ).split("|")

    required_skills = []

    for skill in raw_skills:

        normalized = normalize_skill(skill)

        if normalized and normalized not in required_skills:
            required_skills.append(normalized)

    return required_skills


# ============================================================
# CALCULATE SKILL GAPS
# ============================================================

def calculate_skill_gaps(
    profile: dict,
    assessment: dict,
    careers_df: pd.DataFrame
) -> dict:

    target_career = get_target_career(profile)

    # --------------------------------------------------------
    # No career selected
    # --------------------------------------------------------

    if not target_career:

        return {
            "target_career": None,
            "status": "Career selection required",
            "required_skills": [],
            "strong_skills": [],
            "developing_skills": [],
            "missing_skills": [],
            "career_readiness_percentage": 0
        }

    # --------------------------------------------------------
    # Find career
    # --------------------------------------------------------

    career_row = find_career(
        careers_df,
        target_career
    )

    if career_row is None:

        return {
            "target_career": target_career,
            "status": "Career not found in career knowledge base",
            "required_skills": [],
            "strong_skills": [],
            "developing_skills": [],
            "missing_skills": [],
            "career_readiness_percentage": 0
        }

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_skills = get_required_skills(
        career_row
    )

    # --------------------------------------------------------
    # Assessment
    # --------------------------------------------------------

    assessment_data = get_assessment(
        assessment
    )

    # --------------------------------------------------------
    # Skill categories
    # --------------------------------------------------------

    strong_skills = []
    developing_skills = []
    missing_skills = []

    total_score = 0

    # --------------------------------------------------------
    # Compare required skills with student's skills
    # --------------------------------------------------------

    for skill in required_skills:

        skill_data = assessment_data.get(skill)

        if skill_data is None:

            # Student does not have the required skill
            missing_skills.append({
                "skill": skill,
                "score": 0,
                "level": "Missing"
            })

            continue

        score = float(
            skill_data.get("score", 0)
        )

        total_score += score

        # ----------------------------------------------------
        # Strong
        # ----------------------------------------------------

        if score >= 75:

            strong_skills.append({
                "skill": skill,
                "score": score,
                "level": skill_data.get(
                    "details",
                    {}
                ).get("level", "Intermediate")
            })

        # ----------------------------------------------------
        # Developing
        # ----------------------------------------------------

        elif score > 0:

            developing_skills.append({
                "skill": skill,
                "score": score,
                "level": skill_data.get(
                    "details",
                    {}
                ).get("level", "Beginner")
            })

        # ----------------------------------------------------
        # Missing
        # ----------------------------------------------------

        else:

            missing_skills.append({
                "skill": skill,
                "score": 0,
                "level": "Missing"
            })

    # --------------------------------------------------------
    # Career readiness
    # --------------------------------------------------------

    if required_skills:

        career_readiness = (
            total_score /
            (len(required_skills) * 100)
        ) * 100

    else:

        career_readiness = 0

    career_readiness = round(
        career_readiness,
        2
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "target_career": target_career,
        "status": "Career skill gap analysis completed",
        "required_skills": required_skills,
        "strong_skills": strong_skills,
        "developing_skills": developing_skills,
        "missing_skills": missing_skills,
        "career_readiness_percentage": career_readiness
    }


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(
    profile: dict,
    gap_analysis: dict
):

    output = {
        "student_id": profile.get(
            "student_id",
            "S001"
        ),
        "skill_gap_analysis": gap_analysis
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )




def get_display_skill_name(skill: str) -> str:
    """Convert normalized skill names into user-friendly display names."""
    display_names = {
        "python": "Python", "sql": "SQL", "pandas": "Pandas", "numpy": "NumPy",
        "scikit-learn": "Scikit-learn", "machine learning": "Machine Learning",
        "data science": "Data Science", "data analytics": "Data Analytics",
        "data preprocessing": "Data Preprocessing", "data visualization": "Data Visualization",
        "power bi": "Power BI", "excel": "Microsoft Excel", "matplotlib": "Matplotlib",
        "plotly": "Plotly", "seaborn": "Seaborn", "statistics": "Statistics",
        "tableau": "Tableau", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
        "artificial intelligence": "Artificial Intelligence", "deep learning": "Deep Learning",
        "natural language processing": "Natural Language Processing", "git": "Git",
        "object oriented programming": "Object Oriented Programming", "data structures": "Data Structures",
        "algorithms": "Algorithms", "javascript": "JavaScript", "typescript": "TypeScript",
        "html": "HTML", "css": "CSS", "react": "React", "node.js": "Node.js",
        "fastapi": "FastAPI", "flask": "Flask", "docker": "Docker", "aws": "AWS",
    }
    return display_names.get(skill.lower(), skill)

# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(
    profile: dict,
    gap_analysis: dict
):

    print("\nSKILL GAP ANALYSIS\n")

    print(
        "Skill gap analysis completed successfully."
    )

    print(
        f"Student ID: {profile.get('student_id', 'S001')}"
    )

    print(
        f"Target Career: "
        f"{gap_analysis['target_career']}"
    )

    print(
        f"Status: "
        f"{gap_analysis['status']}"
    )

    print(
        f"Career Readiness: "
        f"{gap_analysis['career_readiness_percentage']}%"
    )

    print("\nStrong Skills:")

    if gap_analysis["strong_skills"]:

        for item in gap_analysis["strong_skills"]:

            print(
                f"{get_display_skill_name(item['skill'])} "
                f"{item['score']} "
                f"{item['level']}"
            )

    else:

        print("None")

    print("\nDeveloping Skills:")

    if gap_analysis["developing_skills"]:

        for item in gap_analysis["developing_skills"]:

            print(
                f"{get_display_skill_name(item['skill'])} "
                f"{item['score']} "
                f"{item['level']}"
            )

    else:

        print("None")

    print("\nMissing Skills:")

    if gap_analysis["missing_skills"]:

        for item in gap_analysis["missing_skills"]:

            print(
                f"{get_display_skill_name(item['skill'])} "
                f"{item['score']} "
                f"{item['level']}"
            )

    else:

        print("None")

    print(
        f"\nOutput file:\n{OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Load profile
    profile = load_json(
        PROFILE_FILE
    )

    # Load assessment
    assessment = load_json(
        ASSESSMENT_FILE
    )

    # Load career knowledge base
    careers_df = load_careers()

    # Calculate skill gaps
    gap_analysis = calculate_skill_gaps(
        profile,
        assessment,
        careers_df
    )

    # Save result
    save_output(
        profile,
        gap_analysis
    )

    # Display result
    display_result(
        profile,
        gap_analysis
    )


if __name__ == "__main__":
    main()