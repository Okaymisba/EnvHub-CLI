# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Optional, List

import supabase
import typer


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
