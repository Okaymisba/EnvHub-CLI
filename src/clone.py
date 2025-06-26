import json
import pathlib

import typer
from typer import style

from src.auth import get_authenticated_client
from src.services.getCurrentEnvVariables import get_current_env_variables
from src.services.getCurrentUserRole import get_current_user_role


async def clone(project_nam: str):
    """
    Clones a project and initializes local environment files required for the
    project.

    This function performs the following steps:
    1. Checks if the provided project name is valid.
    2. Authenticates the client for further operations.
    3. Ensures the current folder is not already initialized with another project.
    4. Retrieves environment variables and user role associated with the project.
    5. Creates the `.envhub` configuration file with project details.
    6. Creates or updates the `.env` file with the encrypted environment variables.
    7. Updates the `.gitignore` file to ensure `.env` and `.envhub` are ignored.

    :param project_nam: Name of the project to be cloned.
    :type project_nam: str

    :return: None if successful. Prints error messages to the console and may
        exit the program on failure.
    :rtype: None
    """
    if not project_nam:
        return typer.secho("Project name is required", fg=typer.colors.RED)

    client = get_authenticated_client()

    envhub_config_file = pathlib.Path.cwd() / ".envhub"
    if envhub_config_file.exists():
        typer.secho(f"This folder is already initialized with a different project.")
        typer.secho(
            "If you want to clone " +
            style(project_nam, fg=typer.colors.BRIGHT_CYAN, bold=True) +
            " to this folder, please run " +
            style("envhub reset", fg=typer.colors.BRIGHT_YELLOW, bold=True) +
            " first."
        )
        exit(1)

    typer.secho(f"Cloning " + style(project_nam, fg=typer.colors.BRIGHT_CYAN, bold=True) + f"...")

    project_id = client.table("projects") \
        .select("id") \
        .eq("name", project_nam) \
        .execute()

    if not project_id.data:
        return typer.secho(f"Project {project_nam} not found", fg=typer.colors.RED)

    envs = get_current_env_variables(client, project_id.data[0]["id"])

    role = await get_current_user_role(client, project_id.data[0]["id"])

    envhub_config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(envhub_config_file, "w") as f:
        json.dump({
            "name": project_nam,
            "id": project_id.data[0]["id"],
            "role": role
        }, f, indent=2)

    dot_env_file = pathlib.Path.cwd() / ".env"
    dot_env_file.parent.mkdir(parents=True, exist_ok=True)
    with open(dot_env_file, "w") as f:
        for env in envs:
            f.write(f"{env['env_name']}={env['env_value_encrypted']}\n")

    gitignore_file = pathlib.Path.cwd() / ".gitignore"
    gitignore_file.parent.mkdir(parents=True, exist_ok=True)

    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, "r") as f:
            existing_content = f.read()

    if ".env" not in existing_content:
        with open(gitignore_file, "a") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write(".env\n")

    if ".envhub" not in existing_content:
        with open(gitignore_file, "a") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write(".envhub\n")

    typer.secho(
        f"successfully cloned " + style(project_nam, fg=typer.colors.BRIGHT_CYAN, bold=True) + f" to .env")

    return None
