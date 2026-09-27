import json
from pathlib import Path
import re

# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

PROFILE_FILE = (
    PROJECT_ROOT
    / "data"
    / "students"
    / "profile_output.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "students"
    / "assessment_output.json"
)


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_ALIASES = {
    "github": "git",
    "git hub": "git",
    "microsoft excel": "excel",
    "ms excel": "excel",
    "power bi": "power bi",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "machine-learning": "machine learning",
    "artificial-intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "vs code": "visual studio code",
    "visual studio code": "visual studio code",
}


def normalize_skill(skill):
    if not isinstance(skill, str):
        return ""

    skill = skill.strip().lower()

    return SKILL_ALIASES.get(skill, skill)


# ============================================================
# LOAD PROFILE
# ============================================================

def load_profile():

    if not PROFILE_FILE.exists():
        raise FileNotFoundError(
            f"Profile file not found:\n{PROFILE_FILE}"
        )

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# EXTRACT PROFILE SKILLS
# ============================================================

def extract_skills(profile):

    skills = []

    skill_data = profile.get("skills", {})

    if isinstance(skill_data, dict):

        for category_skills in skill_data.values():

            if isinstance(category_skills, list):

                for skill in category_skills:

                    normalized = normalize_skill(skill)

                    if (
                        normalized
                        and normalized not in skills
                    ):
                        skills.append(normalized)

    return skills


# ============================================================
# COLLECT EVIDENCE
# ============================================================

def collect_evidence(profile):

    project_text = ""
    internship_text = ""
    certification_text = ""

    # ---------------- PROJECTS ----------------

    projects = profile.get("projects", [])

    if isinstance(projects, list):

        for project in projects:

            if not isinstance(project, dict):
                continue

            project_text += " "

            project_text += str(
                project.get("name", "")
            )

            description = project.get(
                "description",
                []
            )

            if isinstance(description, list):

                project_text += " " + " ".join(
                    str(item)
                    for item in description
                )

            else:

                project_text += " " + str(
                    description
                )

    # ---------------- INTERNSHIPS ----------------

    internships = profile.get(
        "internships",
        []
    )

    if isinstance(internships, list):

        for internship in internships:

            if not isinstance(internship, dict):
                continue

            internship_text += " "

            internship_text += str(
                internship.get("role", "")
            )

            internship_text += " "

            internship_text += str(
                internship.get(
                    "organization",
                    ""
                )
            )

            description = internship.get(
                "description",
                []
            )

            if isinstance(description, list):

                internship_text += " " + " ".join(
                    str(item)
                    for item in description
                )

            else:

                internship_text += " " + str(
                    description
                )

    # ---------------- CERTIFICATIONS ----------------

    certifications = profile.get(
        "certifications",
        []
    )

    if isinstance(certifications, list):

        certification_text = " ".join(
            str(certification)
            for certification in certifications
        )

    return (
        project_text.lower(),
        internship_text.lower(),
        certification_text.lower()
    )


# ============================================================
# CHECK EVIDENCE
# ============================================================

def skill_in_text(skill, text):

    if not skill or not text:
        return False

    skill = normalize_skill(skill)
    text = text.lower()

    if not skill:
        return False

    # Normalize common variations in the evidence text
    text = re.sub(r"\bsklearn\b", "scikit-learn", text)
    text = re.sub(r"\bscikit[\s-]learn\b", "scikit-learn", text)
    text = re.sub(r"\bmachine[\s-]learning\b", "machine learning", text)
    text = re.sub(r"\bartificial[\s-]intelligence\b", "artificial intelligence", text)
    text = re.sub(r"\bgit[\s-]?hub\b", "git", text)
    text = re.sub(r"\bmicrosoft\s+excel\b", "excel", text)
    text = re.sub(r"\bms\s+excel\b", "excel", text)
    text = re.sub(r"\bpower\s*bi\b", "power bi", text)
    text = re.sub(r"\bvs\s*code\b", "visual studio code", text)

    # Match the complete skill, not a substring inside another word
    skill_pattern = re.escape(skill)

    pattern = (
        r"(?<![\w+#.])"
        + skill_pattern
        + r"(?![\w+#.])"
    )

    return re.search(pattern, text) is not None
    


# ============================================================
# ASSESS ONE SKILL
# ============================================================

def assess_skill(
    skill,
    project_text,
    internship_text,
    certification_text
):

    has_project = skill_in_text(
        skill,
        project_text
    )

    has_internship = skill_in_text(
        skill,
        internship_text
    )

    has_certification = skill_in_text(
        skill,
        certification_text
    )

    # --------------------------------------------------------
    # ORIGINAL REQUIRED SCORING
    # --------------------------------------------------------

    score = 40
    evidence = ["Profile"]

    if has_project:

        score += 25
        evidence.append("Project")

    if has_internship:

        score += 25
        evidence.append("Internship")

    if has_certification:

        evidence.append("Certification")

    # +10 when evidence comes from at least
    # two different source types
    if len(evidence) >= 2:

        score += 10

    score = min(score, 100)

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    if score >= 80:

        level = "Advanced"

    elif score >= 60:

        level = "Intermediate"

    else:

        level = "Beginner"

    return {
        "level": level,
        "score": score,
        "evidence": evidence
    }


# ============================================================
# BUILD ASSESSMENT
# ============================================================

def build_assessment(profile):

    skills = extract_skills(profile)

    (
        project_text,
        internship_text,
        certification_text
    ) = collect_evidence(profile)

    assessment = {}

    for skill in skills:

        assessment[skill] = assess_skill(
            skill,
            project_text,
            internship_text,
            certification_text
        )

    return assessment


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(
    profile,
    assessment
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    scores = [
        result["score"]
        for result in assessment.values()
    ]

    overall_score = (
        round(sum(scores) / len(scores), 2)
        if scores
        else 0
    )

    output = {

        "student_id": profile.get(
            "student_id"
        ),

        "skill_assessment": assessment,

        "overall_score": overall_score
    }

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


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("SKILL ASSESSMENT")
    print("=" * 60)

    profile = load_profile()

    assessment = build_assessment(
        profile
    )

    save_output(
        profile,
        assessment
    )

    print(
        "\nSkill assessment completed successfully."
    )

    print(
        f"\nSkills assessed: {len(assessment)}"
    )

    print(
        f"\nOutput file:\n{OUTPUT_FILE}"
    )

    print("\nAssessment:")

    for skill, result in assessment.items():

        print(
            f"{skill}: "
            f"{result['level']} "
            f"({result['score']}) "
            f"- "
            f"{', '.join(result['evidence'])}"
        )


if __name__ == "__main__":
    main()