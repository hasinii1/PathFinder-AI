import json
import os

def load_json_file(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_skill_name(item):
    """Extracts string skill name whether item is a dict or string."""
    if isinstance(item, dict):
        return item.get("skill", "").strip()
    elif isinstance(item, str):
        return item.strip()
    return ""

def generate_personalized_roadmap(profile_path, skill_gap_path):
    profile = load_json_file(profile_path)
    skill_gap = load_json_file(skill_gap_path)

    # 🔴 CHANGE 1: Read skill_gap_analysis object
    analysis = skill_gap.get("skill_gap_analysis", {})

    strong_skills_raw = analysis.get("strong_skills", [])
    developing_skills_raw = analysis.get("developing_skills", [])
    missing_skills_raw = analysis.get("missing_skills", [])

    target_career = analysis.get(
        "target_career",
        skill_gap.get("target_career", profile.get("target_career", "Data Analyst"))
    )

    # 🔴 CHANGE 2: Extract actual skill names safely
    strong_skill_names = [
        extract_skill_name(item) for item in strong_skills_raw if extract_skill_name(item)
    ]
    developing_skill_names = [
        extract_skill_name(item) for item in developing_skills_raw if extract_skill_name(item)
    ]
    missing_skill_names = [
        extract_skill_name(item) for item in missing_skills_raw if extract_skill_name(item)
    ]

    roadmap_steps = []

    # Phase 1: Strengthen Basics (Developing Skills)
    for skill in developing_skill_names:
        roadmap_steps.append({
            "skill": skill,
            "phase": "PHASE 1 — Strengthen Basics",
            "current_status": "Developing",
            "priority": "High",
            "why_needed": f"Strengthen core fundamentals required for {target_career}",
            "learning_goal": f"Achieve functional proficiency in {skill}",
            "recommended_action": f"Complete foundational tutorials and practical exercises in {skill}",
            "estimated_duration": "2 weeks",
            "prerequisites": "None",
            "completion_status": "In Progress"
        })

    # Phase 2: Build Technical Skills (Missing Skills)
    for skill in missing_skill_names:
        roadmap_steps.append({
            "skill": skill,
            "phase": "PHASE 2 — Build Technical Skills",
            "current_status": "Missing",
            "priority": "High",
            "why_needed": f"Core requirement gap for target role: {target_career}",
            "learning_goal": f"Master key concepts and hands-on applications for {skill}",
            "recommended_action": f"Take structured online modules or specialized courses on {skill}",
            "estimated_duration": "3 weeks",
            "prerequisites": "Phase 1 skills",
            "completion_status": "Not Started"
        })

    # Phase 3: Applied Projects
    roadmap_steps.append({
        "skill": "Applied Capstone Project",
        "phase": "PHASE 3 — Projects",
        "current_status": "Missing",
        "priority": "Medium",
        "why_needed": "Demonstrate practical competency to potential recruiters",
        "learning_goal": "Build an end-to-end industry project",
        "recommended_action": f"Build a real-world project utilizing {', '.join(strong_skill_names[:2]) if strong_skill_names else 'core skills'}",
        "estimated_duration": "3 weeks",
        "prerequisites": "Phase 2 technical skills",
        "completion_status": "Not Started"
    })

    # Phase 4: Career Preparation
    roadmap_steps.append({
        "skill": "Career Readiness & Portfolio",
        "phase": "PHASE 4 — Career Preparation",
        "current_status": "Missing",
        "priority": "Medium",
        "why_needed": "Final step to qualify for hiring opportunities",
        "learning_goal": "Prepare job application materials and interview practice",
        "recommended_action": "Optimize resume, host portfolio on GitHub, practice mock interviews",
        "estimated_duration": "2 weeks",
        "prerequisites": "Completed Portfolio Project",
        "completion_status": "Not Started"
    })

    return {
        "target_career": target_career,
        "total_steps": len(roadmap_steps),
        "steps": roadmap_steps
    }