import html

import streamlit as st

from components.styles import apply_styles
from utils.data_loader import (
    get_profile,
    get_skill_gap,
    get_assessment,
    get_opportunities,
    get_roadmap,
    display_name,
    skill_names,
)


# =============================================================
# PAGE CONFIG
# =============================================================

st.set_page_config(
    page_title="PathFinder AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


# =============================================================
# SMALL HELPERS
# =============================================================

def safe_text(value):
    """Safely display profile-derived text inside HTML."""
    return html.escape(str(value or ""))


def get_next_step(missing_skills, developing_skills, steps):
    """
    Decide what the student should focus on next.

    Priority:
    1. Missing career skill
    2. Developing skill
    3. First pending roadmap step
    4. General roadmap action
    """

    if missing_skills:
        return (
            "Build a missing career skill",
            str(missing_skills[0]).title(),
            "This skill was identified as a gap for your target career.",
            "pages/3_Skill_Gap.py",
            "🧩 View Skill Gaps",
        )

    if developing_skills:
        return (
            "Strengthen a developing skill",
            str(developing_skills[0]).title(),
            "Practice this skill further to improve your career readiness.",
            "pages/2_Skill_Assessment.py",
            "📊 View Skill Assessment",
        )

    for step in steps:
        if not isinstance(step, dict):
            continue

        status = str(
            step.get(
                "completion_status",
                step.get("status", ""),
            )
        ).lower().strip()

        if status not in {"completed", "complete", "done"}:
            title = (
                step.get("title")
                or step.get("step")
                or step.get("skill")
                or "Next roadmap step"
            )

            return (
                "Continue your roadmap",
                str(title),
                "Your personalized roadmap has a next step ready for you.",
                "pages/5_Roadmap.py",
                "🗺️ Open Roadmap",
            )

    return (
        "Explore your opportunities",
        "Find roles that match your profile",
        "Review matched opportunities and identify roles to apply for.",
        "pages/4_Opportunities.py",
        "🎯 View Opportunities",
    )


# =============================================================
# HOME / DASHBOARD
# =============================================================

def home():

    profile_processed = st.session_state.get(
        "resume_processed",
        False,
    )

    # =========================================================
    # EMPTY STATE
    # =========================================================

    if not profile_processed:

        st.html(
            """
            <div class="hero">

                <div class="hero-label">
                    AI-POWERED STUDENT GROWTH &
                    OPPORTUNITY NAVIGATOR
                </div>

                <h1>
                    Your journey starts here ✨
                </h1>

                <p>
                    Upload your resume and let PathFinder
                    understand your skills, goals and
                    career direction.
                </p>

            </div>
            """
        )

        st.html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🧭
                </div>

                <h2>
                    Welcome to PathFinder AI
                </h2>

                <p>
                    Your Skills. Your Goals. Your Guidance.
                    <br><br>
                    Start by uploading your resume.
                    PathFinder will analyze your profile,
                    identify skill gaps, find relevant
                    opportunities and create your
                    personalized roadmap.
                </p>

            </div>
            """
        )

        st.page_link(
            "pages/1_Profile.py",
            label="📄 Upload Your Resume",
            use_container_width=True,
        )

        st.html(
            """
            <div style="
                text-align:center;
                margin-top:15px;
                color:#7A7067;
                font-size:12px;
            ">
                PDF or DOCX · Start building your
                personalized career journey
            </div>
            """
        )

        return

    # =========================================================
    # LOAD ACTUAL PROFILE DATA
    # =========================================================

    profile = get_profile()
    skill_gap = get_skill_gap()
    assessment = get_assessment()
    opportunities = get_opportunities()
    roadmap = get_roadmap()

    personal = profile.get(
        "personal_information",
        {},
    )

    name = display_name(profile)

    has_profile = bool(
        personal.get("name")
        or name
    )

    # =========================================================
    # SAFETY CHECK
    # =========================================================

    if not has_profile:

        st.html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🧭
                </div>

                <h2>
                    Complete Your Profile
                </h2>

                <p>
                    Please upload and analyze your resume
                    before viewing your personalized dashboard.
                </p>

            </div>
            """
        )

        st.page_link(
            "pages/1_Profile.py",
            label="📄 Go to Profile Analysis",
            use_container_width=True,
        )

        return

    # =========================================================
    # TARGET CAREER
    # =========================================================

    target_career = (
        profile.get("target_career")
        or "Career Goal Not Set"
    )

    safe_target_career = safe_text(target_career)

    # =========================================================
    # SKILL GAP DATA
    # =========================================================

    gap_analysis = skill_gap.get(
        "skill_gap_analysis",
        {},
    )

    strong_skills = skill_names(
        gap_analysis.get(
            "strong_skills",
            [],
        )
    )

    developing_skills = skill_names(
        gap_analysis.get(
            "developing_skills",
            [],
        )
    )

    missing_skills = skill_names(
        gap_analysis.get(
            "missing_skills",
            [],
        )
    )

    # =========================================================
    # ASSESSMENT / READINESS
    # =========================================================

    assessment_score = assessment.get(
        "overall_score"
    )

    if assessment_score is None:

        assessment_score = assessment.get(
            "career_readiness",
            0,
        )

    if isinstance(
        assessment_score,
        (int, float),
    ):

        readiness = f"{assessment_score:.0f}%"

    else:

        readiness = str(
            assessment_score or "—"
        )

    # =========================================================
    # ROADMAP DATA
    # =========================================================

    roadmap_data = roadmap.get(
        "personalized_roadmap",
        roadmap,
    )

    if isinstance(
        roadmap_data,
        dict,
    ):

        steps = roadmap_data.get(
            "steps",
            [],
        )

    else:

        steps = []

    if not isinstance(
        steps,
        list,
    ):

        steps = []

    # =========================================================
    # ROADMAP COMPLETION
    # =========================================================

    completed_steps = 0

    for step in steps:

        if not isinstance(
            step,
            dict,
        ):
            continue

        status = str(
            step.get(
                "completion_status",
                step.get(
                    "status",
                    "",
                ),
            )
        ).lower().strip()

        if status in {
            "completed",
            "complete",
            "done",
        }:

            completed_steps += 1

    if steps:

        roadmap_progress = (
            f"{round((completed_steps / len(steps)) * 100)}%"
        )

    else:

        roadmap_progress = "0%"

    # =========================================================
    # FIRST NAME
    # =========================================================

    if name:

        first_name = str(name).split()[0]

    else:

        first_name = "Student"

    safe_first_name = safe_text(first_name)

    # =========================================================
    # HERO
    # =========================================================

    st.html(
        f"""
        <div class="hero">

            <div class="hero-label">
                AI-POWERED STUDENT GROWTH &
                OPPORTUNITY NAVIGATOR
            </div>

            <h1>
                Welcome back, {safe_first_name} 👋
            </h1>

            <p>
                Your skills, goals and opportunities —
                connected in one personalized journey.
            </p>

        </div>
        """
    )

    # =========================================================
    # WELCOME BANNER
    # =========================================================

    st.html(
        f"""
        <div class="welcome-banner">

            <h2>
                Your PathFinder Journey
            </h2>

            <p>
                Target career:
                <b>{safe_target_career}</b>
                &nbsp;·&nbsp;
                Analyze your profile, close skill gaps,
                discover opportunities and follow your
                personalized roadmap.
            </p>

        </div>
        """
    )

    # =========================================================
    # TOP METRICS
    # =========================================================

    col1, col2, col3, col4 = st.columns(4)

    # Target career
    with col1:

        st.html(
            f"""
            <div class="metric">

                <div class="label">
                    Target Career
                </div>

                <div class="value"
                     style="font-size:19px;">
                    {safe_target_career}
                </div>

                <div class="hint">
                    Your selected career goal
                </div>

            </div>
            """
        )

    # Career readiness
    with col2:

        st.html(
            f"""
            <div class="metric">

                <div class="label">
                    Career Readiness
                </div>

                <div class="value">
                    {safe_text(readiness)}
                </div>

                <div class="hint">
                    Based on current assessment
                </div>

            </div>
            """
        )

    # Opportunities
    with col3:

        st.html(
            f"""
            <div class="metric">

                <div class="label">
                    Opportunities
                </div>

                <div class="value">
                    {len(opportunities)}
                </div>

                <div class="hint">
                    Matched opportunities
                </div>

            </div>
            """
        )

    # Roadmap progress
    with col4:

        st.html(
            f"""
            <div class="metric">

                <div class="label">
                    Roadmap Progress
                </div>

                <div class="value">
                    {roadmap_progress}
                </div>

                <div class="hint">
                    {completed_steps}/{len(steps)}
                    steps completed
                </div>

            </div>
            """
        )

    # =========================================================
    # YOUR NEXT STEP
    # =========================================================

    (
        next_title,
        next_focus,
        next_description,
        next_page,
        next_button,
    ) = get_next_step(
        missing_skills,
        developing_skills,
        steps,
    )

    safe_next_title = safe_text(next_title)
    safe_next_focus = safe_text(next_focus)
    safe_next_description = safe_text(next_description)

    st.html(
        f"""
        <div class="section-title">
            Your Next Step
        </div>

        <div style="
            background:#FFFDF9;
            border:1px solid #E3D9CA;
            border-left:5px solid #C96F4A;
            border-radius:14px;
            padding:18px 20px;
            margin-bottom:8px;
        ">

            <div style="
                color:#A95738;
                font-size:10px;
                font-weight:850;
                letter-spacing:0.10em;
                text-transform:uppercase;
                margin-bottom:6px;
            ">
                RECOMMENDED FOCUS
            </div>

            <div style="
                color:#3B342E;
                font-size:19px;
                font-weight:850;
                line-height:1.3;
            ">
                {safe_next_focus}
            </div>

            <div style="
                color:#756D63;
                font-size:13px;
                font-weight:700;
                margin-top:4px;
            ">
                {safe_next_title}
            </div>

            <div style="
                color:#756D63;
                font-size:12px;
                line-height:1.6;
                margin-top:7px;
            ">
                {safe_next_description}
            </div>

        </div>
        """
    )

    st.page_link(
        next_page,
        label=next_button,
        use_container_width=True,
    )

    # =========================================================
    # SKILL SNAPSHOT
    # =========================================================

    st.html(
        """
        <div class="section-title">
            Your Current Skill Snapshot
        </div>
        """
    )

    from components.cards import skill_pills

    skill_col1, skill_col2, skill_col3 = st.columns(3)

    # Strong skills
    with skill_col1:

        st.html(
            """
            <div class="card">

                <div style="
                    color:#4E7154;
                    font-weight:800;
                    font-size:14px;
                ">
                    ✓ Strong Skills
                </div>

                <div style="
                    color:#7A7067;
                    font-size:11px;
                    margin-top:5px;
                ">
                    Skills you already demonstrate
                </div>

            </div>
            """
        )

        skill_pills(
            strong_skills,
            "strong",
        )

    # Developing skills
    with skill_col2:

        st.html(
            """
            <div class="card">

                <div style="
                    color:#806225;
                    font-weight:800;
                    font-size:14px;
                ">
                    ◐ Developing Skills
                </div>

                <div style="
                    color:#7A7067;
                    font-size:11px;
                    margin-top:5px;
                ">
                    Skills that need more practice
                </div>

            </div>
            """
        )

        skill_pills(
            developing_skills,
            "developing",
        )

    # Missing skills
    with skill_col3:

        st.html(
            """
            <div class="card">

                <div style="
                    color:#985050;
                    font-weight:800;
                    font-size:14px;
                ">
                    ! Skills to Build
                </div>

                <div style="
                    color:#7A7067;
                    font-size:11px;
                    margin-top:5px;
                ">
                    Skills identified as gaps
                </div>

            </div>
            """
        )

        skill_pills(
            missing_skills,
            "missing",
        )

    # =========================================================
    # COMPLETE JOURNEY
    # =========================================================

    st.html(
        """
        <div class="section-title">
            Your Complete Journey
        </div>

        <div style="
            color:#756D63;
            font-size:12px;
            margin-top:-8px;
            margin-bottom:12px;
        ">
            Move from profile analysis to career simulation
            through one connected journey.
        </div>
        """
    )

    journey = [
        (
            "👤",
            "Profile Analysis",
            "Resume & student profile",
        ),
        (
            "📊",
            "Skill Assessment",
            "Current skill levels",
        ),
        (
            "🧩",
            "Skill Gap",
            "Missing & developing skills",
        ),
        (
            "🎯",
            "Opportunities",
            "Jobs & internships",
        ),
        (
            "🗺️",
            "Roadmap",
            "Personalized learning plan",
        ),
        (
            "📈",
            "Progress",
            "Track your growth",
        ),
        (
            "🔮",
            "Career Simulator",
            "Explore career paths",
        ),
    ]

    # First row: 4 items
    first_row = journey[:4]

    journey_columns = st.columns(4)

    for column, item in zip(
        journey_columns,
        first_row,
    ):

        icon, title, subtitle = item

        with column:

            st.html(
                f"""
                <div class="card"
                     style="
                         text-align:center;
                         min-height:135px;
                         padding:18px 12px;
                     ">

                    <div style="
                        font-size:25px;
                    ">
                        {icon}
                    </div>

                    <div style="
                        font-weight:800;
                        font-size:12px;
                        margin-top:8px;
                        color:#3B342E;
                    ">
                        {safe_text(title)}
                    </div>

                    <div
                        class="small-muted"
                        style="
                            margin-top:6px;
                            line-height:1.4;
                        "
                    >
                        {safe_text(subtitle)}
                    </div>

                </div>
                """
            )

    # Small spacing between rows
    st.html('<div style="height:8px;"></div>')

    # Second row: 3 items
    second_row = journey[4:]

    second_columns = st.columns(
        [1, 1, 1, 1],
        gap="medium",
    )

    for column, item in zip(
        second_columns[:3],
        second_row,
    ):

        icon, title, subtitle = item

        with column:

            st.html(
                f"""
                <div class="card"
                     style="
                         text-align:center;
                         min-height:135px;
                         padding:18px 12px;
                     ">

                    <div style="
                        font-size:25px;
                    ">
                        {icon}
                    </div>

                    <div style="
                        font-weight:800;
                        font-size:12px;
                        margin-top:8px;
                        color:#3B342E;
                    ">
                        {safe_text(title)}
                    </div>

                    <div
                        class="small-muted"
                        style="
                            margin-top:6px;
                            line-height:1.4;
                        "
                    >
                        {safe_text(subtitle)}
                    </div>

                </div>
                """
            )

    # =========================================================
    # TOP OPPORTUNITIES
    # =========================================================

    st.html(
        """
        <div class="section-title">
            Top Opportunities For You
        </div>
        """
    )

    from components.cards import opportunity_card

    if opportunities:

        for opportunity in opportunities[:3]:

            opportunity_card(
                opportunity
            )

    else:

        st.html(
            """
            <div class="info-strip">

                No opportunity results are available yet.
                Complete Profile Analysis first.

            </div>
            """
        )

    # =========================================================
    # PERSONALIZED ROADMAP
    # =========================================================

    st.html(
        """
        <div class="section-title">
            Personalized Learning Roadmap
        </div>
        """
    )

    if steps:

        for index, step in enumerate(
            steps[:4],
            start=1,
        ):

            if not isinstance(
                step,
                dict,
            ):
                continue

            title = (
                step.get("title")
                or step.get("step")
                or step.get("skill")
                or f"Roadmap Step {index}"
            )

            status = (
                step.get(
                    "completion_status"
                )
                or step.get(
                    "status"
                )
                or "Pending"
            )

            priority = step.get(
                "priority",
                "Medium",
            )

            duration = (
                step.get(
                    "estimated_duration"
                )
                or step.get(
                    "duration"
                )
                or "—"
            )

            st.html(
                f"""
                <div class="roadmap-step">

                    <span class="roadmap-number">
                        {index}
                    </span>

                    <b style="color:#3B342E;">
                        {safe_text(title)}
                    </b>

                    <span style="
                        float:right;
                        font-size:11px;
                        font-weight:700;
                        color:#806225;
                    ">
                        {safe_text(priority)}
                    </span>

                    <div
                        class="small-muted"
                        style="
                            margin:8px 0 0 40px;
                        "
                    >
                        {safe_text(duration)}
                        ·
                        {safe_text(status)}
                    </div>

                </div>
                """
            )

    else:

        st.html(
            """
            <div class="info-strip">

                Your personalized roadmap will appear
                after profile analysis.

            </div>
            """
        )

    # =========================================================
    # CONTINUE JOURNEY
    # =========================================================

    st.html(
        """
        <div class="section-title">
            Continue Your Journey
        </div>
        """
    )

    next_col1, next_col2 = st.columns(2)

    with next_col1:

        st.page_link(
            "pages/5_Roadmap.py",
            label="🗺️ Continue Learning Roadmap",
            use_container_width=True,
        )

    with next_col2:

        st.page_link(
            "pages/7_Career_Simulator.py",
            label="🔮 Explore Career Simulator",
            use_container_width=True,
        )

    
    # =========================================================
    # FOOTER
    # =========================================================

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
            Learn · Grow · Succeed
        </div>
        """
    )


# =============================================================
# PAGE DEFINITIONS
# =============================================================

pages = [

    st.Page(
        home,
        title="Home",
        icon="🏠",
        default=True,
    ),

    st.Page(
        "pages/1_Profile.py",
        title="Profile Analysis",
        icon="👤",
    ),

    st.Page(
        "pages/2_Skill_Assessment.py",
        title="Skill Assessment",
        icon="📊",
    ),

    st.Page(
        "pages/3_Skill_Gap.py",
        title="Skill Gap Detection",
        icon="🧩",
    ),

    st.Page(
        "pages/4_Opportunities.py",
        title="Opportunity Matching",
        icon="🎯",
    ),

    st.Page(
        "pages/5_Roadmap.py",
        title="Roadmap",
        icon="🗺️",
    ),

    st.Page(
        "pages/6_Progress.py",
        title="Progress Tracking",
        icon="📈",
    ),

    st.Page(
        "pages/7_Career_Simulator.py",
        title="Career Simulator",
        icon="🔮",
    ),
        st.Page(
        "pages/8_Career_Agent.py",
        title="Career Navigator",
        icon="🤖",
    ),
]


# =============================================================
# SIDEBAR BRAND
#
# The brand is intentionally placed before the navigation.
# st.sidebar.html() is used so the HTML is rendered instead
# of appearing literally as text.
# =============================================================

def sidebar_brand():

    st.sidebar.html(
        """
        <div style="
            padding: 8px 8px 13px 8px;
            margin-bottom: 6px;
            border-bottom: 1px solid #E3D9CA;
        ">

            <div style="
                font-size:20px;
                font-weight:850;
                color:#3B342E;
                line-height:1.2;
            ">
                🧭 PathFinder AI
            </div>

            <div style="
                margin-top:5px;
                font-size:8px;
                font-weight:750;
                letter-spacing:0.8px;
                color:#756D63;
            ">
                YOUR SKILLS · YOUR GOALS · YOUR GUIDANCE
            </div>

        </div>
        """
    )


# =============================================================
# SIDEBAR NAVIGATION
#
# Manual navigation is used instead of Streamlit's automatic
# sidebar navigation so the PathFinder brand stays at the top.
# =============================================================

def sidebar_navigation():

    st.sidebar.markdown(
        """
        <div style="
            margin: 4px 8px 3px 8px;
            color:#A95738;
            font-size:9px;
            font-weight:800;
            letter-spacing:0.12em;
            text-transform:uppercase;
        ">
            Navigation
        </div>
        """,
        unsafe_allow_html=True,
    )

    for page in pages:

        st.sidebar.page_link(
            page,
            label=page.title,
            icon=page.icon,
            use_container_width=True,
        )

    # ---------------------------------------------------------
    # Current student information
    # ---------------------------------------------------------

    profile_processed = st.session_state.get(
        "resume_processed",
        False,
    )

    if profile_processed:

        profile = get_profile()
        name = display_name(profile)

        if name:

            safe_name = safe_text(name)

            st.sidebar.markdown(
                f"""
                <div style="
                    margin:14px 8px 0 8px;
                    padding-top:10px;
                    border-top:1px solid #E3D9CA;
                    color:#756D63;
                    font-size:11px;
                ">
                    <span style="
                        color:#A95738;
                        font-weight:800;
                    ">
                        CURRENT PROFILE
                    </span>
                    <br>
                    <span style="
                        color:#3B342E;
                        font-weight:700;
                        font-size:12px;
                    ">
                        👤 {safe_name}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================
# SIDEBAR
# =============================================================

sidebar_brand()

sidebar_navigation()


# =============================================================
# STREAMLIT NAVIGATION
#
# Navigation is hidden because we are rendering the links
# manually above.
# =============================================================

pg = st.navigation(
    pages,
    position="hidden",
)


# =============================================================
# RUN CURRENT PAGE
# =============================================================

pg.run()