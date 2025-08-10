# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Dict, Any

import typer
from supabase import Client


async def get_subscription_limits_for_project(supabase: Client, project_id: str) -> Dict[str, Any]:
    """
    Fetches the subscription limit data for a specific project by querying the
    Supabase database. This function first retrieves the `user_id` associated
    with the provided `project_id` and subsequently fetches the subscription limits
    of the user from a stored procedure in Supabase.

    :param supabase: The Supabase client used to interact with the database.
    :type supabase: Client
    :param project_id: The unique identifier for the project.
    :type project_id: str
    :return: A dictionary containing subscription limit data for the project.
    :rtype: Dict[str, Any]
    :raises Exit: If the project is not found, access is denied, subscription
                  limits cannot be fetched, or an unexpected error occurs.
    """
    try:
        project_data = supabase.table('projects') \
            .select('user_id') \
            .eq('id', project_id) \
            .single() \
            .execute()

        if not project_data.data:
            typer.secho("Project not found or access denied", fg="red")
            raise typer.Exit(code=1)

        result = supabase.rpc(
            'get_user_subscription_limits',
            {
                'user_uuid': str(project_data.data['user_id'])
            }
        ).execute()

        if not result.data or len(result.data) == 0:
            typer.secho("Failed to fetch subscription limits", fg="red")
            raise typer.Exit(code=1)

        return result.data[0]

    except Exception as e:
        typer.secho(f"An error occurred: {str(e)}", fg="red")
        raise typer.Exit(code=1)
