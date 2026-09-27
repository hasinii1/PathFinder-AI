import csv
import os

def normalize_skill(skill):
    """🔴 CHANGE 5: Normalize skills for accurate comparison."""
    return str(skill).strip().lower()

def extract_skill_name(item):
    if isinstance(item, dict):
        return item.get("skill", "").strip()
    elif isinstance(item, str):
        return item.strip()
    return ""

def simulate_what_if_career(skill_gap_data, target_career, careers_csv_path):
    # 🔴 CHANGE 4: Extract student's skills properly from skill_gap_analysis
    analysis = skill_gap_data.get("skill_gap_analysis", {})

    strong_raw = analysis.get("strong_skills", [])
    developing_raw = analysis.get("developing_skills", [])

    # Student's known skills set
    student_skills_map = {}
    for item in strong_raw + developing_raw:
        s_name = extract_skill_name(item)
        if s_name:
            student_skills_map[normalize_skill(s_name)] = s_name

    required_skills_original = []

    if os.path.exists(careers_csv_path):
        with open(careers_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("career_title", "") or row.get("title", "") or row.get("career", "")
                if title.strip().lower() == target_career.strip().lower():
                    raw_skills = row.get("required_skills", "") or row.get("skills", "")
                    
                    # 🔴 CHANGE 3: Split using "|" instead of ","
                    required_skills_original = [
                        s.strip() for s in raw_skills.split("|") if s.strip()
                    ]
                    break

    if not required_skills_original:
        required_skills_original = ["Python", "Pandas", "NumPy", "Statistics", "Machine Learning"]

    already_have = []
    need_to_learn = []

    # 🔴 CHANGE 5: Compare normalized skills while preserving clean display names
    for req_skill in required_skills_original:
        norm_req = normalize_skill(req_skill)
        if norm_req in student_skills_map:
            already_have.append(student_skills_map[norm_req])
        else:
            need_to_learn.append(req_skill)

    total_req = len(required_skills_original)
    match_percentage = round((len(already_have) / total_req) * 100) if total_req > 0 else 0

    additional_roadmap = []
    for idx, skill in enumerate(need_to_learn, 1):
        additional_roadmap.append({
            "step_number": idx,
            "skill": skill,
            "action": f"Learn foundational concepts and complete assignments in {skill}"
        })

    return {
        "what_if_career": target_career,
        "match_percentage": f"{match_percentage}%",
        "already_have": list(dict.fromkeys(already_have)),
        "need_to_learn": need_to_learn,
        "additional_roadmap": additional_roadmap
    }