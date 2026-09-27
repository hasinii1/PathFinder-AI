import html
import streamlit as st

from components.styles import apply_styles
from utils.data_loader import (
    get_profile,
    get_roadmap,
)
from utils.progress_manager import (
    get_progress,
    get_step_progress,
    update_step_progress,
    get_project_progress,
    update_project_progress,
    calculate_step_progress,
)


apply_styles()


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div class="section-kicker">
        STEP 6
    </div>

    <div class="page-title">
        Progress Tracking
    </div>

    <div class="page-subtitle">
        Track your learning journey, roadmap steps
        and real projects as you move toward your
        target career.
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
                📈
            </div>

            <h2>
                Progress Tracking Starts Here
            </h2>

            <p>
                Complete your Profile Analysis first.
                <br><br>
                Once your personalized roadmap is generated,
                you can track your learning and project progress.
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
# PROFILE / USER KEY
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


# ============================================================
# ROADMAP DATA
# ============================================================

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
# CURRENT PROGRESS
# ============================================================

progress_data = get_progress(
    user_key
)

overall_progress = calculate_step_progress(
    steps,
    user_key,
)


# ============================================================
# PROJECTS FROM CURRENT RESUME
# ============================================================

projects = profile.get(
    "projects",
    [],
)

if not isinstance(
    projects,
    list,
):
    projects = []


project_names = []

for project in projects:

    if isinstance(
        project,
        dict,
    ):
        name = (
            project.get("name")
            or project.get("title")
        )

    else:
        name = str(project)

    if name:
        name = str(
            name
        ).strip()

        if name and name not in project_names:
            project_names.append(
                name
            )


# ============================================================
# TOP METRICS
# ============================================================

completed_steps = 0

for index, step in enumerate(
    steps
):
    value = get_step_progress(
        index,
        step,
        user_key,
    )

    if value >= 100:
        completed_steps += 1


completed_projects = 0

for project_name in project_names:

    value = get_project_progress(
        project_name,
        user_key,
    )

    if value >= 100:
        completed_projects += 1


c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Roadmap Progress",
        f"{overall_progress}%",
    )

with c2:
    st.metric(
        "Steps Completed",
        f"{completed_steps}/{len(steps)}",
    )

with c3:
    st.metric(
        "Projects Completed",
        f"{completed_projects}/{len(project_names)}",
    )

with c4:
    st.metric(
        "Total Projects",
        len(project_names),
    )


# ============================================================
# OVERALL PROGRESS
# ============================================================

st.html(
    '<div class="section-title">'
    'Overall Journey'
    '</div>'
)

st.progress(
    overall_progress / 100
)

st.caption(
    f"Your current roadmap completion is "
    f"{overall_progress}%."
)


# ============================================================
# ROADMAP LEARNING PROGRESS
# ============================================================

st.html(
    '<div class="section-title">'
    'Learning & Roadmap Progress'
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
                No Roadmap Steps Yet
            </h3>

            <p>
                Your personalized roadmap will appear
                after your profile has been analyzed.
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

        skill = (
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
            "",
        )

        current = get_step_progress(
            index,
            step,
            user_key,
        )

        safe_skill = html.escape(
            str(skill)
        )

        safe_phase = html.escape(
            str(phase)
        )

        safe_priority = html.escape(
            str(priority)
        )

        st.html(
            f"""
            <div class="roadmap-step">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:15px;
                    margin-bottom:8px;
                ">

                    <div>
                        <div style="
                            font-size:16px;
                            font-weight:850;
                            color:#3B342E;
                        ">
                            {index + 1}.
                            {safe_skill}
                        </div>

                        <div class="small-muted"
                             style="margin-top:4px;">
                            {safe_phase}
                            {(" · " + safe_priority)
                             if safe_priority
                             else ""}
                        </div>
                    </div>

                    <div style="
                        color:#A95738;
                        font-weight:850;
                        font-size:14px;
                    ">
                        {current}%
                    </div>

                </div>

            </div>
            """
        )

        new_value = st.slider(
            f"Progress — {skill}",
            0,
            100,
            current,
            5,
            key=f"progress_step_{index}",
        )

        if new_value != current:

            update_step_progress(
                index,
                step,
                new_value,
                user_key,
            )

            st.rerun()


# ============================================================
# PROJECT PROGRESS
# ============================================================

st.html(
    '<div class="section-title">'
    'Project Progress'
    '</div>'
)

if not project_names:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                💻
            </div>

            <h3>
                No Projects Detected
            </h3>

            <p>
                Projects detected from your uploaded resume
                will appear here automatically.
            </p>

        </div>
        """
    )

else:

    for index, project_name in enumerate(
        project_names
    ):

        current = get_project_progress(
            project_name,
            user_key,
        )

        safe_project = html.escape(
            project_name
        )

        st.html(
            f"""
            <div class="card"
                 style="margin:10px 0;">

                <div style="
                    font-size:15px;
                    font-weight:850;
                    color:#3B342E;
                ">
                    💻 {safe_project}
                </div>

                <div class="small-muted"
                     style="margin-top:5px;">
                    Track how much of this project
                    you have completed.
                </div>

            </div>
            """
        )

        new_value = st.slider(
            f"Project completion — {project_name}",
            0,
            100,
            current,
            5,
            key=f"project_progress_{index}",
        )

        if new_value != current:

            update_project_progress(
                project_name,
                new_value,
                user_key,
            )

            st.rerun()


# ============================================================
# PROGRESS GUIDE
# ============================================================

st.html(
    '<div class="section-title">'
    'How Progress Works'
    '</div>'
)

st.html(
    """
    <div class="info-strip">

        <b>0%</b> → Not started<br>

        <b>25%</b> → Started learning / planning<br>

        <b>50%</b> → In progress<br>

        <b>75%</b> → Almost completed<br>

        <b>100%</b> → Completed

    </div>
    """
)