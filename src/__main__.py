import asyncio
import json

import typer

from src import auth, reset
from src import clone
from src.add import add
from src.decrypt import decrypt_runtime_and_run_command
from src.pull import pull

app = typer.Typer()


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


if __name__ == "__main__":
    app()
