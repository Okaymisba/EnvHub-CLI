import json
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SESSION_PATH = Path.home() / ".EnvHub" / ".supacli_session.json"


def _save_session(data: dict):
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_PATH, "w") as f:
        json.dump(data, f)


def is_logged_in() -> bool:
    session = _load_session()
    return session is not None


def _load_session() -> dict | None:
    if SESSION_PATH.exists():
        with open(SESSION_PATH) as f:
            return json.load(f)
    return None


def _clear_session():
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()


def login(email: str, password: str) -> bool:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = client.auth.sign_in_with_password({"email": email, "password": password})
    if res.session:
        _save_session({
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "email": res.user.email
        })
        return True
    return False


def logout():
    _clear_session()


def get_logged_in_email() -> str | None:
    session = _load_session()
    return session.get("email") if session else None


def get_authenticated_client() -> Client | None:
    """
    Returns a Supabase client with a valid session.
    If access_token is expired, refreshes the session automatically.
    """
    session_data = _load_session()
    if not session_data:
        return None

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Try setting the session
    client.auth.set_session(client, session_data["access_token"], session_data["refresh_token"])

    # Try an authenticated call to see if token is still valid
    try:
        user = client.auth.get_user()
        if not user:
            # Refresh if token is invalid/expired
            refreshed = client.auth.refresh_session(session_data["refresh_token"])
            if refreshed.session:
                # Save new tokens
                _save_session({
                    "access_token": refreshed.session.access_token,
                    "refresh_token": refreshed.session.refresh_token,
                    "email": refreshed.user.email
                })
                client.auth.set_session(refreshed.session.access_token, refreshed.session.refresh_token)
    except Exception as e:
        print("⚠️ Failed to refresh session:", e)
        return None

    return client
