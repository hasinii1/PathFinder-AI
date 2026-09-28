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
# ATS-STYLE RESUME SCORE
# =========================================================

def _contains_any(text: str, terms) -> bool:
    text = str(text or "").lower()
    return any(str(term).lower() in text for term in terms)


def _count_unique_skill_items(skills) -> int:
    """Count unique detected skills without rewarding duplicate categories."""

    values = []

    if isinstance(skills, dict):
        for group in skills.values():
            if isinstance(group, list):
                values.extend(group)
            elif isinstance(group, dict):
                values.extend(group.keys())
    elif isinstance(skills, list):
        values.extend(skills)

    normalized = {
        str(item).strip().lower()
        for item in values
        if str(item).strip()
    }

    return len(normalized)


def _project_quality_score(projects, text: str) -> int:
    """Score projects by evidence quality rather than project count alone."""

    if not isinstance(projects, list) or not projects:
        return 0

    total = 0.0
    action_terms = (
        "developed", "built", "created", "implemented", "designed",
        "analyzed", "trained", "predicted", "deployed", "automated",
        "integrated", "applied", "worked", "gained",
    )
    technology_terms = (
        "python", "java", "c", "c++", "sql", "mysql", "pandas",
        "numpy", "scikit", "streamlit", "tensorflow", "pytorch",
        "react", "html", "css", "javascript", "power bi", "plotly",
        "machine learning", "deep learning", "opencv",
    )
    result_terms = (
        "accuracy", "achieved", "improved", "increased", "reduced",
        "performance", "result", "f1", "precision", "recall", "%",
    )

    for project in projects[:6]:
        if not isinstance(project, dict):
            project = {"title": str(project), "description": []}

        title = str(
            project.get("title")
            or project.get("name")
            or ""
        ).strip()

        descriptions = project.get("description", [])
        if isinstance(descriptions, str):
            descriptions = [descriptions]

        description = " ".join(
            str(item) for item in descriptions if item
        )
        combined = f"{title} {description}".lower()

        # Each real project can contribute up to 10 points.
        project_score = 0.0

        if title and len(title.split()) >= 2:
            project_score += 1.5
        elif title:
            project_score += 1

        if len(description.split()) >= 35:
            project_score += 2.0
        elif len(description.split()) >= 18:
            project_score += 1.5
        elif description:
            project_score += 0.75

        tech_hits = sum(
            1 for term in technology_terms
            if term in combined
        )
        project_score += min(2.5, tech_hits * 0.6)

        action_hits = sum(
            1 for term in action_terms
            if term in combined
        )
        project_score += min(2.0, action_hits * 0.5)

        if _contains_any(combined, result_terms):
            project_score += 1.0

        total += min(10.0, project_score)

    return min(20, int(round(total)))


def _internship_quality_score(internships, text: str) -> int:
    """Score internship evidence by specificity, not simply internship count."""

    if not isinstance(internships, list) or not internships:
        return 0

    action_terms = (
        "developed", "built", "implemented", "created", "designed",
        "analyzed", "tested", "deployed", "automated", "integrated",
        "worked", "applied", "trained",
    )
    technology_terms = (
        "python", "java", "c", "c++", "sql", "mysql", "pandas",
        "numpy", "machine learning", "scikit", "streamlit", "react",
        "html", "css", "javascript", "power bi", "tensorflow",
    )
    result_terms = (
        "achieved", "improved", "increased", "reduced", "accuracy",
        "performance", "result", "%", "impact",
    )

    total = 0.0

    for internship in internships[:5]:
        if not isinstance(internship, dict):
            internship = {"description": [str(internship)]}

        role = str(internship.get("role") or "").strip()
        organization = str(internship.get("organization") or "").strip()
        duration = str(internship.get("duration") or "").strip()
        description = internship.get("description", [])

        if isinstance(description, str):
            description = [description]

        description_text = " ".join(
            str(item) for item in description if item
        )
        combined = (
            f"{role} {organization} {duration} {description_text}"
        ).lower()

        item_score = 0.0

        if role:
            item_score += 1.25
        if organization:
            item_score += 1.25
        if duration:
            item_score += 0.75

        if len(description_text.split()) >= 20:
            item_score += 1.75
        elif description_text:
            item_score += 1.0

        tech_hits = sum(
            1 for term in technology_terms
            if term in combined
        )
        item_score += min(1.75, tech_hits * 0.5)

        action_hits = sum(
            1 for term in action_terms
            if term in combined
        )
        item_score += min(1.5, action_hits * 0.5)

        if _contains_any(combined, result_terms):
            item_score += 0.75

        total += min(7.5, item_score)

    return min(15, int(round(total)))


def _career_keyword_score(
    resume_text: str,
    skills,
    target_career: str = "",
) -> int:
    """Measure meaningful keyword coverage for the selected career."""

    text = str(resume_text or "").lower()
    career = str(target_career or "").strip().lower()

    career_keywords = {
        "data analyst": (
            "python", "sql", "excel", "power bi", "tableau", "pandas",
            "numpy", "statistics", "data visualization", "analytics", "eda",
        ),
        "data scientist": (
            "python", "sql", "pandas", "numpy", "statistics", "machine learning",
            "scikit", "tensorflow", "pytorch", "data analysis", "visualization",
        ),
        "software developer": (
            "java", "python", "c", "c++", "javascript", "html", "css",
            "sql", "data structures", "algorithms", "git", "api",
        ),
        "software engineer": (
            "java", "python", "c", "c++", "javascript", "sql",
            "data structures", "algorithms", "git", "api", "testing",
        ),
        "ai engineer": (
            "python", "machine learning", "deep learning", "tensorflow",
            "pytorch", "scikit", "numpy", "pandas", "nlp", "computer vision",
        ),
        "machine learning engineer": (
            "python", "machine learning", "deep learning", "scikit",
            "tensorflow", "pytorch", "numpy", "pandas", "model", "deployment",
        ),
    }

    keywords = career_keywords.get(career)

    if not keywords:
        # Use meaningful words from the selected career when it is not in
        # the small built-in career vocabulary.
        keywords = tuple(
            word for word in career.split()
            if len(word) >= 4 and word not in {"with", "and", "the", "for"}
        )

    if not keywords:
        return 5

    hits = sum(1 for keyword in keywords if keyword in text)
    coverage = hits / len(keywords)

    # Keep this factor moderate: career mismatch should matter, but it
    # should not overwhelm the actual quality of the resume.
    if coverage >= 0.75:
        return 10
    if coverage >= 0.55:
        return 8
    if coverage >= 0.35:
        return 6
    if coverage >= 0.20:
        return 4
    if coverage > 0:
        return 2
    return 0


def calculate_ats_evaluation(
    resume_text: str,
    personal_information: dict,
    skills: dict,
    projects: list,
    internships: list,
    certifications: list,
    career_goal: str = "",
    target_career: str = "",
) -> dict:
    """
    Calculate PathFinder's transparent ATS-style resume evaluation.

    This is NOT a commercial ATS score. It evaluates the quality and
    evidence present in the uploaded resume. Section presence alone is
    deliberately given limited weight.
    """

    text = str(resume_text or "")
    lower = text.lower()
    personal_information = personal_information or {}

    breakdown = {}

    # ---------------------------------------------------------
    # 1. Contact Information - 5 points
    # ---------------------------------------------------------
    contact = 0
    if personal_information.get("name"):
        contact += 1
    if personal_information.get("email"):
        contact += 1
    if personal_information.get("phone"):
        contact += 1
    if "linkedin.com" in lower or "linkedin:" in lower:
        contact += 1
    if "github.com" in lower or "github:" in lower or "portfolio" in lower:
        contact += 1
    breakdown["Contact Information"] = contact

    # ---------------------------------------------------------
    # 2. Career Objective / Summary - 5 points
    # ---------------------------------------------------------
    objective = str(career_goal or "").strip()
    if not objective:
        objective_section_terms = (
            "career objective", "objective", "summary", "profile"
        )
        if _contains_any(lower, objective_section_terms):
            objective = lower

    objective_score = 0
    if objective:
        objective_score += 2
        word_count = len(objective.split())
        if 25 <= word_count <= 90:
            objective_score += 1
        if target_career and target_career.lower() in objective.lower():
            objective_score += 2
        elif _contains_any(
            objective.lower(),
            ("software", "programming", "developer", "data", "analytics", "machine learning", "ai"),
        ):
            objective_score += 1
    breakdown["Career Objective / Summary"] = min(5, objective_score)

    # ---------------------------------------------------------
    # 3. Education - 10 points
    # ---------------------------------------------------------
    education_score = 0
    if _contains_any(lower, ("education", "academic")):
        education_score += 1
    if _contains_any(lower, ("b.tech", "btech", "b.e", "bachelor", "degree", "m.tech", "mtech")):
        education_score += 2
    if _contains_any(lower, ("university", "college", "institute")):
        education_score += 2
    if re.search(r"(?:cgpa|gpa|percentage|%|/\s*\d{3,4})", lower):
        education_score += 2
    if re.search(r"\b(?:19|20)\d{2}\b", lower):
        education_score += 1
    if _contains_any(lower, ("computer science", "engineering", "information technology")):
        education_score += 1
    breakdown["Education"] = min(10, education_score)

    # ---------------------------------------------------------
    # 4. Technical Skills - 15 points
    # ---------------------------------------------------------
    skill_count = _count_unique_skill_items(skills)
    skill_score = 0

    if skill_count >= 12:
        skill_score += 6
    elif skill_count >= 8:
        skill_score += 5
    elif skill_count >= 5:
        skill_score += 4
    elif skill_count >= 3:
        skill_score += 3
    elif skill_count >= 1:
        skill_score += 2

    if _contains_any(lower, ("programming", "technical skills", "tools", "web", "database", "core cs")):
        skill_score += 2

    specific_terms = (
        "python", "java", "sql", "mysql", "pandas", "numpy", "scikit-learn",
        "scikit", "streamlit", "power bi", "tableau", "tensorflow", "pytorch",
        "javascript", "html", "css", "git", "opencv",
    )
    specific_hits = sum(1 for term in specific_terms if term in lower)
    skill_score += min(4, specific_hits // 2)

    if target_career:
        skill_score += min(
            3,
            _career_keyword_score(lower, skills, target_career) // 3,
        )

    breakdown["Technical Skills"] = min(15, skill_score)

    # ---------------------------------------------------------
    # 5. Projects - 20 points
    # ---------------------------------------------------------
    breakdown["Projects"] = _project_quality_score(projects, lower)

    # ---------------------------------------------------------
    # 6. Internships / Experience - 15 points
    # ---------------------------------------------------------
    breakdown["Internships / Experience"] = _internship_quality_score(
        internships,
        lower,
    )

    # ---------------------------------------------------------
    # 7. Certifications - 5 points
    # ---------------------------------------------------------
    certification_count = (
        len(certifications) if isinstance(certifications, list) else 0
    )
    certification_score = 0
    if certification_count:
        certification_score += 1
        named = 0
        provider_terms = (
            "infosys", "ibm", "microsoft", "coursera", "udemy", "nptel",
            "aws", "google", "oracle", "simplilearn", "skillsbuild",
        )
        for cert in certifications:
            cert_text = str(cert).lower()
            if len(cert_text.split()) >= 2:
                named += 1
            if any(provider in cert_text for provider in provider_terms):
                certification_score += 1
        if named >= 2:
            certification_score += 1
        if re.search(r"\b(?:20)\d{2}\b", lower):
            certification_score += 1
    breakdown["Certifications"] = min(5, certification_score)

    # ---------------------------------------------------------
    # 8. Achievements / Activities - 5 points
    # ---------------------------------------------------------
    achievement_score = 0
    achievement_terms = (
        "achievements", "activities", "hackathon", "award", "competition",
        "rank", "winner", "finalist", "certificate", "presentation",
    )
    if _contains_any(lower, achievement_terms):
        achievement_score += 1

    concrete_terms = (
        "won", "selected", "ranked", "finalist", "top", "award", "secured",
        "published", "presented", "participated",
    )
    concrete_hits = sum(1 for term in concrete_terms if term in lower)
    achievement_score += min(2, concrete_hits)

    if _contains_any(lower, ("lead", "team", "organized", "volunteered")):
        achievement_score += 1

    if _contains_any(lower, ("sih", "smart india hackathon", "hackathon")):
        achievement_score += 1

    breakdown["Achievements / Activities"] = min(5, achievement_score)

    # ---------------------------------------------------------
    # 9. Target Career Keyword Relevance - 10 points
    # ---------------------------------------------------------
    breakdown["Target Career Keyword Relevance"] = _career_keyword_score(
        lower,
        skills,
        target_career,
    )

    # ---------------------------------------------------------
    # 10. ATS Structure / Parseability - 10 points
    # ---------------------------------------------------------
    structure_score = 0
    headings = (
        "education", "technical skills", "skills", "projects",
        "internships", "experience", "certifications", "objective",
        "summary", "achievements", "activities",
    )
    heading_hits = sum(1 for heading in headings if heading in lower)

    if heading_hits >= 6:
        structure_score += 4
    elif heading_hits >= 4:
        structure_score += 3
    elif heading_hits >= 2:
        structure_score += 2
    elif heading_hits >= 1:
        structure_score += 1

    word_count = len(text.split())
    if 250 <= word_count <= 900:
        structure_score += 2
    elif 120 <= word_count < 250:
        structure_score += 1

    if len(text.strip()) >= 100:
        structure_score += 2

    # Penalize obvious extraction noise / repeated text.
    lines = [line.strip().lower() for line in text.splitlines() if line.strip()]
    unique_ratio = (
        len(set(lines)) / len(lines)
        if lines
        else 0
    )
    if unique_ratio >= 0.85:
        structure_score += 2
    elif unique_ratio >= 0.65:
        structure_score += 1

    breakdown["ATS Structure / Parseability"] = min(10, structure_score)

    total = sum(breakdown.values())

    return {
        "total": max(0, min(100, int(round(total)))),
        "breakdown": breakdown,
        "description": (
            "Quality-based estimate using resume evidence, content strength, "
            "career relevance and ATS structure. This is not a commercial ATS score."
        ),
    }


def calculate_ats_score(
    resume_text: str,
    personal_information: dict,
    skills: dict,
    projects: list,
    internships: list,
    certifications: list,
) -> int:
    """Backward-compatible numeric ATS score helper."""

    evaluation = calculate_ats_evaluation(
        resume_text,
        personal_information,
        skills,
        projects,
        internships,
        certifications,
    )
    return int(evaluation["total"])


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

    ats_score = calculate_ats_score(
        cleaned_text,
        {
            "name": extract_name(cleaned_text),
            "email": extract_email(cleaned_text),
            "phone": extract_phone(cleaned_text),
        },
        categorized_skills,
        extract_projects(cleaned_text),
        extract_internships(cleaned_text),
        extract_certifications(cleaned_text),
    )

    profile = {

        "student_id": student_id,

        "ats_score": ats_score,

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