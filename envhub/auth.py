# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
from pathlib import Path

import typer
from supabase import create_client, Client

SUPABASE_URL = "https://otzukwvudeucxbrrnhvx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90enVrd3Z1ZGV1Y3hicnJuaHZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1Nzc3OTQsImV4cCI6MjA2NjE1Mzc5NH0.jiqXBBOLS_KZGUtLvP90Tr4dCAEQXaqg_nZO_rH4Ty8"
SESSION_PATH = Path.home() / ".EnvHub" / ".supacli_session.json"


def _save_session(data: dict):
    """
    Saves the given session data to disk.

    The data is written to the file specified by `SESSION_PATH`.

    Args:
        data (dict): The session data to save.
    """
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_PATH, "w") as f:
        json.dump(data, f)


def is_logged_in() -> bool:
    """
    Checks if the user is currently logged in.

    This will load the session data from the file specified by `SESSION_PATH` and
    check if it exists and is not empty. If the file does not exist or is empty,
    the function will return `False`.

    Returns:
        bool: `True` if a session exists and is not empty, `False` otherwise.
    """
    session = _load_session()
    return session is not None


def _load_session() -> dict | None:
    """
    Loads the session data from the file specified by `SESSION_PATH`.

    If the file does not exist or is empty, the function will return `None`.

    If the file exists but is not a valid JSON file, a `JSONDecodeError` will be
    raised, and the function will return `None`. Additionally, the file will
    be removed to prevent further attempts at loading it.

    Args:
        None

    Returns:
        dict | None: The loaded session data, or `None` if the file does not
            exist or is not a valid JSON file.
    """
    if SESSION_PATH.exists():
        with open(SESSION_PATH) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                _clear_session()
                return None
    return None


def _clear_session():
    """
    Clears the session data by deleting the file specified by `SESSION_PATH`.

    Returns:
        None
    """
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()


def login(email: str, password: str) -> bool:
    """
    Logs into the Supabase account with the given email and password.

    Args:
        email (str): The email address to log in with.
        password (str): The password to log in with.

    Returns:
        bool: True if the login was successful, False if it failed.

    Raises:
        Exception: If there was an error during the login operation.
    """
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            _save_session({
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
                "email": res.user.email
            })
            return True
    except Exception as e:
        typer.secho(f"Login failed: {str(e)}", fg=typer.colors.RED)
    return False


def logout():
    """
    Logs out the user by clearing the session data from disk.

    This is the inverse of the `login` function. It will remove the session data
    from the file specified by `SESSION_PATH`, effectively logging the user out.

    Returns:
        None
    """
    _clear_session()


def get_logged_in_email() -> str | None:
    """
    Returns the email address of the currently logged in user.

    This function will load the session data from the file specified by
    `SESSION_PATH` and return the value of the `"email"` key. If the file does
    not exist or is not a valid JSON file, the function will return `None`.

    Returns:
        str | None: The email address of the currently logged in user, or `None`
            if no session exists or the session is invalid.
    """
    session = _load_session()
    return session.get("email") if session else None


def get_authenticated_client() -> Client | None:
    """
    Returns a Supabase client with a valid session.
    If access_token is expired, refreshes the session automatically.
    """
    session_data = _load_session()
    if not session_data:
        typer.secho("Not logged in. Please login first using the 'login' command.", fg=typer.colors.RED)
        exit(1)

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        client.auth.set_session(session_data["access_token"], session_data["refresh_token"])

        try:
            refreshed = client.auth.refresh_session(session_data["refresh_token"])
            if refreshed.session:
                _save_session({
                    "access_token": refreshed.session.access_token,
                    "refresh_token": refreshed.session.refresh_token,
                    "email": refreshed.user.email
                })

                client.auth.set_session(refreshed.session.access_token, refreshed.session.refresh_token)
        except Exception as refresh_error:
            user = client.auth.get_user()
            if not user:
                raise refresh_error

        return client
    except Exception as e:
        if "Invalid Refresh Token" in str(e):
            _clear_session()
            typer.secho("Session expired. Please login again.", fg=typer.colors.RED)
            exit(1)
        else:
            typer.secho(f"Authentication error: {str(e)}", fg=typer.colors.RED)
        return None
