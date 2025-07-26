# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import typer

from envhub.decrypt_prod_by_api_key import decrypt_prod_by_api_key

app = typer.Typer(help="EnvHub CLI - Manage your environment variables securely.")


def check_for_updates_async():
    """Check for updates in a non-blocking way."""

    def _check():
        try:
            import requests
            from packaging import version
            import importlib.metadata

            current_version = importlib.metadata.version("envhub-cli")
            response = requests.get("https://pypi.org/pypi/envhub-cli/json", timeout=3)
            latest_version = response.json()["info"]["version"]

            if version.parse(latest_version) > version.parse(current_version):
                typer.secho(
                    f"\n⚠️  A new version of EnvHub is available: {current_version} → {latest_version}"
                    f"\n   Upgrade with: pip install --upgrade envhub-cli\n   Or if using pipx: pipx upgrade envhub-cli\n\n",
                    fg=typer.colors.YELLOW,
                )
        except Exception:
            pass

    # This will run the function _check in a separate thread so that the main thread can continue and won't result
    # in a slow startup
    import threading

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def version_callback(value: bool):
    """
    Determines and displays the version of the EnvHub CLI tool when the input
    value is True. If an error occurs during version retrieval, it gracefully
    handles specific exceptions or defaults to a generic message. Exits the
    process after displaying the version if appropriate.

    :param value: The boolean flag to trigger the version display logic. If True,
        the function attempts to retrieve and print the version of the EnvHub CLI.
    :return: The input value, maintaining the original state.

    :raises typer.Exit: Exits the process after displaying the version information
        when the given value is True.
    """
    import importlib.metadata

    if value:
        try:
            __version__ = importlib.metadata.version("envhub-cli")
            typer.echo(f"EnvHub CLI v{__version__}")

            try:
                import requests
                from packaging import version
                current_version = __version__
                response = requests.get("https://pypi.org/pypi/envhub-cli/json", timeout=3)
                latest_version = response.json()["info"]["version"]

                if version.parse(latest_version) > version.parse(current_version):
                    typer.secho(
                        f"\n⚠️  A new version of EnvHub is available: {current_version} → {latest_version}"
                        f"\n   Upgrade with: pip install --upgrade envhub-cli\n   Or if using pipx: pipx upgrade envhub-cli\n\n",
                        fg=typer.colors.YELLOW,
                    )
            except Exception:
                pass
            raise typer.Exit()
        except importlib.metadata.PackageNotFoundError:
            typer.echo("Version information not available. Package may not be installed.")
            raise typer.Exit(code=1)
    return value


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
    """
    The main function serves as the entry point for the CLI application. It determines if the
    version flag is provided by the user and displays the application version if requested.
    If the version flag is not provided, the function triggers an asynchronous check for updates,
    ensuring that update checks only occur during active CLI commands.

    :param version: A boolean flag that, when set, triggers the display of the application
        version and prevents further execution of the program logic.
    :callback version: Calls the `version_callback` function to handle the version flag.
    :return: None
    """
    if not version:
        check_for_updates_async()


@app.command("login")
def login():
    """
    Logs the user into the system.

    This function interacts with the authentication module to allow the user
    to log in through the CLI. If the user is already logged in, this function
    notifies them of their current status and provides guidance on how to log out.
    When a non-logged-in user attempts to log in, they are prompted for their email
    and password. If the credentials are valid, the login is completed
    successfully, with appropriate feedback shown for success or failure. Special
    instructions are presented for users who signed up using Google sign-in.

    :raises typer.Abort: Raised if prompted inputs are interrupted.
    """
    from envhub import auth

    if auth.is_logged_in():
        typer.secho(f"Already logged in as {auth.get_logged_in_email()}", fg=typer.colors.YELLOW)
        typer.echo("Use `logout` to log out")
        return

    typer.secho("Note: If you signed up with Google, you'll need to set up a CLI password first. "
                "To do this, go to EnvHub (https://envhub.net), click on your profile picture, "
                "then select 'CLI Setup' from the dropdown menu.",
                fg=typer.colors.YELLOW)

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
    from envhub import auth

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
    from envhub import auth

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
    import asyncio
    from envhub import clone

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
    from envhub import reset

    reset.reset()


@app.command("decrypt")
def decrypt_command(
        command: list[str] = typer.Argument(None, help="Optional command to run with decrypted environment")):
    """
    Decrypts configurations and either executes a provided command within a decrypted environment
    or securely decrypts configurations without running additional commands.

    :param command: A list of strings representing an optional command to execute within a decrypted
        runtime environment using the configurations. If no command is provided, only decryption
        and storage will be performed.
    """
    from envhub.decrypt import decrypt_runtime_and_run_command
    from envhub.decrypt_and_store import decrypt_and_store

    if command:
        command_str = " ".join(command)
        decrypt_runtime_and_run_command(command_str)
    else:
        decrypt_and_store()


@app.command("add")
def add_env_var():
    """
    Adds a new environment variable to the configuration file and sends it to the corresponding
    remote environment management system. Prompts the user for both the variable name and its value
    and securely handles hiding the input for sensitive information. Leverages functionalities to
    interact with the system's `.envhub` file and performs asynchronous operations for communication.
    """
    import json
    import asyncio
    from envhub.add import add

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
    from envhub.pull import pull

    pull()


@app.command("list")
def list_env_vars():
    """
    Lists environment variables stored in the `.env` file after decrypting it using the
    `.envhub` configuration file. The decryption process depends on the `role` specified
    within the `.envhub` file, which determines how the decryption keys are handled.

    If the `.envhub` configuration file does not exist or is invalid, an appropriate
    error message will be displayed. The method exits with an error code in case of any
    failures.

    :param: None

    :raises json.JSONDecodeError: If the `.envhub` configuration file contains invalid JSON data.
    :raises Exception: For any other errors encountered during the reading, decryption, or
        listing process, a general exception is raised, and an error message is displayed.

    :return: None
    """
    import pathlib
    import json
    from envhub.utils.crypto import CryptoUtils

    env_file = pathlib.Path.cwd() / ".env"
    envhub_config_file = pathlib.Path.cwd() / ".envhub"

    if not envhub_config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    try:
        with open(envhub_config_file, "r") as f:
            config_data = json.load(f)
            password = config_data.get("password")
            role = config_data.get("role")
            crypto_utils = CryptoUtils()

            if role == "owner":
                decrypted_env = crypto_utils.decrypt_env_file(str(env_file), password)
            elif role in ("user", "admin"):
                decrypted_env = crypto_utils.decrypt_env_file(
                    str(env_file),
                    crypto_utils.decrypt(config_data.get("encrypted_data"), password)
                )
            else:
                typer.secho(f"Unknown role: {role}", fg="red")
                exit(1)

            for key, value in decrypted_env.items():
                typer.echo(f"{key}={value}")

    except json.JSONDecodeError:
        typer.secho("Invalid .envhub config file.", fg=typer.colors.RED)
        exit(1)
    except Exception as e:
        typer.secho(f"Error listing environment variables: {str(e)}", fg=typer.colors.RED)
        exit(1)


@app.command("decrypt-prod")
def decrypt_prod(command: list[str] = typer.Argument(None, help="Optional command to run with decrypted environment")):
    """
    Decrypts the production environment by using the provided command or default behavior.

    This function is a command registered with Typer to decrypt the production environment.
    If a command is provided, it will execute the command within the decrypted environment.
    If no command is provided, the function will simply perform the decryption process.

    :param command: List of command arguments to execute after decrypting the environment.
    :type command: list[str]
    :return: None
    """

    if command:
        command_str = " ".join(command)
        decrypt_prod_by_api_key(command=command_str)
    else:
        decrypt_prod_by_api_key()


if __name__ == "__main__":
    app()
