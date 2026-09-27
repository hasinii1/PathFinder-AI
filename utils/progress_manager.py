import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    ROOT
    / "data"
    / "students"
)


# ============================================================
# DEFAULT STRUCTURE
# ============================================================

def empty_progress():
    return {
        "steps": {},
        "skills": {},
        "projects": {},
        "goals": {},
    }


# ============================================================
# SAFE USER KEY
# ============================================================

def _safe_key(user_key="default"):
    value = str(
        user_key or "default"
    ).strip()

    if not value:
        value = "default"

    return re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        value,
    )[:80]


# ============================================================
# FILE PATH
# ============================================================

def _path(user_key="default"):
    return (
        DATA_DIR
        / f"progress_{_safe_key(user_key)}.json"
    )


# ============================================================
# LOAD PROGRESS
# ============================================================

def get_progress(user_key="default"):
    path = _path(user_key)

    if not path.exists():
        return empty_progress()

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):
            return empty_progress()

        default = empty_progress()

        for category in default:
            if not isinstance(
                data.get(category),
                dict,
            ):
                data[category] = {}

        return data

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
    ):
        return empty_progress()


# ============================================================
# SAVE PROGRESS
# ============================================================

def save_progress(
    data,
    user_key="default",
):
    path = _path(user_key)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not isinstance(data, dict):
        data = empty_progress()

    path.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return data


# ============================================================
# UPDATE ANY CATEGORY
# ============================================================

def update_progress(
    category,
    item,
    value,
    user_key="default",
):
    data = get_progress(
        user_key
    )

    if category not in data:
        data[category] = {}

    try:
        numeric_value = int(value)
    except (
        ValueError,
        TypeError,
    ):
        numeric_value = 0

    numeric_value = max(
        0,
        min(
            100,
            numeric_value,
        ),
    )

    data[category][str(item)] = (
        numeric_value
    )

    save_progress(
        data,
        user_key,
    )

    return data


# ============================================================
# ROADMAP STEP KEY
# ============================================================

def step_key(index, step):
    """
    Creates a stable identifier for a roadmap step.

    Example:
        0:Python
        1:Machine Learning
        2:Applied Capstone Project
    """

    skill = ""

    if isinstance(step, dict):
        skill = (
            step.get("skill")
            or step.get("title")
            or step.get("name")
            or f"Step {index + 1}"
        )

    else:
        skill = str(step)

    skill = str(skill).strip()

    if not skill:
        skill = f"Step {index + 1}"

    return (
        f"{index}:{skill}"
    )


# ============================================================
# GET ROADMAP STEP PROGRESS
# ============================================================

def get_step_progress(
    index,
    step,
    user_key="default",
):
    data = get_progress(
        user_key
    )

    key = step_key(
        index,
        step,
    )

    value = data.get(
        "steps",
        {},
    ).get(
        key,
        0,
    )

    try:
        return max(
            0,
            min(
                100,
                int(value),
            ),
        )
    except (
        ValueError,
        TypeError,
    ):
        return 0


# ============================================================
# UPDATE ROADMAP STEP
# ============================================================

def update_step_progress(
    index,
    step,
    value,
    user_key="default",
):
    data = get_progress(
        user_key
    )

    if "steps" not in data:
        data["steps"] = {}

    key = step_key(
        index,
        step,
    )

    try:
        numeric_value = int(value)
    except (
        ValueError,
        TypeError,
    ):
        numeric_value = 0

    numeric_value = max(
        0,
        min(
            100,
            numeric_value,
        ),
    )

    data["steps"][key] = (
        numeric_value
    )

    # Also keep skill/project
    # summaries for compatibility.
    skill = ""

    if isinstance(step, dict):
        skill = (
            step.get("skill")
            or step.get("title")
            or ""
        )

    if skill:
        data.setdefault(
            "skills",
            {},
        )[str(skill)] = (
            numeric_value
        )

    save_progress(
        data,
        user_key,
    )

    return data


# ============================================================
# RESET STUDENT PROGRESS
# ============================================================

def clear_progress(user_key="default"):
    path = _path(user_key)

    try:
        if path.exists():
            path.unlink()

    except OSError:
        pass

    return empty_progress()


# ============================================================
# CHECK OVERALL ROADMAP PROGRESS
# ============================================================

def calculate_step_progress(
    steps,
    user_key="default",
):
    if not steps:
        return 0

    values = []

    for index, step in enumerate(
        steps
    ):
        values.append(
            get_step_progress(
                index,
                step,
                user_key,
            )
        )

    if not values:
        return 0

    return round(
        sum(values)
        / len(values)
    )


# ============================================================
# PROJECT PROGRESS
# ============================================================

def update_project_progress(
    project_name,
    value,
    user_key="default",
):
    return update_progress(
        "projects",
        project_name,
        value,
        user_key,
    )


def get_project_progress(
    project_name,
    user_key="default",
):
    data = get_progress(
        user_key
    )

    value = data.get(
        "projects",
        {},
    ).get(
        project_name,
        0,
    )

    try:
        return max(
            0,
            min(
                100,
                int(value),
            ),
        )
    except (
        ValueError,
        TypeError,
    ):
        return 0