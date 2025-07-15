# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import supabase
import typer


def get_project_password(client: supabase.Client, project_id: str, user_id: str) -> str:
    """
    fetches the password hash for a specific project associated with a specific user
    from the "projects" table in the Supabase database. the function connects to
    the database using the provided Supabase client, retrieves the associated
    password hash based on the project ID and user ID, and returns it.

    :param client: supabase client used to interact with the "projects" table.
    :type client: supabase.Client
    :param project_id: Unique identifier of the project for which the password hash is fetched.
    :type project_id: str
    :param user_id: Unique identifier of the user associated with the project.
    :type user_id: str
    :return: The password hash string of the specified project.
    :rtype: str
    """
    try:
        response = client.table("projects") \
            .select("password_hash") \
            .eq("id", project_id) \
            .eq("user_id", user_id) \
            .execute()
        return response.data[0]["password_hash"]
    except Exception as e:
        typer.secho(f"Error fetching project password: {str(e)}", fg=typer.colors.RED)
        exit(1)
