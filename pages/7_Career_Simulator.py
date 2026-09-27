import streamlit as st
import pandas as pd

from components.styles import apply_styles
from utils.data_loader import (
    get_profile,
    get_roadmap,
    ROOT,
)


# ============================================================
# PAGE SETUP
# ============================================================

apply_styles()


# ============================================================
# LOAD PROFILE
# ============================================================

profile = get_profile()


# ============================================================
# LOAD CAREERS FROM careers.csv
# ============================================================

CAREERS_FILE = (
    ROOT
    / "data"
    / "careers"
    / "careers.csv"
)


def load_career_data():

    if not CAREERS_FILE.exists():

        return pd.DataFrame()

    try:

        df = pd.read_csv(
            CAREERS_FILE
        )

        required_columns = {
            "career",
            "required_skills",
        }

        if not required_columns.issubset(
            df.columns
        ):

            return pd.DataFrame()

        return df

    except Exception:

        return pd.DataFrame()


careers_df = load_career_data()


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div class="section-kicker">
        WHAT-IF
    </div>

    <div class="page-title">
        Career Simulator
    </div>

    <div class="page-subtitle">
        Explore how your current skill profile maps
        to different career directions.
    </div>
    """
)


# ============================================================
# CHECK CAREER DATA
# ============================================================

if careers_df.empty:

    st.error(
        "No career data is available. "
        "Please check data/careers/careers.csv."
    )

    st.stop()


# ============================================================
# CHECK PROFILE
# ============================================================

personal = profile.get(
    "personal_information",
    {}
)


if not personal.get("name"):

    st.info(
        "Analyze your profile first to use "
        "the Career Simulator."
    )

    st.stop()


# ============================================================
# GET ALL CAREERS
# ============================================================

career_list = (
    careers_df["career"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)


career_list = list(
    dict.fromkeys(
        career
        for career in career_list
        if career
    )
)


if not career_list:

    st.error(
        "No careers are available in careers.csv."
    )

    st.stop()


# ============================================================
# CURRENT TARGET CAREER
# ============================================================

current_career = profile.get(
    "target_career"
)


if current_career in career_list:

    current_index = career_list.index(
        current_career
    )

else:

    current_index = 0


# ============================================================
# CAREER SELECTOR
# ============================================================

career = st.selectbox(
    "Choose a career to explore",
    career_list,
    index=current_index,
    help=(
        "All careers are loaded directly "
        "from careers.csv."
    ),
)


# ============================================================
# FIND SELECTED CAREER
# ============================================================

selected_rows = careers_df[
    careers_df["career"]
    .astype(str)
    .str.strip()
    == career
]


if selected_rows.empty:

    st.error(
        "The selected career could not be found."
    )

    st.stop()


career_row = selected_rows.iloc[0]


# ============================================================
# REQUIRED SKILLS
# ============================================================

raw_required_skills = str(
    career_row.get(
        "required_skills",
        "",
    )
)


required_skills = [
    skill.strip()
    for skill in raw_required_skills.split("|")
    if skill.strip()
]


# ============================================================
# STUDENT PROFILE SKILLS
# ============================================================

student_skills = set()

skills_data = profile.get(
    "skills",
    {}
)


if isinstance(
    skills_data,
    dict,
):

    for skill_group in skills_data.values():

        if isinstance(
            skill_group,
            list,
        ):

            for skill in skill_group:

                if isinstance(
                    skill,
                    str,
                ):

                    student_skills.add(
                        skill.strip().lower()
                    )


elif isinstance(
    skills_data,
    list,
):

    for skill in skills_data:

        if isinstance(
            skill,
            str,
        ):

            student_skills.add(
                skill.strip().lower()
            )


# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skill(skill):

    skill = str(
        skill
    ).strip().lower()

    aliases = {

        "github": "git",

        "git hub": "git",

        "git": "git",

        "microsoft excel": "excel",

        "ms excel": "excel",

        "excel": "excel",

        "sklearn": "scikit-learn",

        "scikit learn": "scikit-learn",

        "scikit-learn": "scikit-learn",

        "ai": "artificial intelligence",

        "artificial intelligence":
            "artificial intelligence",

        "ml": "machine learning",

        "machine learning":
            "machine learning",

        "machine-learning":
            "machine learning",

        "nlp":
            "natural language processing",

        "natural language processing":
            "natural language processing",

        "power bi":
            "power bi",
    }

    return aliases.get(
        skill,
        skill,
    )


normalized_student_skills = {
    normalize_skill(skill)
    for skill in student_skills
}


# ============================================================
# COMPARE SKILLS
# ============================================================

already_have = []

need_to_learn = []


for required_skill in required_skills:

    normalized_required = normalize_skill(
        required_skill
    )

    if normalized_required in normalized_student_skills:

        already_have.append(
            required_skill
        )

    else:

        need_to_learn.append(
            required_skill
        )


# ============================================================
# MATCH PERCENTAGE
# ============================================================

if required_skills:

    match_percentage = round(
        (
            len(already_have)
            / len(required_skills)
        )
        * 100
    )

else:

    match_percentage = 0


# ============================================================
# EXISTING WHAT-IF RESULT
# ============================================================

roadmap = get_roadmap()

simulation_data = roadmap.get(
    "what_if_simulations",
    {}
)


if not isinstance(
    simulation_data,
    dict,
):

    simulation_data = {}


existing_result = simulation_data.get(
    career,
    {}
)


# ============================================================
# USE EXISTING SIMULATION DATA
# ============================================================

if existing_result:

    existing_match = existing_result.get(
        "match_percentage"
    )

    if existing_match is not None:

        match_percentage = existing_match

    existing_have = existing_result.get(
        "already_have"
    )

    existing_missing = existing_result.get(
        "need_to_learn"
    )

    if isinstance(
        existing_have,
        list,
    ):

        already_have = existing_have

    if isinstance(
        existing_missing,
        list,
    ):

        need_to_learn = existing_missing


# ============================================================
# CAREER HERO
# ============================================================

st.html(
    f"""
    <div class="hero">

        <div class="section-kicker">
            WHAT-IF CAREER
        </div>

        <h1>
            {career}
        </h1>

        <p>
            Current profile match:
            <b>
                {match_percentage}%
            </b>
        </p>

    </div>
    """
)


# ============================================================
# MATCH SUMMARY
# ============================================================

m1, m2, m3 = st.columns(3)


with m1:

    st.html(
        f"""
        <div class="metric">

            <div class="label">
                Match
            </div>

            <div class="value">
                {match_percentage}%
            </div>

            <div class="hint">
                Current profile alignment
            </div>

        </div>
        """
    )


with m2:

    st.html(
        f"""
        <div class="metric">

            <div class="label">
                Skills You Have
            </div>

            <div class="value">
                {len(already_have)}
            </div>

            <div class="hint">
                Required skills matched
            </div>

        </div>
        """
    )


with m3:

    st.html(
        f"""
        <div class="metric">

            <div class="label">
                Skills To Build
            </div>

            <div class="value">
                {len(need_to_learn)}
            </div>

            <div class="hint">
                Skills to develop
            </div>

        </div>
        """
    )


# ============================================================
# SKILL COMPARISON
# ============================================================

st.html(
    """
    <div class="section-title">
        Career Skill Comparison
    </div>
    """
)


a, b = st.columns(2)


# ============================================================
# ALREADY HAVE
# ============================================================

with a:

    have_html = ""

    if already_have:

        for skill in already_have:

            have_html += f"""
            <div style="
                padding:7px 0;
                border-bottom:1px solid #E3D9CA;
            ">
                ✓ {skill}
            </div>
            """

    else:

        have_html = """
        <div class="small-muted">
            No matching required skills detected yet.
        </div>
        """

    st.html(
        f"""
        <div class="card">

            <h4>
                ✓ Already Have
            </h4>

            {have_html}

        </div>
        """
    )


# ============================================================
# NEED TO LEARN
# ============================================================

with b:

    missing_html = ""

    if need_to_learn:

        for skill in need_to_learn:

            missing_html += f"""
            <div style="
                padding:7px 0;
                border-bottom:1px solid #E3D9CA;
            ">
                → {skill}
            </div>
            """

    else:

        missing_html = """
        <div class="small-muted">
            No additional required skills detected.
        </div>
        """

    st.html(
        f"""
        <div class="card">

            <h4>
                → Need to Learn
            </h4>

            {missing_html}

        </div>
        """
    )


# ============================================================
# REQUIRED SKILLS
# ============================================================

st.html(
    """
    <div class="section-title">
        Required Skills For This Career
    </div>
    """
)


if required_skills:

    from components.cards import skill_pills

    skill_pills(
        required_skills,
        "neutral",
    )

else:

    st.info(
        "No required skills are defined for "
        "this career in careers.csv."
    )


# ============================================================
# ADDITIONAL ROADMAP
# ============================================================

st.html(
    """
    <div class="section-title">
        Additional Roadmap
    </div>
    """
)


if existing_result:

    additional_roadmap = existing_result.get(
        "additional_roadmap",
        []
    )

    if additional_roadmap:

        for item in additional_roadmap:

            st.html(
                f"""
                <div class="roadmap-step">

                    <span class="roadmap-number">
                        {item.get(
                            "step_number",
                            ""
                        )}
                    </span>

                    <b>
                        {item.get(
                            "skill",
                            "Skill"
                        )}
                    </b>

                    <br>

                    <span class="small-muted">
                        {item.get(
                            "action",
                            ""
                        )}
                    </span>

                </div>
                """
            )

    else:

        st.info(
            "No additional roadmap has been generated "
            "for this career yet."
        )

else:

    if need_to_learn:

        for index, skill in enumerate(
            need_to_learn,
            start=1,
        ):

            st.html(
                f"""
                <div class="roadmap-step">

                    <span class="roadmap-number">
                        {index}
                    </span>

                    <b>
                        Build {skill}
                    </b>

                    <br>

                    <span class="small-muted">
                        Add {skill} to your learning plan
                        and practice it through projects.
                    </span>

                </div>
                """
            )

    else:

        st.info(
            "Your current profile covers the "
            "required skills for this career."
        )