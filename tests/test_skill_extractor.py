from resume_processing.extract_text import extract_text_from_pdf
from resume_processing.preprocessing import clean_resume_text
from resume_processing.skill_extractor import extract_skills, get_skills_by_category


# Step 1: Extract text from resume
raw_text = extract_text_from_pdf(
    "resume_processing/resume.pdf"
)

# Step 2: Clean the extracted text
cleaned_text = clean_resume_text(raw_text)

# Step 3: Extract skills
skills = extract_skills(cleaned_text)

# Step 4: Display detected skills
print("\n========== DETECTED SKILLS ==========\n")

for item in skills:
    print(f"- {item['skill']} ({item['category']})")


# Step 5: Display skills grouped by category
categorized_skills = get_skills_by_category(skills)

print("\n========== SKILLS BY CATEGORY ==========\n")

for category, category_skills in categorized_skills.items():
    print(f"{category}:")
    
    for skill in category_skills:
        print(f"  - {skill}")

    print()