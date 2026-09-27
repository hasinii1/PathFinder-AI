import html
import streamlit as st


def _safe(value):
    return html.escape(str(value))


def metric_card(label, value, hint=""):
    st.html(
        f"""
        <div class="metric">
            <div class="label">
                {_safe(label)}
            </div>

            <div class="value">
                {_safe(value)}
            </div>

            <div class="hint">
                {_safe(hint)}
            </div>
        </div>
        """
    )


def skill_pills(skills, kind="neutral"):
    classes = {
        "strong": "pill-strong",
        "developing": "pill-developing",
        "missing": "pill-missing",
    }

    css_class = classes.get(
        kind,
        "pill-neutral",
    )

    if not skills:
        st.caption("None yet")
        return

    pills = ""

    for skill in skills:
        safe_skill = _safe(
            str(skill).strip().title()
        )

        pills += (
            f'<span class="pill {css_class}">'
            f'{safe_skill}'
            f'</span>'
        )

    st.html(pills)


def opportunity_card(opp, key=None):
    title = opp.get(
        "title",
        "Opportunity",
    )

    company = opp.get(
        "company",
        "Company",
    )

    location = opp.get(
        "location",
        "Location not specified",
    )

    job_type = opp.get(
        "job_type",
        "Role",
    )

    match = opp.get(
        "match_percentage",
        0,
    )

    matched = opp.get(
        "matched_skills",
        [],
    ) or []

    missing = opp.get(
        "missing_skills",
        [],
    ) or []

    url = opp.get(
        "url",
        "",
    )

    left, right = st.columns(
        [5, 1]
    )

    with left:

        st.html(
            f"""
            <div class="opp-title">
                {_safe(title)}
            </div>

            <div class="opp-company">
                {_safe(company)}
                ·
                {_safe(location)}
                ·
                {_safe(job_type)}
            </div>
            """
        )

        if matched:
            matched_text = ", ".join(
                str(x).title()
                for x in matched[:5]
            )

            st.caption(
                "Matched: "
                + matched_text
            )

        if missing:
            missing_text = ", ".join(
                str(x).title()
                for x in missing[:4]
            )

            st.caption(
                "To improve: "
                + missing_text
            )

    with right:

        st.html(
            f"""
            <div class="match-badge">
                {_safe(match)}% match
            </div>
            """
        )

        if url:
            st.link_button(
                "View Details",
                url,
                use_container_width=True,
            )

    st.html(
        '<div style="height:8px"></div>'
    )