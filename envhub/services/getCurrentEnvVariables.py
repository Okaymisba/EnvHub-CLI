# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List

import supabase
import typer

from envhub.services.getEnvVariables import get_env_variables


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
