import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>

        /* =========================================================
           PATHFINDER AI — WARM PROFESSIONAL DESIGN
           ========================================================= */

        :root {
            --bg: #F7F3EC;
            --surface: #FFFDF9;
            --surface-2: #F2ECE2;

            --terracotta: #B85F3F;
            --terracotta-dark: #91452D;
            --terracotta-soft: #F3D7CB;

            --sage: #6F8F73;
            --sage-soft: #E5EFE5;

            --gold: #B58A42;
            --gold-soft: #F4EBD7;

            --text: #2F2A25;
            --muted: #71675E;
            --border: #DED3C4;

            --danger: #B85C5C;
            --danger-soft: #F7E3E0;

            --sidebar-bg: #EEE6DA;

            --shadow: 0 8px 24px rgba(92, 70, 52, 0.08);
        }


        /* =========================================================
           GLOBAL
           ========================================================= */

        .stApp {
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        .main {
            background: var(--bg) !important;
        }

        .block-container {
            max-width: 1450px !important;
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }

        body {
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        p {
            color: var(--muted);
        }


        /* =========================================================
           SIDEBAR BASE
           ========================================================= */

        section[data-testid="stSidebar"] {
            background: #EEE6DA !important;
            border-right: 1px solid #DED3C4 !important;
        }

        section[data-testid="stSidebar"] > div {
            background: #EEE6DA !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background: #EEE6DA !important;
            overflow: visible !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 0.35rem !important;
        }


        /* =========================================================
           SIDEBAR BRAND
           ========================================================= */

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 10px;

            padding: 7px 8px 12px 8px;

            margin: 0 4px 8px 4px;

            border-bottom: 1px solid #DDD2C3;
        }

        .sidebar-brand-mark {
            width: 36px;
            height: 36px;

            border-radius: 10px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: #B85F3F;

            color: #FFFFFF !important;

            font-size: 20px;
            font-weight: 800;

            flex-shrink: 0;

            box-shadow:
                0 4px 10px rgba(145, 69, 45, 0.18);
        }

        .sidebar-brand-name {
            font-size: 18px;
            font-weight: 800;

            color: #2F2A25 !important;

            line-height: 1.05;
        }

        .sidebar-brand-name span {
            color: #91452D !important;
        }

        .sidebar-tagline {
            margin-top: 4px;

            font-size: 7.5px;

            font-weight: 750;

            letter-spacing: 0.7px;

            color: #71675E !important;

            line-height: 1.25;
        }


        /* =========================================================
           SIDEBAR NAVIGATION HEADING
           ========================================================= */

        .sidebar-navigation-title {
            margin: 4px 8px 4px 8px;

            color: #91452D !important;

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 1px;

            text-transform: uppercase;
        }


        /* =========================================================
           SIDEBAR PAGE LINKS
           
           DARK TEXT
           NO BOX
           NO BACKGROUND
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] {

            display: flex !important;

            align-items: center !important;

            width: calc(100% - 14px) !important;

            min-height: 31px !important;

            height: 31px !important;

            box-sizing: border-box !important;

            margin: 1px 7px !important;

            padding: 3px 8px !important;

            background: transparent !important;

            background-color: transparent !important;

            color: #2F2A25 !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;

            text-decoration: none !important;

            font-size: 13px !important;

            font-weight: 700 !important;

            line-height: 1.15 !important;

            opacity: 1 !important;
        }


        /* =========================================================
           FORCE DARK COLOR ON EVERYTHING INSIDE SIDEBAR LINK
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] span,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] p,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] div,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] label {

            color: #2F2A25 !important;

            opacity: 1 !important;

            font-size: 13px !important;

            font-weight: 700 !important;
        }


        /* =========================================================
           SIDEBAR ICONS — FORCE DARK
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] svg,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] svg * {

            color: #2F2A25 !important;

            fill: #2F2A25 !important;

            stroke: #2F2A25 !important;

            opacity: 1 !important;

            width: 16px !important;

            height: 16px !important;
        }


        /* =========================================================
           SIDEBAR INNER WRAPPER
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] > div {

            display: flex !important;

            align-items: center !important;

            width: 100% !important;

            min-height: 25px !important;

            height: 25px !important;

            padding: 0 !important;

            margin: 0 !important;

            background: transparent !important;

            background-color: transparent !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;
        }


        /* =========================================================
           SIDEBAR HOVER
           
           STILL NO BOX
           ONLY TEXT + ICON COLOR CHANGES
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover {

            background: transparent !important;

            background-color: transparent !important;

            color: #91452D !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;
        }


        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover span,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover p,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover div,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover label {

            color: #91452D !important;

            opacity: 1 !important;
        }


        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover svg,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover svg * {

            color: #91452D !important;

            fill: #91452D !important;

            stroke: #91452D !important;

            opacity: 1 !important;
        }


        /* =========================================================
           ACTIVE SIDEBAR PAGE
           
           DARK TERRACOTTA TEXT
           NO BOX
           ONLY LEFT LINE
           ========================================================= */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] {

            background: transparent !important;

            background-color: transparent !important;

            color: #91452D !important;

            border: none !important;

            border-left: 3px solid #91452D !important;

            border-radius: 0 !important;

            padding-left: 8px !important;

            font-weight: 800 !important;

            box-shadow: none !important;

            opacity: 1 !important;
        }


        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] span,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] p,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] div,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] label {

            color: #91452D !important;

            font-weight: 800 !important;

            opacity: 1 !important;
        }


        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] svg,

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] svg * {

            color: #91452D !important;

            fill: #91452D !important;

            stroke: #91452D !important;

            opacity: 1 !important;
        }


        /* =========================================================
           AUTOMATIC STREAMLIT NAVIGATION
           ========================================================= */

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] {

            display: flex !important;

            align-items: center !important;

            min-height: 31px !important;

            height: 31px !important;

            box-sizing: border-box !important;

            margin: 1px 7px !important;

            padding: 3px 8px !important;

            background: transparent !important;

            background-color: transparent !important;

            color: #2F2A25 !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;

            font-size: 13px !important;

            font-weight: 700 !important;

            opacity: 1 !important;
        }


        /* Force automatic nav text dark */

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] span,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] p,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] div {

            color: #2F2A25 !important;

            font-weight: 700 !important;

            opacity: 1 !important;
        }


        /* Force automatic nav icons dark */

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] svg,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"] svg * {

            color: #2F2A25 !important;

            fill: #2F2A25 !important;

            stroke: #2F2A25 !important;

            opacity: 1 !important;
        }


        /* Automatic hover */

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover {

            background: transparent !important;

            background-color: transparent !important;

            color: #91452D !important;

            border: none !important;

            border-radius: 0 !important;

            box-shadow: none !important;
        }


        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover span,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover p,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover div {

            color: #91452D !important;
        }


        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover svg,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"]:hover svg * {

            color: #91452D !important;

            fill: #91452D !important;

            stroke: #91452D !important;
        }


        /* Automatic active */

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] {

            background: transparent !important;

            background-color: transparent !important;

            color: #91452D !important;

            border: none !important;

            border-left: 3px solid #91452D !important;

            border-radius: 0 !important;

            font-weight: 800 !important;

            box-shadow: none !important;
        }


        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] span,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] p,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] div {

            color: #91452D !important;

            font-weight: 800 !important;
        }


        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] svg,

        section[data-testid="stSidebar"]
        [data-testid="stNavLink"][aria-current="page"] svg * {

            color: #91452D !important;

            fill: #91452D !important;

            stroke: #91452D !important;
        }


        /* =========================================================
           CURRENT PROFILE
           ========================================================= */

        .sidebar-user {

            margin: 7px 8px 4px 8px;

            padding: 7px 9px;

            border-radius: 8px;

            background: rgba(255, 253, 249, 0.60);

            border: 1px solid #DDD2C3;

            color: #2F2A25;

            font-size: 11px;

            font-weight: 650;

            line-height: 1.25;
        }


        /* =========================================================
           MAIN CONTENT
           ========================================================= */

        .hero {

            position: relative;

            overflow: hidden;

            padding: 34px 38px;

            margin-bottom: 20px;

            border-radius: 22px;

            background:
                linear-gradient(
                    135deg,
                    #C96F4A 0%,
                    #B86241 100%
                );

            color: white;

            box-shadow:
                0 12px 30px rgba(169, 87, 56, 0.18);
        }


        .hero::after {

            content: "";

            position: absolute;

            width: 220px;

            height: 220px;

            right: -70px;

            top: -90px;

            border-radius: 50%;

            background:
                rgba(255, 255, 255, 0.10);
        }


        .hero-label {

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 1.4px;

            opacity: 0.82;

            margin-bottom: 10px;
        }


        .hero h1 {

            margin: 0;

            color: white;

            font-size: 34px;

            line-height: 1.15;

            font-weight: 800;
        }


        .hero p {

            margin-top: 10px;

            margin-bottom: 0;

            color: rgba(255,255,255,0.88);

            font-size: 15px;
        }


        /* =========================================================
           WELCOME BANNER
           ========================================================= */

        .welcome-banner {

            padding: 20px 24px;

            margin-bottom: 22px;

            background: var(--surface);

            border: 1px solid var(--border);

            border-left: 5px solid var(--terracotta);

            border-radius: 14px;

            box-shadow: var(--shadow);
        }


        .welcome-banner h2 {

            margin: 0 0 5px;

            color: var(--text);

            font-size: 18px;

            font-weight: 800;
        }


        .welcome-banner p {

            margin: 0;

            color: var(--muted);

            font-size: 13px;
        }


        .welcome-banner b {

            color: var(--terracotta-dark);
        }


        /* =========================================================
           HEADINGS
           ========================================================= */

        .section-kicker {

            color: var(--terracotta-dark);

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 1.2px;

            text-transform: uppercase;

            margin-bottom: 5px;
        }


        .page-title {

            color: var(--text);

            font-size: 30px;

            font-weight: 800;

            line-height: 1.15;
        }


        .page-subtitle {

            color: var(--muted);

            font-size: 14px;

            margin-top: 7px;

            margin-bottom: 24px;
        }


        .section-title {

            color: var(--text);

            font-size: 19px;

            font-weight: 800;

            margin-top: 28px;

            margin-bottom: 13px;
        }


        /* =========================================================
           CARDS
           ========================================================= */

        .card {

            background: var(--surface);

            border: 1px solid var(--border);

            border-radius: 16px;

            padding: 18px;

            box-shadow: var(--shadow);

            color: var(--text);
        }


        .card:hover {

            border-color: #D7C6B5;
        }


        /* =========================================================
           METRIC
           ========================================================= */

        .metric {

            min-height: 125px;

            background: var(--surface);

            border: 1px solid var(--border);

            border-radius: 16px;

            padding: 18px;

            box-shadow: var(--shadow);
        }


        .metric .label {

            color: var(--muted);

            font-size: 11px;

            font-weight: 700;

            text-transform: uppercase;

            letter-spacing: 0.5px;
        }


        .metric .value {

            margin-top: 8px;

            color: var(--text);

            font-size: 27px;

            font-weight: 800;

            line-height: 1.15;
        }


        .metric .hint {

            margin-top: 8px;

            color: var(--muted);

            font-size: 11px;
        }


        /* =========================================================
           SKILL PILLS
           ========================================================= */

        .pill {

            display: inline-block;

            padding: 6px 10px;

            margin: 3px 4px 3px 0;

            border-radius: 999px;

            font-size: 11px;

            font-weight: 700;
        }


        .pill-neutral {

            background: var(--surface-2);

            color: var(--text);

            border: 1px solid var(--border);
        }


        .pill-strong {

            background: var(--sage-soft);

            color: #4E7154;

            border: 1px solid #C9DCCB;
        }


        .pill-developing {

            background: var(--gold-soft);

            color: #806225;

            border: 1px solid #E5D5AF;
        }


        .pill-missing {

            background: var(--danger-soft);

            color: #985050;

            border: 1px solid #E7C5C0;
        }


        /* =========================================================
           OPPORTUNITIES
           ========================================================= */

        .opp-title {

            color: var(--text);

            font-size: 16px;

            font-weight: 800;

            line-height: 1.25;
        }


        .opp-company {

            color: var(--muted);

            font-size: 12px;

            margin-top: 5px;

            margin-bottom: 7px;
        }


        .match-badge {

            display: inline-block;

            padding: 7px 10px;

            border-radius: 999px;

            background: var(--sage-soft);

            color: #4E7154;

            border: 1px solid #C9DCCB;

            font-size: 11px;

            font-weight: 800;

            text-align: center;
        }


        /* =========================================================
           ROADMAP
           ========================================================= */

        .roadmap-step {

            background: var(--surface);

            border: 1px solid var(--border);

            border-radius: 14px;

            padding: 15px 18px;

            margin-bottom: 10px;

            box-shadow:
                0 4px 14px rgba(92,70,52,0.05);
        }


        .roadmap-number {

            display: inline-flex;

            width: 30px;

            height: 30px;

            align-items: center;

            justify-content: center;

            margin-right: 8px;

            border-radius: 50%;

            background: var(--terracotta-soft);

            color: var(--terracotta-dark);

            font-size: 12px;

            font-weight: 800;
        }


        /* =========================================================
           SUCCESS / INFO
           ========================================================= */

        .success-strip {

            padding: 12px 15px;

            border-radius: 10px;

            background: var(--sage-soft);

            border: 1px solid #C9DCCB;

            color: #4E7154;

            font-size: 13px;

            font-weight: 700;
        }


        .info-strip {

            padding: 13px 15px;

            border-radius: 10px;

            background: var(--gold-soft);

            border: 1px solid #E5D5AF;

            color: #806225;

            font-size: 13px;
        }


        /* =========================================================
           EMPTY STATE
           ========================================================= */

        .empty-state {

            padding: 58px 30px;

            text-align: center;

            background: var(--surface);

            border: 1px dashed #D7C6B5;

            border-radius: 20px;

            box-shadow: var(--shadow);
        }


        .empty-icon {

            font-size: 46px;

            margin-bottom: 10px;
        }


        .empty-state h2 {

            color: var(--text);

            margin: 0;

            font-size: 24px;

            font-weight: 800;
        }


        .empty-state h3 {

            color: var(--text);

            margin: 0;

            font-size: 21px;

            font-weight: 800;
        }


        .empty-state p {

            max-width: 570px;

            margin: 10px auto 20px;

            color: var(--muted);

            font-size: 14px;

            line-height: 1.6;
        }


        /* =========================================================
           PROFILE
           ========================================================= */

        .profile-card {

            background: var(--surface);

            border: 1px solid var(--border);

            border-radius: 16px;

            padding: 20px;

            box-shadow: var(--shadow);
        }


        .small-muted {

            color: var(--muted);

            font-size: 12px;
        }


        /* =========================================================
           STEPPER
           ========================================================= */

        .stepper {

            display: flex;

            align-items: center;

            margin: 18px 0 25px;

            gap: 7px;
        }


        .step {

            padding: 8px 12px;

            border-radius: 999px;

            background: var(--surface-2);

            border: 1px solid var(--border);

            color: var(--muted);

            font-size: 11px;

            font-weight: 700;
        }


        .step.active {

            background: var(--terracotta-soft);

            border-color: #E5B8A6;

            color: var(--terracotta-dark);
        }


        .connector {

            height: 1px;

            flex: 1;

            background: var(--border);
        }


        /* =========================================================
           INPUTS
           ========================================================= */

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div {

            background: var(--surface) !important;

            border-color: var(--border) !important;

            color: var(--text) !important;

            border-radius: 10px !important;
        }


        .stTextInput input:focus,
        .stTextArea textarea:focus {

            border-color: var(--terracotta) !important;

            box-shadow:
                0 0 0 1px var(--terracotta) !important;
        }


        /* =========================================================
           MAIN BUTTONS
           ========================================================= */

        .stButton > button,
        .stButton > button[kind="primary"],
        .stButton > button[kind="secondary"] {

            background: #A95738 !important;

            background-color: #A95738 !important;

            color: #FFFFFF !important;

            border: 1px solid #91452D !important;

            border-radius: 10px !important;

            font-weight: 750 !important;

            min-height: 42px !important;

            box-shadow:
                0 3px 8px rgba(145,69,45,0.18) !important;
        }


        .stButton > button span,
        .stButton > button p,
        .stButton > button div {

            color: #FFFFFF !important;
        }


        .stButton > button:hover,
        .stButton > button[kind="primary"]:hover,
        .stButton > button[kind="secondary"]:hover {

            background: #91452D !important;

            background-color: #91452D !important;

            color: #FFFFFF !important;

            border-color: #783923 !important;
        }


        .stButton > button:hover span,
        .stButton > button:hover p,
        .stButton > button:hover div {

            color: #FFFFFF !important;
        }


        /* =========================================================
           STREAMLIT BASE BUTTONS
           ========================================================= */

        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-secondary"] {

            background: #A95738 !important;

            background-color: #A95738 !important;

            color: #FFFFFF !important;

            border: 1px solid #91452D !important;

            border-radius: 10px !important;

            font-weight: 750 !important;

            min-height: 42px !important;

            box-shadow:
                0 3px 8px rgba(145,69,45,0.18) !important;
        }


        [data-testid="stBaseButton-primary"] *,
        [data-testid="stBaseButton-secondary"] * {

            color: #FFFFFF !important;
        }


        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover {

            background: #91452D !important;

            background-color: #91452D !important;

            color: #FFFFFF !important;

            border-color: #783923 !important;
        }


        [data-testid="stBaseButton-primary"]:hover *,
        [data-testid="stBaseButton-secondary"]:hover * {

            color: #FFFFFF !important;
        }


        /* =========================================================
           LINK BUTTONS
           ========================================================= */

        .stLinkButton > a {

            background: #A95738 !important;

            background-color: #A95738 !important;

            color: #FFFFFF !important;

            border: 1px solid #91452D !important;

            border-radius: 10px !important;

            font-weight: 750 !important;

            min-height: 42px !important;

            text-decoration: none !important;

            box-shadow:
                0 3px 8px rgba(145,69,45,0.18) !important;
        }


        .stLinkButton > a span,
        .stLinkButton > a p,
        .stLinkButton > a div {

            color: #FFFFFF !important;
        }


        .stLinkButton > a:hover {

            background: #91452D !important;

            background-color: #91452D !important;

            color: #FFFFFF !important;

            border-color: #783923 !important;
        }


        .stLinkButton > a:hover span,
        .stLinkButton > a:hover p,
        .stLinkButton > a:hover div {

            color: #FFFFFF !important;
        }


        [data-testid="stBaseButton-link"] {

            background: #A95738 !important;

            background-color: #A95738 !important;

            color: #FFFFFF !important;

            border: 1px solid #91452D !important;

            border-radius: 10px !important;

            font-weight: 750 !important;

            min-height: 42px !important;
        }


        [data-testid="stBaseButton-link"] * {

            color: #FFFFFF !important;
        }


        [data-testid="stBaseButton-link"]:hover {

            background: #91452D !important;

            background-color: #91452D !important;

            color: #FFFFFF !important;

            border-color: #783923 !important;
        }


        [data-testid="stBaseButton-link"]:hover * {

            color: #FFFFFF !important;
        }


        /* =========================================================
           FILE UPLOADER
           ========================================================= */

        [data-testid="stFileUploader"] {

            background: var(--surface) !important;

            border: 1px dashed #D7C6B5 !important;

            border-radius: 14px !important;

            padding: 10px !important;
        }


        [data-testid="stFileUploaderDropzone"] {

            background: var(--surface) !important;
        }


        /* =========================================================
           PROGRESS
           ========================================================= */

        .stProgress > div > div > div > div {

            background: var(--terracotta) !important;
        }


        /* =========================================================
           CHECKBOX / RADIO
           ========================================================= */

        input[type="checkbox"]:checked {

            accent-color: var(--terracotta) !important;
        }


        input[type="radio"]:checked {

            accent-color: var(--terracotta) !important;
        }


        /* =========================================================
           STREAMLIT METRIC
           ========================================================= */

        [data-testid="stMetric"] {

            background: var(--surface) !important;

            border: 1px solid var(--border) !important;

            border-radius: 14px !important;

            padding: 14px !important;

            box-shadow: var(--shadow) !important;
        }


        [data-testid="stMetricLabel"] {

            color: var(--muted) !important;
        }


        [data-testid="stMetricValue"] {

            color: var(--text) !important;
        }


        /* =========================================================
           CAPTION
           ========================================================= */

        .stCaption {

            color: var(--muted) !important;
        }


        /* =========================================================
           HIDE STREAMLIT DECORATION
           ========================================================= */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }


        /* =========================================================
           SIDEBAR HEIGHT
           ========================================================= */

        @media (min-height: 650px) {

            section[data-testid="stSidebar"] {
                overflow: hidden !important;
            }

            section[data-testid="stSidebar"] > div {
                overflow: hidden !important;
            }

            section[data-testid="stSidebar"]
            [data-testid="stSidebarContent"] {
                overflow: hidden !important;
            }
        }


        /* =========================================================
           RESPONSIVE
           ========================================================= */

        @media (max-width: 900px) {

            .block-container {

                padding-left: 1rem !important;

                padding-right: 1rem !important;
            }


            .hero {

                padding: 25px;
            }


            .hero h1 {

                font-size: 27px;
            }


            .stepper {

                flex-wrap: wrap;
            }


            .connector {

                display: none;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )