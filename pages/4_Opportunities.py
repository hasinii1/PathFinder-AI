import html
import streamlit as st

from components.styles import apply_styles
from components.cards import opportunity_card
from utils.data_loader import get_opportunities, get_skill_gap


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
    <div class="section-kicker">STEP 4</div>

    <div class="page-title">
        Opportunity Matching
    </div>

    <div class="page-subtitle">
        Live opportunities ranked using career relevance,
        job skill coverage and your current skills.
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
            <div class="empty-icon">🎯</div>

            <h3>Opportunity Matching Not Available Yet</h3>

            <p class="small-muted">
                Upload and analyze your resume from
                <b>Profile Analysis</b> first.
                Opportunities will then be matched using
                your current skills and selected career.
            </p>
        </div>
        """
    )

    st.stop()


# ---------------------------------------------------------
# LOAD DATA ONLY AFTER RESUME IS PROCESSED
# ---------------------------------------------------------
opps = get_opportunities()

skill_gap_data = get_skill_gap()

career = skill_gap_data.get(
    "skill_gap_analysis",
    {}
).get(
    "target_career",
    "Your Career"
)


# ---------------------------------------------------------
# CALCULATE HIGHEST MATCH
# ---------------------------------------------------------
match_values = []

for opportunity in opps:

    try:
        match = float(
            opportunity.get(
                "match_percentage",
                0
            )
        )
    except Exception:
        match = 0

    match_values.append(match)


highest_match = max(
    match_values,
    default=0
)


# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------
c1, c2, c3 = st.columns(3)


with c1:
    st.metric(
        "Matched Opportunities",
        len(opps)
    )


with c2:
    st.metric(
        "Target Career",
        career
    )


with c3:
    st.metric(
        "Highest Match",
        f"{highest_match:.0f}%"
    )


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
q = st.text_input(
    "Search opportunities",
    placeholder="Search title, company or location"
)


minimum = st.slider(
    "Minimum match percentage",
    0,
    100,
    30,
    5
)


# ---------------------------------------------------------
# FILTER OPPORTUNITIES
# ---------------------------------------------------------
filtered = []


for opportunity in opps:

    searchable_text = " ".join(
        str(
            opportunity.get(
                key,
                ""
            )
        )
        for key in [
            "title",
            "company",
            "location"
        ]
    ).lower()

    try:
        match = float(
            opportunity.get(
                "match_percentage",
                0
            )
        )
    except Exception:
        match = 0

    search_matches = (
        not q
        or q.lower() in searchable_text
    )

    percentage_matches = (
        match >= minimum
    )

    if (
        percentage_matches
        and search_matches
    ):
        filtered.append(opportunity)


# ---------------------------------------------------------
# RESULT COUNT
# ---------------------------------------------------------
st.caption(
    f"Showing {len(filtered)} opportunities"
)


# ---------------------------------------------------------
# DISPLAY OPPORTUNITIES
# ---------------------------------------------------------
if filtered:

    for i, opportunity in enumerate(
        filtered[:30]
    ):

        opportunity_card(
            opportunity,
            key=f"opp_{i}"
        )

else:

    st.html(
        """
        <div class="empty-state">
            <div class="empty-icon">🔎</div>

            <h3>No Opportunities Found</h3>

            <p class="small-muted">
                No opportunities match your current filters.
                Try lowering the minimum match percentage
                or changing your search.
            </p>
        </div>
        """
    )