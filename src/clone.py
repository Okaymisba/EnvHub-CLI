import json
import pathlib

import typer
from typer import style

from src.auth import get_authenticated_client
from src.services.getCurrentEnvVariables import get_current_env_variables
from src.services.getCurrentUserRole import get_current_user_role
from src.services.getEncryptedProjectPassword import gen_encrypted_project_password
from src.services.getProjectPassword import get_project_password


async def clone(project_name: str):
    """
    Clones an existing project configuration and environment variables to the current directory.
    This involves fetching project details, environment variables, user roles, and optionally project
    passwords. It also prepares required files like `.env` and `.envhub`, and updates `.gitignore`
    to commit safely, preventing unintended secrets exposure.

    :param project_name: The name of the project to be cloned
    :type project_name: str
    :return: None
    :raises ValueError: If the project name is not provided or the project does not exist
    """
    if not project_name:
        return typer.secho("Project name is required", fg=typer.colors.RED)

    client = get_authenticated_client()

    envhub_config_file = pathlib.Path.cwd() / ".envhub"
    if envhub_config_file.exists():
        typer.secho(f"This folder is already initialized with a different project.")
        typer.secho(
            "If you want to clone " +
            style(project_name, fg=typer.colors.BRIGHT_CYAN, bold=True) +
            " to this folder, please run " +
            style("envhub reset", fg=typer.colors.BRIGHT_YELLOW, bold=True) +
            " first."
        )
        exit(1)

    typer.secho(f"Cloning " + style(project_name, fg=typer.colors.BRIGHT_CYAN, bold=True) + f"...")

    project_id = client.table("projects") \
        .select("id, user_id") \
        .eq("name", project_name) \
        .execute()

    if not project_id.data:
        return typer.secho(f"Project {project_name} not found", fg=typer.colors.RED)

    envs = get_current_env_variables(client, project_id.data[0]["id"])

    role = await get_current_user_role(client, project_id.data[0]["id"])

    password_data = dict()

    if role == "owner":
        password_hash = get_project_password(client, project_id.data[0]["id"], project_id.data[0]["user_id"])
        if not password_hash:
            typer.secho("Failed to fetch project password", fg=typer.colors.RED)
            exit(1)
        password_data.update({
            "password_hash": password_hash
        })
    elif role == "admin" or role == "member":
        encrypted_password_data = gen_encrypted_project_password(client, project_id.data[0]["id"],
                                                                 project_id.data[0]["user_id"])
        if not encrypted_password_data:
            typer.secho("Failed to fetch project password", fg=typer.colors.RED)
            exit(1)

        password_data.update({
            "encrypted_data": {
                "salt": encrypted_password_data["salt"],
                "nonce": encrypted_password_data["nonce"],
                "ciphertext": encrypted_password_data["ciphertext"],
                "tag": encrypted_password_data["tag"]
            },
            "access_password_hash": encrypted_password_data["access_password_hash"]
        })

    envhub_config_file.parent.mkdir(parents=True, exist_ok=True)
    # TODO: Encrypting the data of the .envhub file
    with open(envhub_config_file, "w") as f:
        json.dump({
            "name": project_name,
            "id": project_id.data[0]["id"],
            "role": role,
            **password_data
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
        f"successfully cloned " + style(project_name, fg=typer.colors.BRIGHT_CYAN, bold=True) + f" to .env")

    return None
