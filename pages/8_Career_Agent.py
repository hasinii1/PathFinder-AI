import streamlit as st

from components.styles import apply_styles
from agents.career_navigator import run_career_agent


# =============================================================
# PAGE CONFIG
# =============================================================

st.set_page_config(
    page_title="Career Navigator | PathFinder AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


# =============================================================
# CALLBACKS
# =============================================================

def set_suggested_question(question):
    st.session_state["career_agent_question"] = question


def clear_career_question():
    st.session_state["career_agent_question"] = ""
    st.session_state.pop("career_agent_response", None)


# =============================================================
# HEADER
# =============================================================

st.html(
    """
    <div class="hero">
        <div class="hero-label">
            AI-POWERED CAREER GUIDANCE
        </div>

        <h1>
            Career Navigator 🤖
        </h1>

        <p>
            Ask PathFinder's AI career agent about your skills,
            career goals, skill gaps, opportunities and roadmap.
        </p>
    </div>
    """
)


# =============================================================
# INTRODUCTION
# =============================================================

st.html(
    """
    <div class="welcome-banner">
        <h2>
            Your Personal AI Career Guide
        </h2>

        <p>
            Career Navigator uses your existing PathFinder profile,
            skill assessment, skill gaps, opportunities and roadmap
            to provide personalized career guidance.
        </p>
    </div>
    """
)


# =============================================================
# CHECK PROFILE
# =============================================================

profile_processed = st.session_state.get(
    "resume_processed",
    False,
)

if not profile_processed:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                🤖
            </div>

            <h2>
                Complete Your Profile First
            </h2>

            <p>
                Please upload and analyze your resume before using
                Career Navigator. This allows the AI agent to
                understand your skills, goals and career direction.
            </p>

        </div>
        """
    )

    st.page_link(
        "pages/1_Profile.py",
        label="📄 Go to Profile Analysis",
        use_container_width=True,
    )

    st.stop()


# =============================================================
# SUGGESTED QUESTIONS
# =============================================================

st.html(
    """
    <div class="section-title">
        Ask Your Career Question
    </div>

    <div style="
        color:#756D63;
        font-size:12px;
        margin-top:-8px;
        margin-bottom:12px;
    ">
        Ask about your skills, career path, opportunities,
        skill gaps or personalized roadmap.
    </div>
    """
)


suggested_questions = [
    "What skills should I improve for my target career?",
    "What are my biggest skill gaps?",
    "What opportunities are suitable for me?",
    "What should I learn next?",
    "Am I ready for my target career?",
    "How can I improve my career readiness?",
]


# =============================================================
# QUESTION INPUT
# =============================================================

question = st.text_area(
    "Career Question",
    placeholder=(
        "Example: What skills should I improve to become "
        "a Data Scientist?"
    ),
    height=110,
    key="career_agent_question",
)


# =============================================================
# SUGGESTED QUESTION BUTTONS
# =============================================================

st.html(
    """
    <div style="
        color:#756D63;
        font-size:12px;
        font-weight:700;
        margin-top:4px;
        margin-bottom:8px;
    ">
        Suggested questions
    </div>
    """
)

question_columns = st.columns(3)

for index, suggested_question in enumerate(suggested_questions):

    with question_columns[index % 3]:

        st.button(
            suggested_question,
            key=f"suggested_question_{index}",
            use_container_width=True,
            on_click=set_suggested_question,
            args=(suggested_question,),
        )


# =============================================================
# ASK AGENT
# =============================================================

st.html('<div style="height:8px;"></div>')

ask_col, clear_col = st.columns([3, 1])

with ask_col:

    ask_agent = st.button(
        "🤖 Ask Career Navigator",
        type="primary",
        use_container_width=True,
    )

with clear_col:

    clear_question = st.button(
        "Clear",
        use_container_width=True,
        on_click=clear_career_question,
    )


# =============================================================
# RUN CAREER AGENT
# =============================================================

if ask_agent:

    current_question = st.session_state.get(
        "career_agent_question",
        "",
    ).strip()

    if not current_question:

        st.warning(
            "Please enter a career question first."
        )

    else:

        with st.spinner(
            "Career Navigator is analyzing your profile..."
        ):

            response = run_career_agent(
                current_question
            )

        st.session_state["career_agent_response"] = response


# =============================================================
# DISPLAY AGENT RESPONSE
# =============================================================

agent_response = st.session_state.get(
    "career_agent_response"
)

if agent_response:

    st.html(
        """
        <div class="section-title">
            Career Navigator Response
        </div>
        """
    )

    st.markdown(
        agent_response
    )


# =============================================================
# HOW IT WORKS
# =============================================================

st.html(
    """
    <div style="height:18px;"></div>

    <div class="section-title">
        How Career Navigator Works
    </div>

    <div class="card">

        <div style="
            color:#3B342E;
            font-size:14px;
            font-weight:800;
            margin-bottom:10px;
        ">
            Your question → AI Agent → PathFinder data → Personalized guidance
        </div>

        <div style="
            color:#756D63;
            font-size:12px;
            line-height:1.7;
        ">
            The Career Navigator can use your analyzed profile,
            skill assessment, skill gaps, relevant opportunities
            and personalized roadmap. The LLM connects this
            information to understand your question and provide
            a personalized response.
        </div>

    </div>
    """
)


# =============================================================
# FOOTER
# =============================================================

st.html(
    """
    <div style="
        text-align:center;
        padding:35px 0 10px;
        color:#7A7067;
        font-size:12px;
    ">
        PathFinder AI
        ·
        Career Navigator
    </div>
    """
)