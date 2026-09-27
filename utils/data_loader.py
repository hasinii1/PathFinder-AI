import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "students"

FILES = {
    "profile": DATA_DIR / "profile_output.json",
    "assessment": DATA_DIR / "assessment_output.json",
    "skill_gap": DATA_DIR / "skill_gap_output.json",
    "opportunities": DATA_DIR / "opportunity_results.json",
    "roadmap": DATA_DIR / "roadmap_output.json",
}


def load_json(path):
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def load_data(name):
    return load_json(FILES[name])


def get_profile(): return load_data("profile")
def get_assessment(): return load_data("assessment")
def get_skill_gap(): return load_data("skill_gap")
def get_roadmap(): return load_data("roadmap")


def get_opportunities():
    data = load_data("opportunities")
    return data.get("opportunities", []) if isinstance(data, dict) else data


def display_name(profile):
    p = profile.get("personal_information", {}) if isinstance(profile, dict) else {}
    name = p.get("name") or profile.get("name") or "Student"
    return str(name).title()


def skill_names(items):
    result = []
    for item in items or []:
        if isinstance(item, dict):
            value = item.get("skill", "")
        else:
            value = str(item)
        if value:
            result.append(value)
    return result
