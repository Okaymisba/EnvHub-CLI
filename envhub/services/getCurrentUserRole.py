# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Optional

import supabase
import typer


async def get_current_user_role(client: supabase.Client, project_id: str) -> Optional[str]:
    """
    Fetches the current user's role for a specific project.

    This function retrieves the role of the authenticated user for a specific
    project by querying the 'project_members' table from the Supabase client.
    If the user is not part of the project or the role could not be determined,
    the function returns None. In case of an error during the process, the function
    displays an error message and terminates the program.

    :param client: Supabase client instance used to query the database.
    :type client: supabase.Client
    :param project_id: ID of the project for which the user's role is being fetched.
    :type project_id: str
    :return: The role of the current user in the specified project, or None if the user
             does not have a role in the project.
    :rtype: Optional[str]
    """
    try:
        user_id = client.auth.get_user().user.id
        if not user_id:
            return None

        response = client \
            .table('project_members') \
            .select('role') \
            .eq('project_id', project_id) \
            .eq('user_id', user_id) \
            .execute()

        data = response.data
        if not data:
            return None

        return data[0].get('role')
    except Exception as e:
        typer.secho(f"Error fetching current user role: {str(e)}", fg=typer.colors.RED)
        exit(1)
