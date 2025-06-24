from typing import Optional, List

import supabase
import typer

from src.auth import get_authenticated_client


def clone(project_nam: str):
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

    typer.secho(f"Cloning {project_nam}...")

    project_id = client.table("projects") \
        .select("id") \
        .eq("name", project_nam) \
        .execute()

    if not project_id.data:
        return typer.secho(f"Project {project_nam} not found", fg=typer.colors.RED)

    envs = get_current_env_variables(client, project_id.data[0]["id"])

    dot_env_file = ".env"
    with open(dot_env_file, "w") as f:
        for env in envs:
            f.write(f"{env['env_name']}={env['env_value_encrypted']}\n")

    typer.secho(f"Cloned {project_nam} to {dot_env_file}")

    return None


def get_env_variables(client: supabase.Client, project_id: str, version_id: Optional[str] = None) -> List[dict]:
    """
    Fetches environment variables from the Supabase database for a given project.

    Args:
        client (supabase.Client): The Supabase client used to interact with the database.
        project_id (str): The ID of the project whose environment variables are to be fetched.
        version_id (Optional[str], optional): The version ID of the environment variables. If not provided,
                                              fetches variables not specific to a version. Defaults to None.

    Returns:
        List[dict]: A list of dictionaries containing environment variables, sorted by environment name.
                    Returns an empty list if no variables are found or if an error occurs.
    """
    try:
        query = client.table("env_variables") \
            .select("*") \
            .eq("project_id", project_id)

        if version_id:
            query = query.eq("version_id", version_id)

        response = query.order("env_name").execute()
        return response.data or []
    except Exception as e:
        typer.secho(f"Error fetching environment variables: {str(e)}", fg=typer.colors.RED)
        return []


def get_current_env_variables(client: supabase.Client, project_id: str) -> List[dict]:
    """
    Fetches the current environment variables from the Supabase database for a given project.

    Args:
        client (supabase.Client): The Supabase client used to interact with the database.
        project_id (str): The ID of the project whose environment variables are to be fetched.

    Returns:
        List[dict]: A list of dictionaries containing environment variables, sorted by environment name.
                    Returns an empty list if no variables are found or if an error occurs.
    """
    try:
        version_resp = client.table("env_versions") \
            .select("id") \
            .eq("project_id", project_id) \
            .order("version_number", desc=True) \
            .limit(1) \
            .execute()

        if not version_resp.data:
            return []

        latest_version_id = version_resp.data[0]["id"]
        return get_env_variables(client, project_id, latest_version_id)
    except Exception as e:
        typer.secho(f"Error fetching environment versions: {str(e)}", fg=typer.colors.RED)
        return []
