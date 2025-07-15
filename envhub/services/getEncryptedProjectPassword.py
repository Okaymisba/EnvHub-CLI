# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import supabase
import typer


def get_encrypted_project_password(client: supabase.Client, project_id: str, user_id: str):
    """
    Fetches the encrypted project password and associated access password hash for a specific
    user in a given project. The function queries the `project_members` table to retrieve
    the necessary data and parses the `encrypted_project_password` into its components.

    :param client: An instance of supabase.Client used to interact with the database.
    :type client: supabase.Client

    :param project_id: Unique identifier of the project for which the password is fetched.
    :type project_id: str

    :param user_id: Unique identifier of the user whose access and project-related
        passwords are retrieved.
    :type user_id: str

    :return: A dictionary containing the parsed components of the encrypted project
        password (`ciphertext`, `salt`, `nonce`, `tag`) and the `access_password_hash`
        if successful; `None` if the data is not found or improperly formatted.
    :rtype: dict | None
    """
    try:
        response = client.table("project_members") \
            .select("encrypted_project_password", "access_password_hash") \
            .eq("project_id", project_id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            return None

        if not response.data[0].get("encrypted_project_password") or not response.data[0].get("access_password_hash"):
            return None

        parts = response.data[0]["encrypted_project_password"].split(":")
        if len(parts) != 4:
            raise ValueError("Invalid encrypted project password format")

        return {
            "ciphertext": parts[0],
            "salt": parts[1],
            "nonce": parts[2],
            "tag": parts[3],
            "access_password_hash": response.data[0]["access_password_hash"]
        }

    except Exception as e:
        typer.secho(f"Error fetching project password: {str(e)}", fg=typer.colors.RED)
        exit(1)
