import hashlib
import html

import streamlit as st

from components.styles import apply_styles
from components.cards import skill_pills

from utils.data_loader import (
    get_profile,
)

from utils.profile_pipeline import (
    extract_resume_text,
    clear_previous_results,
    run_pipeline,
)


apply_styles()


# ============================================================
# CAREER LIST
# ============================================================

from pathlib import Path
import pandas as pd


ROOT = Path(
    __file__
).resolve().parents[1]

CAREERS_FILE = (
    ROOT
    / "data"
    / "careers"
    / "careers.csv"
)


def load_careers():
    """
    Load available target careers from careers.csv.
    """

    if not CAREERS_FILE.exists():
        return []

    try:

        df = pd.read_csv(
            CAREERS_FILE
        )

        careers = []

        possible_columns = [
            "career",
            "career_name",
            "title",
            "name",
            "target_career",
        ]

        selected_column = None

        for column in possible_columns:

            if column in df.columns:
                selected_column = column
                break

        if selected_column:

            careers = (
                df[selected_column]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

        elif len(df.columns) > 0:

            careers = (
                df.iloc[:, 0]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

        careers = list(
            dict.fromkeys(
                x
                for x in careers
                if x
            )
        )

        return careers

    except Exception:
        return []


careers = load_careers()


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div class="section-kicker">
        STEP 1
    </div>

    <div class="page-title">
        Student Profile
    </div>

    <div class="page-subtitle">
        Upload your resume and let PathFinder AI
        understand your skills, projects, experience
        and career goals.
    </div>
    """
)


# ============================================================
# PROCESS STEPPER
# ============================================================

st.html(
    """
    <div class="stepper">

        <div class="step active">
            1 · Upload Resume
        </div>

        <div class="connector"></div>

        <div class="step">
            2 · Personal Details
        </div>

        <div class="connector"></div>

        <div class="step">
            3 · Career Goal
        </div>

    </div>
    """
)


# ============================================================
# RESUME UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "Upload Resume",
    type=[
        "pdf",
        "docx",
    ],
    help="PDF or DOCX, up to 10 MB",
)


if uploaded:

    file_signature = hashlib.md5(
        uploaded.getvalue()
    ).hexdigest()

    previous_signature = (
        st.session_state.get(
            "resume_file_signature"
        )
    )

    is_new_resume = (
        previous_signature
        != file_signature
    )


    # --------------------------------------------------------
    # NEW RESUME
    # --------------------------------------------------------

    if is_new_resume:

        clear_previous_results()

        st.session_state.resume_text = ""
        st.session_state.resume_filename = ""
        st.session_state.resume_file_signature = (
            file_signature
        )

        st.session_state.resume_processed = (
            False
        )

        st.session_state.profile_created = (
            False
        )

        st.session_state.selected_target_career = (
            None
        )


        for key in [
            "profile_name",
            "profile_email",
            "profile_phone",
            "profile_goal",
            "target_career_select",
        ]:

            st.session_state.pop(
                key,
                None,
            )


        if uploaded.size > (
            10 * 1024 * 1024
        ):

            st.error(
                "Please upload a file smaller than 10 MB."
            )

        else:

            try:

                text = extract_resume_text(
                    uploaded.getvalue(),
                    uploaded.name,
                )

                if not text.strip():

                    st.error(
                        "No readable text was found. "
                        "Please upload a text-based PDF/DOCX resume."
                    )

                else:

                    st.session_state.resume_text = (
                        text
                    )

                    st.session_state.resume_filename = (
                        uploaded.name
                    )

                    st.success(
                        f"New resume loaded successfully: "
                        f"{uploaded.name}"
                    )

                    st.caption(
                        f"Extracted approximately "
                        f"{len(text.split())} words "
                        f"for AI profile analysis."
                    )

            except Exception as exc:

                st.error(
                    f"Could not read this resume: {exc}"
                )


    elif st.session_state.get(
        "resume_text"
    ):

        st.caption(
            "Current resume: "
            + st.session_state.get(
                "resume_filename",
                uploaded.name,
            )
        )


# ============================================================
# CURRENT DATA
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

resume_text = st.session_state.get(
    "resume_text",
    "",
)


# ============================================================
# PROFILE ANALYSIS FORM
# ============================================================

if resume_text:

    st.html(
        '<div class="section-title">'
        'AI Profile Analysis'
        '</div>'
    )

    st.info(
        "PathFinder will extract your name, contact details, "
        "skills, projects, internships and certifications "
        "from the uploaded resume."
    )


    p1, p2 = st.columns(2)


    # --------------------------------------------------------
    # PERSONAL DETAILS
    # --------------------------------------------------------

    with p1:

        name = st.text_input(
            "Full Name",
            value=personal.get(
                "name",
                "",
            ),
            key="profile_name",
        )

        email = st.text_input(
            "Email Address",
            value=personal.get(
                "email",
                "",
            ),
            key="profile_email",
        )


    # --------------------------------------------------------
    # PHONE + TARGET CAREER
    # --------------------------------------------------------

    with p2:

        phone = st.text_input(
            "Phone Number",
            value=personal.get(
                "phone",
                "",
            ),
            key="profile_phone",
        )


        if careers:

            existing_target = (
                profile.get(
                    "target_career",
                    "",
                )
            )

            selected_target = (
                st.session_state.get(
                    "selected_target_career"
                )
            )


            if selected_target not in careers:

                selected_target = (
                    existing_target
                    if existing_target in careers
                    else None
                )


            target = st.selectbox(
                "Target Career",
                careers,
                index=(
                    careers.index(
                        selected_target
                    )
                    if selected_target in careers
                    else None
                ),
                placeholder=(
                    "Select your target career"
                    if selected_target not in careers
                    else None
                ),
                key="target_career_select",
                help=(
                    "Choose the career you want "
                    "PathFinder to prepare you for. "
                    "This is your preference and is not "
                    "automatically taken from the resume objective."
                ),
            )

            st.caption(
                "Target Career is your preference. "
                "Your resume's objective is kept separately "
                "as Career Goal."
            )

        else:

            target = None

            st.error(
                "No careers were found in "
                "data/careers/careers.csv."
            )


    # --------------------------------------------------------
    # CAREER GOAL
    # --------------------------------------------------------

    goal = st.text_area(
        "Career Goal / Objective",
        value=profile.get(
            "career_goal",
            "",
        ),
        height=100,
        key="profile_goal",
        placeholder=(
            "This is taken from your resume objective, "
            "but you can edit it if needed."
        ),
    )


    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    if st.button(
        "Analyze Profile & Build My Path",
        type="primary",
        use_container_width=True,
    ):

        if not careers:

            st.error(
                "Please make sure careers.csv "
                "exists in data/careers/."
            )

        elif not target:

            st.error(
                "Please select your Target Career. "
                "It is your preferred career path."
            )

        else:

            try:

                from resume_processing.profile_analyzer import (
                    analyze_profile,
                )


                # ------------------------------------------------
                # ANALYZE CURRENT RESUME
                # ------------------------------------------------

                parsed = analyze_profile(
                    resume_text,
                    student_id="S001",
                )


                # ------------------------------------------------
                # TARGET CAREER IS USER PREFERENCE
                # ------------------------------------------------

                parsed["target_career"] = (
                    str(target).strip()
                )

                st.session_state.selected_target_career = (
                    parsed["target_career"]
                )


                # ------------------------------------------------
                # PERSONAL INFORMATION
                # ------------------------------------------------

                parsed_personal = (
                    parsed.setdefault(
                        "personal_information",
                        {},
                    )
                )


                parsed_personal["name"] = (
                    name.strip()
                    or parsed_personal.get(
                        "name",
                        "",
                    )
                )

                parsed_personal["email"] = (
                    email.strip()
                    or parsed_personal.get(
                        "email",
                        "",
                    )
                )

                parsed_personal["phone"] = (
                    phone.strip()
                    or parsed_personal.get(
                        "phone",
                        "",
                    )
                )


                # ------------------------------------------------
                # CAREER GOAL
                # ------------------------------------------------

                parsed["career_goal"] = (
                    goal.strip()
                    or parsed.get(
                        "career_goal",
                        "",
                    )
                )


                # ------------------------------------------------
                # COMPLETE PATHFINDER PIPELINE
                # ------------------------------------------------

                with st.spinner(
                    "Analyzing profile → "
                    "assessing skills → "
                    "detecting gaps → "
                    "generating roadmap → "
                    "matching opportunities..."
                ):

                    run_pipeline(
                        parsed
                    )


                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                st.session_state.resume_processed = (
                    True
                )

                st.session_state.profile_created = (
                    True
                )

                st.success(
                    "Profile analysis completed successfully! "
                    "Your personalized PathFinder journey is ready."
                )

                st.rerun()


            except Exception as exc:

                st.session_state.resume_processed = (
                    False
                )

                st.session_state.profile_created = (
                    False
                )

                st.error(
                    f"Profile pipeline failed: {exc}"
                )


# ============================================================
# PROFILE RESULT
# ============================================================

st.html(
    '<div class="section-title">'
    'Profile Analysis Result'
    '</div>'
)


profile = get_profile()

personal = (
    profile.get(
        "personal_information",
        {},
    )
    if isinstance(profile, dict)
    else {}
)


profile_ready = (
    st.session_state.get(
        "profile_created",
        False,
    )
    and
    st.session_state.get(
        "resume_processed",
        False,
    )
)


if profile_ready and personal:

    st.html(
        """
        <div class="success-strip">
            ✓ Profile analysis completed successfully
        </div>
        """
    )

    st.html(
        '<div style="height:10px"></div>'
    )


    # ========================================================
    # PERSONAL + CAREER
    # ========================================================

    a, b = st.columns(
        [1, 2]
    )


    with a:

        safe_name = html.escape(
            str(
                personal.get(
                    "name"
                )
                or "Student"
            ).strip()
        )

        safe_email = html.escape(
            str(
                personal.get(
                    "email"
                )
                or "Not provided"
            ).strip()
        )

        safe_phone = html.escape(
            str(
                personal.get(
                    "phone"
                )
                or "Not provided"
            ).strip()
        )


        st.html(
            f"""
            <div class="profile-card">

                <div style="
                    font-size:38px;
                ">
                    👤
                </div>

                <div style="
                    font-size:20px;
                    font-weight:850;
                    margin-top:6px;
                ">
                    {safe_name}
                </div>

                <div class="small-muted"
                     style="
                        margin-top:9px;
                        line-height:1.8;
                     ">

                    <div>
                        ✉ {safe_email}
                    </div>

                    <div>
                        ☎ {safe_phone}
                    </div>

                </div>

            </div>
            """
        )


    with b:

        safe_goal = html.escape(
            str(
                profile.get(
                    "career_goal"
                )
                or "Not provided"
            ).strip()
        )

        safe_target = html.escape(
            str(
                profile.get(
                    "target_career"
                )
                or "Not selected"
            ).strip()
        )


        st.html(
            f"""
            <div class="profile-card">

                <div style="
                    font-weight:850;
                    margin-bottom:6px;
                ">
                    Career Goal / Resume Objective
                </div>

                <div class="small-muted"
                     style="
                        line-height:1.6;
                        margin-bottom:18px;
                     ">
                    {safe_goal}
                </div>

                <div style="
                    font-weight:850;
                    margin-bottom:6px;
                ">
                    Target Career
                </div>

                <div style="
                    color:#A95738;
                    font-weight:800;
                ">
                    {safe_target}
                </div>

            </div>
            """
        )


    # ========================================================
    # DETECTED SKILLS
    # ========================================================

    st.html(
        '<div class="section-title">'
        'Detected Skills'
        '</div>'
    )


    all_skills = []

    skills_data = profile.get(
        "skills",
        {},
    )


    if isinstance(
        skills_data,
        dict,
    ):

        for values in skills_data.values():

            if isinstance(
                values,
                list,
            ):

                for value in values:

                    cleaned = str(
                        value
                    ).strip()

                    if cleaned:
                        all_skills.append(
                            cleaned
                        )


    elif isinstance(
        skills_data,
        list,
    ):

        for value in skills_data:

            if isinstance(
                value,
                dict,
            ):
                value = (
                    value.get("skill")
                    or value.get("name")
                    or ""
                )

            cleaned = str(
                value
            ).strip()

            if cleaned:
                all_skills.append(
                    cleaned
                )


    # Remove duplicates
    all_skills = list(
        dict.fromkeys(
            all_skills
        )
    )


    if all_skills:

        skill_pills(
            all_skills,
            "neutral",
        )

    else:

        st.caption(
            "No skills detected."
        )


    # ========================================================
    # PROJECTS / EXPERIENCE / CERTIFICATIONS
    # ========================================================

    st.html(
        '<div class="section-title">'
        'Projects, Experience & Certifications'
        '</div>'
    )


    projects = profile.get(
        "projects",
        [],
    )

    internships = profile.get(
        "internships",
        [],
    )

    certifications = profile.get(
        "certifications",
        [],
    )


    if not isinstance(
        projects,
        list,
    ):
        projects = []


    if not isinstance(
        internships,
        list,
    ):
        internships = []


    if not isinstance(
        certifications,
        list,
    ):
        certifications = []


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Projects",
            len(projects),
        )


    with col2:

        st.metric(
            "Internships",
            len(internships),
        )


    with col3:

        st.metric(
            "Certifications",
            len(certifications),
        )


    # ========================================================
    # PROJECT DETAILS
    # ========================================================

    if projects:

        st.html(
            '<div class="section-title">'
            'Detected Projects'
            '</div>'
        )


        for project in projects:

            if isinstance(
                project,
                dict,
            ):

                project_name = (
                    project.get(
                        "name"
                    )
                    or project.get(
                        "title"
                    )
                    or "Project"
                )

                description = (
                    project.get(
                        "description",
                        "",
                    )
                )

                if isinstance(
                    description,
                    list,
                ):

                    description = " ".join(
                        str(x)
                        for x in description
                    )

            else:

                project_name = str(
                    project
                )

                description = ""


            safe_project_name = (
                html.escape(
                    str(
                        project_name
                    ).strip()
                )
            )

            safe_description = (
                html.escape(
                    str(
                        description
                    ).strip()
                )
            )


            description_html = ""

            if safe_description:

                description_html = (
                    f"""
                    <div class="small-muted"
                         style="
                            margin-top:6px;
                            line-height:1.5;
                         ">
                        {safe_description}
                    </div>
                    """
                )


            st.html(
                f"""
                <div class="card"
                     style="margin:8px 0;">

                    <b>
                        {safe_project_name}
                    </b>

                    {description_html}

                </div>
                """
            )


else:

    st.info(
        "Upload a resume and select your "
        "Target Career to build the PathFinder profile."
    )