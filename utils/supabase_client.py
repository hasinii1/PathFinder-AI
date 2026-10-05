"""Supabase authentication and database helpers for PathFinder AI."""

import os

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def _credentials():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    return url, key


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client | None:
    """Create one reusable Supabase client for the Streamlit app."""
    url, key = _credentials()

    if not url or not key:
        return None

    return create_client(url, key)


def is_supabase_configured():
    url, key = _credentials()
    return bool(url and key)


def sign_up(email, password, full_name):
    client = get_supabase()
    if client is None:
        return None, "Supabase is not configured."

    try:
        response = client.auth.sign_up(
            {
                "email": email.strip(),
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name.strip(),
                    }
                },
            }
        )

        user = response.user

        if user is not None:
            _save_profile(user, full_name)

        return user, None

    except Exception as error:
        return None, str(error)


def sign_in(email, password):
    client = get_supabase()
    if client is None:
        return None, "Supabase is not configured."

    try:
        response = client.auth.sign_in_with_password(
            {
                "email": email.strip(),
                "password": password,
            }
        )

        user = response.user

        if user is not None:
            _save_profile(
                user,
                (user.user_metadata or {}).get("full_name", ""),
            )

        return user, None

    except Exception as error:
        return None, str(error)


def _save_profile(user, full_name=""):
    """Create/update the basic application profile for an auth user."""
    client = get_supabase()
    if client is None or user is None:
        return

    try:
        metadata = user.user_metadata or {}
        name = (
            str(full_name or metadata.get("full_name", "")).strip()
            or "Student"
        )

        client.table("profiles").upsert(
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": name,
            },
            on_conflict="id",
        ).execute()
    except Exception:
        # Authentication should still work if the profile table has not
        # been created yet. The SQL schema is provided separately.
        pass


def set_current_user(user):
    st.session_state["auth_user"] = user
    st.session_state["authenticated"] = user is not None


def get_current_user():
    return st.session_state.get("auth_user")


def sign_out():
    client = get_supabase()

    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    for key in [
        "auth_user",
        "authenticated",
        "resume_processed",
        "profile_created",
        "resume_text",
        "resume_filename",
        "resume_file_signature",
        "selected_target_career",
        "career_agent_question",
        "career_agent_response",
    ]:
        st.session_state.pop(key, None)
