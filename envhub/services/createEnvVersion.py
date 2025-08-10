# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import typer

from envhub.services.getCurrentEnvVariables import get_current_env_variables
from envhub.utils.crypto import CryptoUtils


async def create_env_version(
        project_id: str,
        env_entries: list[dict],
        password: str,
        supabase,
        is_paid_user: bool = False
):
    """
    Creates a new environment version for a specific project. Depending on whether the user is a paid
    user or not, it updates the environment variables and versions appropriately, by either modifying
    the current version or creating a new one. It also handles encryption for the environment variables
    and stores them within the given database.

    :param project_id: The unique identifier of the project for which the environment version is being created
    :param env_entries: A list of environment entries, where each entry is represented as a dictionary
      containing environment variable name and value
    :param password: The encryption key used to securely encrypt and decrypt environment variable values
    :param supabase: An instance of the database client to handle all read and write operations for the environment
      versions and variables
    :param is_paid_user: A flag indicating whether the user is a paid user; if False, existing
      versions may be overwritten instead of creating new ones (default is False)
    """
    try:
        existing_variables = get_current_env_variables(supabase, project_id)

        version_resp = supabase \
            .table('env_versions') \
            .select('id, version_number') \
            .eq('project_id', project_id) \
            .order('version_number', desc=True) \
            .limit(1) \
            .execute()

        existing_versions = version_resp.data or []
        version_id = None
        version_number = None

        if not is_paid_user:
            if existing_versions:
                delete_resp = supabase \
                    .table('env_variables') \
                    .delete() \
                    .eq('version_id', existing_versions[0]['id']) \
                    .execute()

                version_id = existing_versions[0]['id']
                version_number = existing_versions[0]['version_number']
            else:
                version_number = 1
                dummy_encryption = CryptoUtils.encrypt('version_metadata', password)

                version_insert = supabase.table('env_versions').insert({
                    'project_id': project_id,
                    'version_number': version_number,
                    'variable_count': len(env_entries),
                    'salt': dummy_encryption['salt'],
                    'nonce': dummy_encryption['nonce'],
                    'tag': dummy_encryption['tag']
                }).execute()

                version = version_insert.data[0] if version_insert.data and len(version_insert.data) > 0 else None
                if not version:
                    raise Exception("Failed to create version")
                version_id = version['id']
        else:
            version_number = (existing_versions[0]['version_number'] + 1) if existing_versions else 1
            dummy_encryption = CryptoUtils.encrypt('version_metadata', password)

            version_insert = supabase.table('env_versions').insert({
                'project_id': project_id,
                'version_number': version_number,
                'variable_count': len(existing_variables) + len(env_entries),
                'salt': dummy_encryption['salt'],
                'nonce': dummy_encryption['nonce'],
                'tag': dummy_encryption['tag']
            }).execute()

            version = version_insert.data[0] if version_insert.data and len(version_insert.data) > 0 else None
            if not version:
                raise Exception("Failed to create version")
            version_id = version['id']

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
                print(f"Failed to decrypt existing variable {existing_var['env_name']}: {e}")

        all_entries.extend(env_entries)

        env_variables = []
        for entry in all_entries:
            encrypted = CryptoUtils.encrypt(entry['value'], password)
            env_variables.append({
                'project_id': project_id,
                'version_id': version_id,
                'env_name': entry['name'],
                'env_value_encrypted': encrypted['ciphertext'],
                'salt': encrypted['salt'],
                'nonce': encrypted['nonce'],
                'tag': encrypted['tag']
            })

        supabase.table('env_variables').insert(env_variables).execute()

    except Exception as e:
        typer.secho(f"Error creating environment version: {str(e)}", fg=typer.colors.RED)
        raise
