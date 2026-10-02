import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .agent_tools import (
    get_student_profile,
    get_skill_assessment,
    get_skill_gaps,
    get_relevant_opportunities,
    get_roadmap,
    get_opportunity_summary,
)


# ============================================================
# PATHFINDER AI - LLM CAREER NAVIGATOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured.\n"
        "Please add GEMINI_API_KEY to F:\\pathfinder\\.env"
    )


client = genai.Client(api_key=API_KEY)

# Gemini 3.5 Flash is currently responding successfully
MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are Career Navigator, an LLM-powered career guidance
agent inside PathFinder AI.

PathFinder AI is a Student Growth and Opportunity Navigator.

Your job is to understand a student's request and use the
available PathFinder tools to provide useful and personalized
career guidance.

AVAILABLE TOOLS:

1. Student Profile
2. Skill Assessment
3. Skill Gap Detection
4. Relevant Opportunity Matching
5. Personalized Roadmap
6. Opportunity Database Summary

IMPORTANT RULES:

- Use PathFinder data as the primary source.
- Never invent student information.
- Never invent skills, projects, education, certifications,
  internships or achievements.
- If information is unavailable, clearly say so.
- Recommendations should be based on the student's available
  profile and career goal.
- Do not claim that PathFinder trained an ML model unless the
  available data explicitly confirms it.
- The current PathFinder implementation uses automated text
  processing, skill extraction, rule-based analysis and
  weighted matching.
- The LLM is used for natural-language reasoning, synthesis,
  interaction and personalized guidance.
- Do not expose API keys.
- Do not expose private implementation details.
- Do not request or return the entire opportunity database.
- Use the relevant opportunity tool when opportunity information
  is needed.
- Give practical and understandable recommendations.

When answering a career question:

1. Understand the student's goal.
2. Retrieve relevant student information.
3. Analyze their current skills.
4. Identify relevant gaps.
5. Consider relevant opportunities when appropriate.
6. Connect the answer to the roadmap.
7. Give clear next steps.

Do not call every tool unnecessarily.

If the question is specifically about skills, prioritize:
- Student Profile
- Skill Assessment
- Skill Gaps
- Roadmap

If the question is about jobs or internships, prioritize:
- Student Profile
- Skill Gaps
- Relevant Opportunities

If the question is about the student's overall career path,
use the relevant combination of tools.

Keep answers structured, professional and easy for a student
to understand.
"""


# ============================================================
# TOOL WRAPPERS
# ============================================================

def student_profile_tool():
    """
    Get the student's analyzed profile including education,
    skills, projects, career goal and other extracted profile
    information.
    """
    return get_student_profile()


def skill_assessment_tool():
    """
    Get the student's current skill assessment, including
    assessed skills and their current skill levels.
    """
    return get_skill_assessment()


def skill_gap_tool():
    """
    Get the student's detected skill gaps for the target career.
    """
    return get_skill_gaps()


def relevant_opportunities_tool(limit: int = 5):
    """
    Get the highest-ranked relevant opportunities from the
    existing PathFinder opportunity matching results.

    The complete opportunity database is not returned.
    The maximum number of opportunities is limited to 8.
    """

    try:
        limit = int(limit)
    except Exception:
        limit = 5

    limit = max(1, min(limit, 8))

    return get_relevant_opportunities(limit=limit)


def roadmap_tool():
    """
    Get the student's personalized learning and development
    roadmap.
    """
    return get_roadmap()


def opportunity_summary_tool():
    """
    Get a compact summary of the live opportunity database,
    including total opportunities and company-level information.
    """
    return get_opportunity_summary()


# ============================================================
# TOOL LIST
# ============================================================

AGENT_TOOLS = [
    student_profile_tool,
    skill_assessment_tool,
    skill_gap_tool,
    relevant_opportunities_tool,
    roadmap_tool,
    opportunity_summary_tool,
]


# ============================================================
# RESPONSE CLEANING
# ============================================================

def clean_response(response):
    """
    Safely extracts text from the Gemini response.
    """

    if response is None:
        return ""

    try:
        text = response.text

        if text:
            return text.strip()

    except Exception:
        pass

    return ""


# ============================================================
# ERROR HANDLING
# ============================================================

def format_gemini_error(error):
    """
    Converts Gemini API errors into understandable messages.
    """

    error_text = str(error)
    upper_error = error_text.upper()

    if "503" in error_text or "UNAVAILABLE" in upper_error:
        return (
            "Gemini is temporarily unavailable because the "
            "model is experiencing high demand.\n\n"
            "Please try again after a short while."
        )

    if "429" in error_text or "RESOURCE_EXHAUSTED" in upper_error:
        return (
            "The Gemini API request limit has been reached "
            "temporarily.\n\n"
            "Please wait and try again later."
        )

    if "401" in error_text or "UNAUTHENTICATED" in upper_error:
        return (
            "Gemini authentication failed.\n\n"
            "Please check the GEMINI_API_KEY in the .env file."
        )

    if "403" in error_text or "PERMISSION_DENIED" in upper_error:
        return (
            "Gemini access was denied.\n\n"
            "Please verify that the API key has permission to "
            "use the configured Gemini model."
        )

    if "404" in error_text or "NOT_FOUND" in upper_error:
        return (
            "The configured Gemini model could not be found.\n\n"
            f"Current model: {MODEL_NAME}"
        )

    return (
        "Career Navigator encountered an unexpected Gemini error.\n\n"
        f"Details: {error_text}"
    )


# ============================================================
# CREATE CAREER NAVIGATOR CHAT
# ============================================================

def create_career_chat():
    """
    Creates a Gemini chat session with the PathFinder tools.

    Chat.send_message() is used because the Gemini SDK recommends
    it for automatic function calling.
    """

    return client.chats.create(
        model=MODEL_NAME,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.3,
            "tools": AGENT_TOOLS,
        },
    )


# ============================================================
# RUN CAREER AGENT
# ============================================================

def run_career_agent(user_request):
    """
    Sends a student's question to the LLM Career Navigator.

    Gemini can decide which PathFinder tools are needed and
    automatically use them before producing the final answer.
    """

    if not user_request or not user_request.strip():
        return "Please enter a career goal or question."

    try:

        # Create a new chat for this request
        chat = create_career_chat()

        # Send the student's request
        response = chat.send_message(
            user_request.strip()
        )

        # Extract final response
        result = clean_response(response)

        if result:
            return result

        return (
            "Career Navigator did not return a text response.\n\n"
            "Please try your question again."
        )

    except Exception as error:
        return format_gemini_error(error)


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PATHFINDER AI - CAREER NAVIGATOR")
    print("=" * 60)

    print("\nGemini model:", MODEL_NAME)

    print("\nAvailable Career Navigator tools:")
    print("1. Student Profile")
    print("2. Skill Assessment")
    print("3. Skill Gap Detection")
    print("4. Relevant Opportunities")
    print("5. Personalized Roadmap")
    print("6. Opportunity Summary")

    print("\n" + "-" * 60)

    question = input(
        "Enter a career goal or question: "
    ).strip()

    print("\nProcessing your request...")

    result = run_career_agent(question)

    print("\n" + "=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)

    print(result)

    print("\n" + "=" * 60)