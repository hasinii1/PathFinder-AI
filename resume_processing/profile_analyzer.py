import re
import json
from pathlib import Path

from resume_processing.extract_text import extract_text_from_pdf
from resume_processing.preprocessing import clean_resume_text
from resume_processing.skill_extractor import (
    extract_skills,
    get_skills_by_category,
)


# =========================================================
# BASIC INFORMATION
# =========================================================

def extract_name(text: str) -> str:
    """
    Extract the student's name from the beginning of the resume.

    The first meaningful line is treated as the name unless it is
    a generic resume heading.
    """

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    if not lines:
        return ""

    excluded = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "biodata",
        "curriculum vitae resume",
    }

    for line in lines[:5]:
        cleaned = line.strip(":-• ")

        if not cleaned:
            continue

        if cleaned.lower() in excluded:
            continue

        # Do not treat an email/phone as a name
        if "@" in cleaned:
            continue

        if re.fullmatch(
            r"(?:\+91[-\s]?)?[6-9]\d{9}",
            cleaned.replace(" ", ""),
        ):
            continue

        return cleaned

    return ""


def extract_email(text: str) -> str:
    """Extract email address."""

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract Indian phone number."""

    match = re.search(
        r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)",
        text,
    )

    return match.group(0) if match else ""


# =========================================================
# SECTION EXTRACTION
# =========================================================

def get_lines(text: str) -> list[str]:
    """Convert resume text into clean non-empty lines."""

    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


def find_section(
    lines: list[str],
    headings: list[str],
) -> list[str]:
    """
    Extract content between a section heading and the next
    major resume section.
    """

    normalized_headings = {
        heading.lower().strip()
        for heading in headings
    }

    major_headings = {
        "career objective",
        "objective",
        "career goal",
        "summary",
        "profile",

        "education",
        "academic background",

        "projects",
        "academic projects",
        "personal projects",
        "project",

        "internship",
        "internships",
        "internship experience",
        "experience",
        "work experience",

        "technical skills",
        "skills",
        "technical knowledge",

        "certifications",
        "certificates",

        "interests",
        "areas of interest",
        "professional interests",

        "hackathon",
        "hackathons",

        "achievements",
        "awards",

        "publications",

        "extracurricular activities",
        "activities",

        "languages",
        "languages known",

        "references",
    }

    start_index = None

    for i, line in enumerate(lines):

        cleaned_line = line.lower().strip(" :-•")

        if cleaned_line in normalized_headings:
            start_index = i + 1
            break

    if start_index is None:
        return []

    section_lines = []

    for i in range(start_index, len(lines)):

        current = lines[i].lower().strip(" :-•")

        if current in major_headings:
            break

        section_lines.append(lines[i])

    return section_lines


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_sentence(text: str) -> str:
    """Convert broken multi-line text into clean text."""

    text = re.sub(r"\s+", " ", text)

    return text.strip(" •-:")


# =========================================================
# CAREER GOAL
# =========================================================

def extract_career_goal(text: str) -> str:
    """
    Extract the career objective/summary from the resume.

    IMPORTANT:
    This is NOT the selected target career.
    The target career comes from the user's preference in the UI.
    """

    lines = get_lines(text)

    section = find_section(
        lines,
        [
            "career objective",
            "objective",
            "career goal",
            "summary",
            "profile",
        ],
    )

    if not section:
        return ""

    return clean_sentence(" ".join(section))


# =========================================================
# INTERESTS
# =========================================================

def extract_interests(text: str) -> list[str]:
    """Extract interests."""

    lines = get_lines(text)

    section = find_section(
        lines,
        [
            "interests",
            "areas of interest",
            "professional interests",
        ],
    )

    interests = []

    for line in section:

        line = line.strip("•- ")

        if line:
            interests.append(
                clean_sentence(line)
            )

    return interests


# =========================================================
# PROJECT HELPERS
# =========================================================

def looks_like_project_title(line: str) -> bool:
    """
    Determine whether a line looks like a project title.

    This is intentionally generic and does NOT contain
    student-specific project names.
    """

    cleaned = line.strip("•- ")

    if not cleaned:
        return False

    lower = cleaned.lower()

    # Common description/metadata lines
    description_starters = (
        "developed ",
        "built ",
        "created ",
        "designed ",
        "implemented ",
        "analyzed ",
        "developed an ",
        "developed a ",
        "using ",
        "used ",
        "technologies:",
        "technology:",
        "tech stack:",
        "tools:",
        "role:",
        "description:",
        "responsibilities:",
        "github:",
        "demo:",
        "link:",
    )

    if lower.startswith(description_starters):
        return False

    # URLs are not project titles
    if "http://" in lower or "https://" in lower:
        return False

    # Email/phone are not project titles
    if "@" in cleaned:
        return False

    # Dates alone are not project titles
    if re.fullmatch(
        r"[\w\s,./-]+(?:19|20)\d{2}[\w\s,./-]*",
        cleaned,
    ):
        return False

    # Very long lines are normally descriptions
    if len(cleaned) > 120:
        return False

    # Full sentences usually indicate descriptions
    if cleaned.endswith((".", "?", "!")):
        return False

    # Project headings often contain separators
    if "|" in cleaned or "–" in cleaned or "—" in cleaned:
        return True

    # Short title-like lines
    words = cleaned.split()

    if 1 <= len(words) <= 12:
        return True

    return False


# =========================================================
# PROJECTS
# =========================================================

def extract_projects(text: str) -> list[dict]:
    """
    Extract projects generically from the Projects section.

    No project names are hardcoded.
    """

    lines = get_lines(text)

    section = find_section(
        lines,
        [
            "projects",
            "academic projects",
            "personal projects",
            "project",
        ],
    )

    if not section:
        return []

    projects = []
    current_project = None

    for raw_line in section:

        original = raw_line.strip()

        if not original:
            continue

        clean_line = original.strip("•- ")

        if not clean_line:
            continue

        # -------------------------------------------------
        # Detect a new project heading
        # -------------------------------------------------

        if looks_like_project_title(clean_line):

            if current_project:
                current_project["description"] = [
                    clean_sentence(item)
                    for item in current_project["description"]
                    if clean_sentence(item)
                ]

                projects.append(current_project)

            current_project = {
                "name": clean_sentence(clean_line),
                "description": [],
            }

            continue

        # -------------------------------------------------
        # Description / project details
        # -------------------------------------------------

        if current_project is None:
            # If the section begins with a description and
            # no title was detected, create a generic project.
            current_project = {
                "name": "Project",
                "description": [],
            }

        cleaned_description = clean_sentence(clean_line)

        if cleaned_description:
            current_project["description"].append(
                cleaned_description
            )

    # Add final project
    if current_project:

        current_project["description"] = [
            clean_sentence(item)
            for item in current_project["description"]
            if clean_sentence(item)
        ]

        projects.append(current_project)

    # Remove meaningless empty projects
    projects = [
        project
        for project in projects
        if project.get("name")
    ]

    return projects


# =========================================================
# INTERNSHIPS
# =========================================================

def extract_internships(text: str) -> list[dict]:
    """Extract internship information generically."""

    lines = get_lines(text)

    section = find_section(
        lines,
        [
            "internship",
            "internships",
            "internship experience",
            "experience",
            "work experience",
        ],
    )

    if not section:
        return []

    internship_text = " ".join(section)

    internship = {
        "role": "",
        "organization": "",
        "duration": "",
        "description": [],
    }

    # -----------------------------------------------------
    # ROLE
    # -----------------------------------------------------

    for line in section:

        lower = line.lower()

        if "intern" in lower:

            internship["role"] = clean_sentence(
                line
            )

            break

    # -----------------------------------------------------
    # ORGANIZATION
    # -----------------------------------------------------

    organization_patterns = [
        r"\bat\s+([A-Za-z0-9&.,'() -]{2,80})",
        r"\bwith\s+([A-Za-z0-9&.,'() -]{2,80})",
    ]

    for pattern in organization_patterns:

        match = re.search(
            pattern,
            internship_text,
            flags=re.IGNORECASE,
        )

        if match:

            organization = match.group(1)

            # Keep it reasonably short
            organization = organization.split(
                " May "
            )[0]

            organization = organization.split(
                " June "
            )[0]

            organization = organization.strip(
                " -–—,.:"
            )

            if organization:
                internship["organization"] = (
                    clean_sentence(organization)
                )

                break

    # Fallback: detect common organization-like lines
    if not internship["organization"]:

        for line in section:

            lower = line.lower()

            if (
                "intern" not in lower
                and len(line.split()) <= 8
                and not re.search(
                    r"\b(?:19|20)\d{2}\b",
                    line,
                )
            ):
                internship["organization"] = (
                    clean_sentence(line)
                )

                break

    # -----------------------------------------------------
    # DURATION
    # -----------------------------------------------------

    duration_match = re.search(
        r"\b("
        r"(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{4}"
        r")\s*(?:[-–—]|to)\s*("
        r"(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{4}"
        r")\b",
        internship_text,
        flags=re.IGNORECASE,
    )

    if duration_match:

        internship["duration"] = (
            f"{duration_match.group(1)} - "
            f"{duration_match.group(2)}"
        )

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    description_lines = []

    for line in section:

        cleaned = clean_sentence(line)
        lower_line = cleaned.lower()

        if not cleaned:
            continue

        # Skip role line
        if (
            internship["role"]
            and cleaned == internship["role"]
        ):
            continue

        # Skip obvious duration-only lines
        if re.search(
            r"\b(?:19|20)\d{2}\b",
            cleaned,
        ) and re.search(
            r"(?:[-–—]|to)",
            cleaned,
        ):
            continue

        # Skip organization-only line
        if (
            internship["organization"]
            and cleaned == internship["organization"]
        ):
            continue

        description_lines.append(cleaned)

    if description_lines:

        combined_description = clean_sentence(
            " ".join(description_lines)
        )

        internship["description"] = [
            combined_description
        ]

    if (
        internship["role"]
        or internship["organization"]
        or internship["duration"]
        or internship["description"]
    ):
        return [internship]

    return []


# =========================================================
# CERTIFICATIONS
# =========================================================

def extract_certifications(text: str) -> list[str]:
    """Extract certifications."""

    lines = get_lines(text)

    section = find_section(
        lines,
        [
            "certifications",
            "certificates",
        ],
    )

    certifications = []

    for line in section:

        line = line.strip("•- ")

        if line:

            certifications.append(
                clean_sentence(line)
            )

    return certifications


# =========================================================
# PROFILE ANALYZER
# =========================================================

def analyze_profile(
    resume_text: str,
    student_id: str = "S001",
) -> dict:
    """
    Convert the uploaded resume into a structured profile.

    target_career is deliberately NOT extracted here.
    It is selected by the user in the Streamlit UI.
    """

    cleaned_text = clean_resume_text(
        resume_text
    )

    detected_skills = extract_skills(
        cleaned_text
    )

    categorized_skills = get_skills_by_category(
        detected_skills
    )

    profile = {

        "student_id": student_id,

        "personal_information": {
            "name": extract_name(
                cleaned_text
            ),
            "email": extract_email(
                cleaned_text
            ),
            "phone": extract_phone(
                cleaned_text
            ),
        },

        # Resume's objective/summary
        "career_goal": extract_career_goal(
            cleaned_text
        ),

        # User-selected target career is added later
        "target_career": "",

        "skills": categorized_skills,

        "projects": extract_projects(
            cleaned_text
        ),

        "internships": extract_internships(
            cleaned_text
        ),

        "certifications": extract_certifications(
            cleaned_text
        ),

        "interests": extract_interests(
            cleaned_text
        ),
    }

    return profile


# =========================================================
# SAVE PROFILE
# =========================================================

def save_profile(
    profile: dict,
    output_path: str,
) -> None:
    """Save structured profile as JSON."""

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False,
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    resume_path = (
        Path(__file__).resolve().parent
        / "resume.pdf"
    )

    output_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "students"
        / "profile_output.json"
    )

    print(
        "\n========== PATHFINDER AI =========="
    )

    print(
        "Student Profile Analyzer"
    )

    print(
        "===================================\n"
    )

    raw_text = extract_text_from_pdf(
        str(resume_path)
    )

    profile = analyze_profile(
        raw_text,
        student_id="S001",
    )

    save_profile(
        profile,
        str(output_path),
    )

    print(
        "Profile analysis completed successfully."
    )

    print(
        f"\nProfile saved to:\n{output_path}"
    )

    print(
        "\n========== PROFILE ==========\n"
    )

    print(
        json.dumps(
            profile,
            indent=4,
            ensure_ascii=False,
        )
    )