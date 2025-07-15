# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import typer

from envhub import auth
from envhub.services.createEnvVersion import create_env_version
from envhub.services.getEncryptedProjectPassword import get_encrypted_project_password
from envhub.utils.crypto import CryptoUtils


async def add(entries: list, password: str, current_user_role: str, project_id: str):
    """
    Adds environment variables to a specified project. The function ensures that only users with proper
    roles ('admin' or 'owner') can perform the operation. For 'admin' users, it manages decryption and
    verification of the project password before proceeding. It interacts with external services and
    utilities for authentication, password management, and environment version updates.

    :param entries: A list of key-value pairs representing the environment variables to add.
    :type entries: list
    :param password: The password associated with the project, either in plain or encrypted form depending on the role.
    :type password: str
    :param current_user_role: The role of the current user performing the action ('user', 'admin', or 'owner').
    :type current_user_role: str
    :param project_id: Unique identifier of the project where environment variables will be added.
    :type project_id: str
    :return: None
    :rtype: None
    """
    try:
        if current_user_role == 'user':
            typer.secho("You don't have permission to add environment variables.", fg=typer.colors.RED)
            exit(1)

        if current_user_role == 'admin':
            client = auth.get_authenticated_client()
            encrypted_password = get_encrypted_project_password(client, project_id, client.auth.get_user().user.id)

            if not encrypted_password:
                typer.secho("Error: Project password not found.", fg=typer.colors.RED)
                exit(1)

            decrypted_password = CryptoUtils.decrypt(encrypted_password, password)

            if not decrypted_password:
                typer.secho("Error: Failed to decrypt project password.", fg=typer.colors.RED)
                exit(1)

            await create_env_version(project_id, entries, decrypted_password, client)

            return

        if current_user_role == 'owner':
            await create_env_version(project_id, entries, password, auth.get_authenticated_client())

    except Exception as e:
        typer.secho(f"Error adding environment variables: {str(e)}", fg=typer.colors.RED)
        exit(1)
