# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import importlib.metadata
import json

import requests
import typer
from packaging import version

from envhub import auth, reset
from envhub import clone
from envhub.add import add
from envhub.decrypt import decrypt_runtime_and_run_command
from envhub.pull import pull
from envhub.services.getCurrentEnvVariables import get_current_env_variables
from envhub.utils.crypto import CryptoUtils
from envhub.utils.getEncryptedPasswordData import get_encrypted_password_data
from envhub.utils.getPassword import get_password
from envhub.utils.getProjectId import get_project_id
from envhub.utils.getRole import get_role

__version__ = importlib.metadata.version("envhub-cli")

app = typer.Typer()


def check_for_updates():
    """Check if a newer version is available on PyPI."""
    try:
        current_version = importlib.metadata.version("envhub-cli")
        response = requests.get("https://pypi.org/pypi/envhub-cli/json", timeout=3)
        latest_version = response.json()["info"]["version"]

        if version.parse(latest_version) > version.parse(current_version):
            typer.secho(
                f"\n⚠️  A new version of EnvHub is available: {current_version} → {latest_version}"
                f"\n   Upgrade with: pip install --upgrade envhub-cli\n",
                fg=typer.colors.YELLOW,
            )
    except Exception:
        pass


def version_callback(value: bool):
    if value:
        typer.echo(f"EnvHub CLI v{__version__}")
        check_for_updates()
        raise typer.Exit()


@app.callback()
def main(
        version: bool = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        )
):
    """EnvHub CLI - Manage your environment variables securely."""
    check_for_updates()
    pass


@app.command("login")
def login():
    """
    Logs into the application using provided email and password.

    This function checks if the user is already logged in. If the user is already
    logged in, a message is displayed, and the function exits. If the user is not
    logged in, they will be prompted to provide their email and password. Successful
    authentication results in a success message; otherwise, an error message is shown.

    :return: None
    """
    if auth.is_logged_in():
        typer.secho(f"Already logged in as {auth.get_logged_in_email()}", fg=typer.colors.YELLOW)
        typer.echo("Use `logout` to log out")
        return

    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)

    if auth.login(email, password):
        typer.secho("Logged in successfully", fg=typer.colors.GREEN)
    else:
        typer.secho("Login failed", fg=typer.colors.RED)


@app.command("logout")
def logout():
    """
    Logs the user out of the application.

    This function triggers the logout mechanism provided by the `auth` module and
    notifies the user of successful logout via a console message. It utilizes
    Typer for displaying messages with enhanced console styling.

    :return: None
    """
    auth.logout()
    typer.secho("Logged out successfully", fg=typer.colors.GREEN)


@app.command("whoami")
def whoami():
    """
    Provides a command to display the currently logged-in user's email or
    a message indicating that the user is not logged in when no email is
    retrieved.

    :return: None
    """
    email = auth.get_logged_in_email()
    if email:
        typer.secho(f"Logged in as: {email}", fg=typer.colors.CYAN)
    else:
        typer.secho("You are not logged in", fg=typer.colors.RED)


@app.command("clone")
def clone_project(project_name: str):
    """
    Clones the specified project using the given project name.

    This function utilizes asynchronous operations to clone a project
    by calling the clone module's `clone` function. It takes a project
    name as input and handles the process asynchronously.

    :param project_name: The name of the project to be cloned.
    :type project_name: str
    :return: None
    """
    asyncio.run(clone.clone(project_name))


@app.command("reset")
def reset_folder():
    """
    Resets the current folder by invoking the reset functionality.

    This command is used to perform a reset operation in the current folder.
    It makes use of the `reset` module to initialize or restore the folder
    to its default state.

    :return: None
    """
    reset.reset()


@app.command("decrypt")
def decrypt_command(command: list[str] = typer.Argument(..., help="Command to run with decrypted environment")):
    """
    Decrypts the runtime environment and executes the specified command.

    This command enables the execution of another command in a runtime
    environment with decrypted settings. Users are required to specify
    the command as a list of strings, which will be concatenated into
    a single executable command string.

    :param command: The command to be executed with the decrypted
        environment as a list of strings.
    :type command: list[str]
    :return: None
    """
    command_str = " ".join(command)
    decrypt_runtime_and_run_command(command_str)


@app.command("add")
def add_env_var():
    """
    Adds a new environment variable to the configuration file and sends it to the corresponding
    remote environment management system. Prompts the user for both the variable name and its value
    and securely handles hiding the input for sensitive information. Leverages functionalities to
    interact with the system's `.envhub` file and performs asynchronous operations for communication.
    """
    env_name = typer.prompt("Enter the variable name")
    env_value = typer.prompt("Enter the variable value", hide_input=True)
    with open(".envhub", "r") as f:
        json_config = json.load(f)
    try:
        asyncio.run(add([env_name, env_value],
                        json_config.get("password"),
                        json_config.get("role"),
                        json_config.get("project_id")
                        )
                    )
    except Exception as e:
        typer.secho(f"Error adding environment variable: {e}", fg=typer.colors.RED)

    typer.secho("Environment variable added successfully", fg=typer.colors.GREEN)


@app.command("pull")
def pull_env_vars():
    """
    Pulls environment variables from a predefined source.

    This function triggers the `pull` functionality that retrieves environment
    variables from the designated source or service. It is typically used to
    sync environment variables for the application configuration.

    :return: None
    """
    pull()


@app.command("list")
def list_env_vars():
    """
    List and decrypt environment variables associated with the current project.

    This function interacts with encrypted environment variables stored in the project and decrypts
    them based on the user's role: `owner`, `user`, or `admin`. It utilizes cryptographic utilities
    to access and decrypt the respective variables. The decrypted environment variables are then
    printed to the terminal in the format `ENV_NAME=decrypted_value`.

    :returns: None

    """
    crypto_utils = CryptoUtils()
    client = auth.get_authenticated_client()
    envs = get_current_env_variables(client, get_project_id())
    role = get_role()
    if role == "owner":
        for env in envs:
            typer.echo(f"{env['env_name']}={
            crypto_utils.decrypt({
                "ciphertext": env['env_value_encrypted'],
                "nonce": env['nonce'],
                "tag": env['tag'],
                "salt": env['salt']
            },
                get_password()
            )
            }"
                       )

    elif role == "user" or role == "admin":
        for env in envs:
            typer.echo(f"{env['env_name']}={
            crypto_utils.decrypt({
                "ciphertext": env['env_value_encrypted'],
                "nonce": env['nonce'],
                "tag": env['tag'],
                "salt": env['salt']
            },
                crypto_utils.decrypt(
                    get_encrypted_password_data(),
                    get_password()
                )
            )
            }"
                       )


if __name__ == "__main__":
    app()
