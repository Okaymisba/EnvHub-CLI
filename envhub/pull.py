# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import pathlib

import typer

from envhub import auth
from envhub.services.getCurrentEnvVariables import get_current_env_variables


def pull():
    """
    Pulls environment variable changes from the remote repository for the specific
    project and updates the local `.env` file accordingly. The function retrieves
    the configuration file to determine the project ID, fetches the current
    environment variables from the server, and writes them to a local `.env` file.

    :raises SystemExit: If no config file is found in the current working directory or
        if other critical operations fail.
    :raises FileNotFoundError: If the `.env` file cannot be created or written to.

    :return: None
    """
    typer.secho("Pulling changes from the remote repository...", fg=typer.colors.CYAN)

    config_file = pathlib.Path.cwd() / ".envhub"
    if not config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    with open(config_file, "r") as f:
        config_data = json.load(f)

    client = auth.get_authenticated_client()
    current_env_vars = get_current_env_variables(client, config_data["project_id"])

    if not current_env_vars:
        typer.secho("No environment variables found for this project.", fg=typer.colors.RED)
        return

    dot_env_file = pathlib.Path.cwd() / ".env"
    dot_env_file.parent.mkdir(parents=True, exist_ok=True)
    with open(dot_env_file, "w") as f:
        for env in current_env_vars:
            f.write(f"{env['env_name']}={env['env_value_encrypted']}\n")

    typer.secho("Changes pulled successfully.", fg=typer.colors.GREEN)
