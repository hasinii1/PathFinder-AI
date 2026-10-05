import streamlit as st

from components.styles import apply_styles
from utils.supabase_client import (
    is_supabase_configured,
    set_current_user,
    sign_in,
    sign_up,
)

st.set_page_config(
    page_title="Login | PathFinder AI",
    page_icon="🧭",
    layout="wide",
)

apply_styles()

st.html(
    """
    <div class="hero">
        <div class="hero-label">PATHFINDER AI</div>
        <h1>Welcome to PathFinder AI 🧭</h1>
        <p>
            Sign in to access your personalized student growth,
            skill and career guidance journey.
        </p>
    </div>
    """
)

if not is_supabase_configured():
    st.html(
        """
        <div class="empty-state">
            <div class="empty-icon">🔐</div>
            <h2>Supabase is not configured</h2>
            <p>
                Add SUPABASE_URL and SUPABASE_KEY to your local .env
                file or your Render environment variables, then restart
                the application.
            </p>
        </div>
        """
    )
    st.stop()

login_tab, signup_tab = st.tabs(["Login", "Create Account"])

with login_tab:
    st.subheader("Login")

    email = st.text_input(
        "Email",
        key="login_email",
    )
    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
    )

    if st.button(
        "Login",
        type="primary",
        use_container_width=True,
    ):
        if not email.strip() or not password:
            st.warning("Please enter your email and password.")
        else:
            with st.spinner("Signing you in..."):
                user, error = sign_in(email, password)

            if error:
                st.error(error)
            elif user is not None:
                set_current_user(user)
                st.success("Login successful.")
                st.rerun()

with signup_tab:
    st.subheader("Create Account")

    full_name = st.text_input(
        "Full Name",
        key="signup_name",
    )
    signup_email = st.text_input(
        "Email",
        key="signup_email",
    )
    signup_password = st.text_input(
        "Password",
        type="password",
        key="signup_password",
    )
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="signup_confirm_password",
    )

    if st.button(
        "Create Account",
        type="primary",
        use_container_width=True,
    ):
        if not full_name.strip() or not signup_email.strip():
            st.warning("Please enter your name and email.")
        elif len(signup_password) < 6:
            st.warning("Password must contain at least 6 characters.")
        elif signup_password != confirm_password:
            st.warning("Passwords do not match.")
        else:
            with st.spinner("Creating your account..."):
                user, error = sign_up(
                    signup_email,
                    signup_password,
                    full_name,
                )

            if error:
                st.error(error)
            elif user is not None:
                if getattr(user, "identities", None) is None:
                    st.error("An account with this email may already exist.")
                elif getattr(user, "confirmed_at", None) is None:
                    st.success(
                        "Account created. Please check your email to confirm "
                        "your account, then log in."
                    )
                else:
                    set_current_user(user)
                    st.success("Account created successfully.")
                    st.rerun()
