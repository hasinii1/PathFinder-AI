import html
import streamlit as st

from components.styles import apply_styles
from components.cards import skill_pills
from utils.data_loader import get_skill_gap, skill_names


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------
apply_styles()


# ---------------------------------------------------------
# CHECK WHETHER CURRENT SESSION HAS PROCESSED A RESUME
# ---------------------------------------------------------
resume_processed = st.session_state.get("resume_processed", False)


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------
st.html(
    """
    <div class="section-kicker">STEP 3</div>

    <div class="page-title">
        Skill Gap Detection
    </div>

    <div class="page-subtitle">
        Compare your current skills with the requirements
        of your selected career.
    </div>
    """
)


# ---------------------------------------------------------
# SHOW EMPTY STATE BEFORE RESUME ANALYSIS
# ---------------------------------------------------------
if not resume_processed:

    st.html(
        """
        <div class="empty-state">
            <div class="empty-icon">🧩</div>

            <h3>Skill Gap Detection Not Available Yet</h3>

            <p class="small-muted">
                Upload and analyze your resume from
                <b>Profile Analysis</b> first.
                Your skill gaps will be calculated from
                your current resume and selected career.
            </p>
        </div>
        """
    )

    st.stop()


# ---------------------------------------------------------
# LOAD SKILL GAP ONLY AFTER RESUME IS PROCESSED
# ---------------------------------------------------------
raw_data = get_skill_gap()

data = raw_data.get(
    "skill_gap_analysis",
    {}
)


# ---------------------------------------------------------
# EXTRACT DATA
# ---------------------------------------------------------
career = data.get(
    "target_career",
    "Not selected"
)

strong = skill_names(
    data.get("strong_skills")
)

developing = skill_names(
    data.get("developing_skills")
)

missing = skill_names(
    data.get("missing_skills")
)

readiness = data.get(
    "career_readiness_percentage",
    0
)


# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Career Readiness",
        f"{float(readiness):.0f}%"
    )

with c2:
    st.metric(
        "Strong Skills",
        len(strong)
    )

with c3:
    st.metric(
        "Developing",
        len(developing)
    )

with c4:
    st.metric(
        "Missing",
        len(missing)
    )


# ---------------------------------------------------------
# TARGET CAREER
# ---------------------------------------------------------
safe_career = html.escape(str(career))

st.html(
    f"""
    <div class="info-strip">
        Target career:
        <b>{safe_career}</b>
    </div>
    """
)


# ---------------------------------------------------------
# SKILL PROFILE
# ---------------------------------------------------------
st.html(
    """
    <div class="section-title">
        Your Skill Profile
    </div>
    """
)


a, b, c = st.columns(3)


with a:

    st.markdown("**Strong Skills**")

    skill_pills(
        strong,
        "strong"
    )


with b:

    st.markdown("**Partial / Developing Skills**")

    skill_pills(
        developing,
        "developing"
    )


with c:

    st.markdown("**Missing Skills**")

    skill_pills(
        missing,
        "missing"
    )


# ---------------------------------------------------------
# KEY SKILL GAPS
# ---------------------------------------------------------
st.html(
    """
    <div class="section-title">
        Key Skill Gaps
    </div>
    """
)


if not missing:

    st.html(
        """
        <div class="success-strip">
            ✓ No major skill gaps detected for the selected career.
        </div>
        """
    )

else:

    for skill in missing:

        safe_skill = html.escape(
            str(skill).title()
        )

        st.html(
            f"""
            <div class="roadmap-step">

                <div style="
                    color:#A95738;
                    font-weight:800;
                    font-size:15px;
                    margin-bottom:5px;
                ">
                    ⚠ {safe_skill}
                </div>

                <div class="small-muted">
                    Required for {safe_career}
                    · Add this skill to your learning roadmap.
                </div>

            </div>
            """
        )