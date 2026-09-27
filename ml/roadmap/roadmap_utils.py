import json
import os

# Cleaned relative package imports for package execution
from .roadmap_generator import generate_personalized_roadmap
from .career_simulator import simulate_what_if_career

def run_member_4_pipeline():
    profile_path = "data/students/profile_output.json"
    skill_gap_path = "data/students/skill_gap_output.json"
    careers_csv_path = "data/careers/careers.csv"
    output_path = "data/students/roadmap_output.json"

    # Generate Personalized Roadmap dynamically from Member 2's output
    roadmap_data = generate_personalized_roadmap(profile_path, skill_gap_path)

    # Read gap_data for simulator dynamically
    gap_data = {}
    if os.path.exists(skill_gap_path):
        with open(skill_gap_path, 'r', encoding='utf-8') as f:
            gap_data = json.load(f)

    # Test all requested What-If target careers dynamically
    test_careers = [
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Software Developer"
    ]

    what_if_simulations = {}
    for career in test_careers:
        sim_result = simulate_what_if_career(
            skill_gap_data=gap_data,
            target_career=career,
            careers_csv_path=careers_csv_path
        )
        what_if_simulations[career] = sim_result

    # Combined output structure for Member 5 UI rendering
    final_output = {
        "personalized_roadmap": roadmap_data,
        "what_if_simulation": what_if_simulations.get("Data Scientist", {}),
        "what_if_simulations": what_if_simulations
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)

    print(f"✅ Member 4 successfully generated output file at: {output_path}")

if __name__ == "__main__":
    run_member_4_pipeline()