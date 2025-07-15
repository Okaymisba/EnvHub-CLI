# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import typer

from envhub.services.getCurrentEnvVariables import get_current_env_variables
from envhub.utils.crypto import CryptoUtils


async def create_env_version(project_id: str, env_entries: list, password: str, supabase) -> dict:
    """
    Creates a new environment version for the given project. This involves fetching existing
    environment variables, determining the next version number, encrypting metadata and
    variables, and inserting them into the appropriate database tables.

    :param project_id: The unique identifier of the project for which the environment version
        is being created.
    :type project_id: str
    :param env_entries: A list containing a new environment variable entry, where the first
        element is the variable name and the second element is its value.
    :type env_entries: list
    :param password: The encryption password used to encrypt and decrypt environment variables.
    :type password: str
    :param supabase: The Supabase client instance used for database operations.
    :return: A dictionary representing the newly created version's metadata.
    :rtype: dict
    :raises SystemExit: If an error occurs during decryption or any other process, the
        application exits with an error message.
    """
    try:
        existing_variables = get_current_env_variables(supabase, project_id)

        version_resp = supabase \
            .table('env_versions') \
            .select('version_number') \
            .filter('project_id', 'eq', project_id) \
            .order('version_number', desc=True) \
            .limit(1) \
            .execute()

        existing_versions = version_resp.data or []
        next_version_number = (existing_versions[0]['version_number'] + 1) if existing_versions else 1

        dummy_encryption = CryptoUtils.encrypt('version_metadata', password)

        version_insert_resp = supabase \
            .table('env_versions') \
            .insert({
            'project_id': project_id,
            'version_number': next_version_number,
            'variable_count': len(existing_variables) + 1,
            'salt': dummy_encryption['salt'],
            'nonce': dummy_encryption['nonce'],
            'tag': dummy_encryption['tag']
        }) \
            .execute()

        version = version_insert_resp.data[0]

        all_entries = []

        for existing_var in existing_variables:
            try:
                decrypted_value = CryptoUtils.decrypt(
                    {
                        "ciphertext": existing_var['env_value_encrypted'],
                        "salt": existing_var['salt'],
                        "nonce": existing_var['nonce'],
                        "tag": existing_var['tag']
                    },
                    password)
                all_entries.append({
                    'name': existing_var['env_name'],
                    'value': decrypted_value
                })
            except Exception as e:
                typer.secho(f"Error decrypting environment variable: {e}", fg=typer.colors.RED)
                exit(1)

        all_entries.append({"name": env_entries[0], "value": env_entries[1]})
        env_variables = []

        for entry in all_entries:
            encrypted = CryptoUtils.encrypt(entry['value'], password)
            env_variables.append({
                'project_id': project_id,
                'version_id': version['id'],
                'env_name': entry['name'],
                'env_value_encrypted': encrypted['ciphertext'],
                'salt': encrypted['salt'],
                'nonce': encrypted['nonce'],
                'tag': encrypted['tag']
            })

        supabase.table('env_variables').insert(env_variables).execute()

        return version

    except Exception as e:
        typer.secho(f"Error creating environment version: {str(e)}", fg=typer.colors.RED)
        exit(1)
