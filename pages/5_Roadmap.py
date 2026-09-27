import html
import streamlit as st

from components.styles import apply_styles
from utils.data_loader import (
    get_roadmap,
    get_profile,
)
from utils.progress_manager import (
    get_step_progress,
    calculate_step_progress,
)


apply_styles()


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div class="section-kicker">
        STEP 5
    </div>

    <div class="page-title">
        Personalized Roadmap
    </div>

    <div class="page-subtitle">
        A step-by-step learning and career preparation
        plan generated from your current skills,
        skill gaps and target career.
    </div>
    """
)


# ============================================================
# PROFILE CHECK
# ============================================================

profile_processed = st.session_state.get(
    "resume_processed",
    False,
)

if not profile_processed:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                🗺️
            </div>

            <h3>
                Your Roadmap Is Not Ready Yet
            </h3>

            <p>
                Upload and analyze your resume from
                Profile Analysis first.
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


# ============================================================
# LOAD DATA
# ============================================================

profile = get_profile()

personal = (
    profile.get(
        "personal_information",
        {},
    )
    if isinstance(profile, dict)
    else {}
)

user_key = (
    personal.get("email")
    or "default"
)

user_key = str(
    user_key
).strip()


roadmap_data = get_roadmap()

roadmap = roadmap_data.get(
    "personalized_roadmap",
    {},
)

if not isinstance(
    roadmap,
    dict,
):
    roadmap = {}

steps = roadmap.get(
    "steps",
    [],
)

if not isinstance(
    steps,
    list,
):
    steps = []


# ============================================================
# TARGET CAREER
# ============================================================

target_career = (
    profile.get(
        "target_career"
    )
    or "Target Career"
)

safe_career = html.escape(
    str(target_career)
)


# ============================================================
# CALCULATE REAL PROGRESS
# ============================================================

overall_progress = calculate_step_progress(
    steps,
    user_key,
)

completed = 0

for index, step in enumerate(
    steps
):

    value = get_step_progress(
        index,
        step,
        user_key,
    )

    if value >= 100:
        completed += 1


# ============================================================
# CAREER STRIP
# ============================================================

st.html(
    f"""
    <div class="info-strip">

        🎯 Target Career:
        <b>{safe_career}</b>

    </div>
    """
)


# ============================================================
# PROGRESS SUMMARY
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Overall Progress",
        f"{overall_progress}%",
    )

with c2:
    st.metric(
        "Completed Steps",
        f"{completed}/{len(steps)}",
    )

with c3:
    st.metric(
        "Roadmap Steps",
        len(steps),
    )


st.html(
    '<div class="section-title">'
    'Roadmap Completion'
    '</div>'
)

st.progress(
    overall_progress / 100
)

st.caption(
    f"{completed} of {len(steps)} roadmap steps "
    f"are fully completed."
)


# ============================================================
# ROADMAP
# ============================================================

st.html(
    '<div class="section-title">'
    'Your Learning Journey'
    '</div>'
)


if not steps:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                🗺️
            </div>

            <h3>
                No Roadmap Steps Available
            </h3>

            <p>
                Complete Profile Analysis so PathFinder
                can generate your personalized roadmap.
            </p>

        </div>
        """
    )

else:

    for index, step in enumerate(
        steps
    ):

        if not isinstance(
            step,
            dict,
        ):
            continue

        title = (
            step.get("skill")
            or step.get("title")
            or f"Step {index + 1}"
        )

        phase = step.get(
            "phase",
            "Learning",
        )

        priority = step.get(
            "priority",
            "Normal",
        )

        duration = step.get(
            "estimated_duration",
            "",
        )

        why_needed = step.get(
            "why_needed",
            "",
        )

        learning_goal = step.get(
            "learning_goal",
            "",
        )

        recommended_action = step.get(
            "recommended_action",
            "",
        )

        prerequisites = step.get(
            "prerequisites",
            [],
        )

        current_progress = get_step_progress(
            index,
            step,
            user_key,
        )

        if current_progress >= 100:
            status = "Completed"
            status_color = "#4E7154"
            status_bg = "#E5EFE5"

        elif current_progress > 0:
            status = "In Progress"
            status_color = "#806225"
            status_bg = "#F4EBD7"

        else:
            status = "Not Started"
            status_color = "#985050"
            status_bg = "#F5E2E0"


        safe_title = html.escape(
            str(title)
        )

        safe_phase = html.escape(
            str(phase)
        )

        safe_priority = html.escape(
            str(priority)
        )

        safe_duration = html.escape(
            str(duration)
        )

        safe_why = html.escape(
            str(why_needed)
        )

        safe_goal = html.escape(
            str(learning_goal)
        )

        safe_action = html.escape(
            str(recommended_action)
        )


        prerequisite_text = ""

        if isinstance(
            prerequisites,
            list,
        ):
            prerequisite_text = ", ".join(
                str(x)
                for x in prerequisites
            )

        elif prerequisites:
            prerequisite_text = str(
                prerequisites
            )

        safe_prerequisites = html.escape(
            prerequisite_text
        )


        st.html(
            f"""
            <div class="roadmap-step">

                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                    margin-bottom:12px;
                ">

                    <span class="roadmap-number">
                        {index + 1}
                    </span>

                    <div style="flex:1;">

                        <div style="
                            font-size:17px;
                            font-weight:850;
                            color:#3B342E;
                        ">
                            {safe_title}
                        </div>

                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_phase}
                            ·
                            Priority: {safe_priority}
                        </div>

                    </div>

                    <div style="
                        background:{status_bg};
                        color:{status_color};
                        border-radius:999px;
                        padding:7px 11px;
                        font-size:11px;
                        font-weight:850;
                        white-space:nowrap;
                    ">
                        {status}
                    </div>

                </div>


                <div style="
                    height:8px;
                    background:#EAE1D3;
                    border-radius:999px;
                    overflow:hidden;
                    margin:12px 0 8px;
                ">

                    <div style="
                        width:{current_progress}%;
                        height:100%;
                        background:#6F8F73;
                        border-radius:999px;
                    "></div>

                </div>


                <div style="
                    text-align:right;
                    color:#A95738;
                    font-size:12px;
                    font-weight:800;
                    margin-bottom:12px;
                ">
                    {current_progress}% complete
                </div>


                {
                    f'''
                    <div class="small-muted"
                         style="margin-bottom:7px;">
                        <b>Duration:</b>
                        {safe_duration}
                    </div>
                    '''
                    if duration
                    else ""
                }


                {
                    f'''
                    <div style="
                        margin-top:10px;
                        line-height:1.55;
                    ">
                        <b>Why this is needed</b>
                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_why}
                        </div>
                    </div>
                    '''
                    if why_needed
                    else ""
                }


                {
                    f'''
                    <div style="
                        margin-top:12px;
                        line-height:1.55;
                    ">
                        <b>Learning Goal</b>
                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_goal}
                        </div>
                    </div>
                    '''
                    if learning_goal
                    else ""
                }


                {
                    f'''
                    <div style="
                        margin-top:12px;
                        line-height:1.55;
                    ">
                        <b>Recommended Action</b>
                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_action}
                        </div>
                    </div>
                    '''
                    if recommended_action
                    else ""
                }


                {
                    f'''
                    <div style="
                        margin-top:12px;
                        line-height:1.55;
                    ">
                        <b>Prerequisites</b>
                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_prerequisites}
                        </div>
                    </div>
                    '''
                    if prerequisite_text
                    else ""
                }

            </div>
            """
        )


# ============================================================
# PROGRESS INFORMATION
# ============================================================

st.html(
    '<div class="section-title">'
    'Update Your Progress'
    '</div>'
)

st.html(
    """
    <div class="info-strip">

        Go to <b>Progress Tracking</b> to update
        the completion percentage of each roadmap step.

        <br><br>

        Your Roadmap page automatically reflects
        those saved progress values.

    </div>
    """
)

st.page_link(
    "pages/6_Progress.py",
    label="📈 Update Progress",
    use_container_width=True,
)