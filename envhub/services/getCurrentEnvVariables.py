# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import functools
from typing import List, Optional

import typer
from supabase import Client


@functools.lru_cache(maxsize=32)
def _get_cached_latest_version_id(client: Client, project_id: str) -> Optional[str]:
    """
    Fetches the latest version ID for a given project from the "env_versions" table,
    using an LRU cache to store results for up to 32 distinct project queries. Returns
    the ID of the latest version if available, or None if no data is found or an error
    occurs during the query.

    :param client: The client instance used to interact with the database.
    :type client: Client
    :param project_id: The unique identifier of the project for which the latest
        version ID is being fetched.
    :type project_id: str
    :return: The latest version ID if available, otherwise None.
    :rtype: Optional[str]
    """
    try:
        version_resp = (client.table("env_versions")
                        .select("id", count="exact")
                        .eq("project_id", project_id)
                        .order("version_number", desc=True)
                        .limit(1)
                        .execute())

        if not version_resp.data:
            return None

        return version_resp.data[0]["id"]
    except Exception as e:
        typer.secho(f"Error fetching latest version: {str(e)}", fg=typer.colors.RED)
        return None


def get_current_env_variables(client: Client, project_id: str) -> List[dict]:
    """
    Retrieve the current environment variables for a specific project, using the latest
    cached version id. If no version id is cached or an error occurs while fetching,
    appropriate feedback will be provided, or an empty list will be returned.

    :param client: Instance of the Client used to manage database queries and operations.
    :param project_id: Identifier of the project whose environment variables are being retrieved.
    :return: A list of dictionaries representing environment variables, including information
             like name and encrypted value. Returns an empty list if no variables exist
             or an error occurs during retrieval.
    """
    latest_version_id = _get_cached_latest_version_id(client, project_id)

    if not latest_version_id:
        typer.secho("No environment version found for the project.", fg=typer.colors.YELLOW)
        return []

    try:
        response = (client.table("env_variables")
                    .select(
            "id, env_name, env_value_encrypted, "
            "salt, nonce, tag"
        )
                    .eq("project_id", project_id)
                    .eq("version_id", latest_version_id)
                    .order("env_name")
                    .execute())

        return response.data or []
    except Exception as e:
        typer.secho(f"Error fetching environment variables: {str(e)}", fg=typer.colors.RED)
        return []
