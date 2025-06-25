import json
import pathlib

import typer
from typer import style

from src.auth import get_authenticated_client
from src.services.getCurrentEnvVariables import get_current_env_variables
from src.services.getCurrentUserRole import get_current_user_role


async def clone(project_nam: str):
    """
    Clone the environment variables of a project to a .env file.

    Args:
        project_nam (str): The name of the project to clone.

    Returns:
        None
    """
    if not project_nam:
        return typer.secho("Project name is required", fg=typer.colors.RED)

    client = get_authenticated_client()

    envhub_config_file = pathlib.Path.cwd() / ".envhub/config.json"
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
