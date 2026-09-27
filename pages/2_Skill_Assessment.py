import html
import streamlit as st

from components.styles import apply_styles
from utils.data_loader import get_assessment


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
    <div class="section-kicker">STEP 2</div>
    <div class="page-title">Skill Assessment</div>
    <div class="page-subtitle">
        Your current skill levels based on evidence found in your
        resume, projects, internships and certifications.
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
            <div class="empty-icon">📊</div>
            <h3>Skill Assessment Not Available Yet</h3>
            <p class="small-muted">
                Upload and analyze your resume from
                <b>Profile Analysis</b> first.
                Your skill assessment will be generated from
                the resume you provide.
            </p>
        </div>
        """
    )

    st.stop()


# ---------------------------------------------------------
# LOAD ASSESSMENT ONLY AFTER RESUME IS PROCESSED
# ---------------------------------------------------------
data = get_assessment()

assessment = data.get("skill_assessment", {})
overall = data.get("overall_score", 0)


# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Overall Skill Score",
        f"{float(overall):.2f}%"
    )

with c2:
    st.metric(
        "Skills Assessed",
        len(assessment)
    )

with c3:
    st.metric(
        "Evidence Sources",
        "Resume + Projects"
    )


# ---------------------------------------------------------
# CURRENT SKILL LEVELS
# ---------------------------------------------------------
st.html(
    """
    <div class="section-title">
        Current Skill Levels
    </div>
    """
)


if not assessment:

    st.html(
        """
        <div class="empty-state">
            <div class="empty-icon">🧩</div>
            <h3>No Skills Detected</h3>
            <p class="small-muted">
                No skills were found in the analyzed profile yet.
            </p>
        </div>
        """
    )

else:

    # Sort skills from highest score to lowest score
    sorted_skills = sorted(
        assessment.items(),
        key=lambda x: float(x[1].get("score", 0)),
        reverse=True
    )

    for skill, details in sorted_skills:

        score = float(details.get("score", 0))
        level = details.get("level", "Developing")

        safe_skill = html.escape(str(skill).title())
        safe_level = html.escape(str(level))

        st.html(
            f"""
            <div style="
                background:#FFFDF9;
                border:1px solid #E3D9CA;
                border-radius:14px;
                padding:14px 16px;
                margin:8px 0;
            ">
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:15px;
                    margin-bottom:8px;
                ">
                    <div>
                        <span style="
                            color:#2F2A25;
                            font-weight:800;
                            font-size:14px;
                        ">
                            {safe_skill}
                        </span>

                        <span style="
                            color:#756D63;
                            font-size:12px;
                            margin-left:8px;
                        ">
                            · {safe_level}
                        </span>
                    </div>

                    <div style="
                        color:#A95738;
                        font-weight:800;
                        font-size:13px;
                    ">
                        {score:.0f}%
                    </div>
                </div>

                <div style="
                    height:8px;
                    background:#EAE1D3;
                    border-radius:999px;
                    overflow:hidden;
                ">
                    <div style="
                        width:{max(0, min(100, score))}%;
                        height:100%;
                        background:#6F8F73;
                        border-radius:999px;
                    "></div>
                </div>
            </div>
            """
        )