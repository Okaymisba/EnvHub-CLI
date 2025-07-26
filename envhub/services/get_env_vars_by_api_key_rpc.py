# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List, Dict, Any

import typer
from supabase import Client


def get_env_vars_by_api_key(client: Client, api_key: str) -> List[Dict[str, Any]]:
    """
    Fetches environment variables associated with a given API key by calling an RPC function
    on the provided client.

    This function communicates with the backend via an RPC call to retrieve the environment
    variables linked to the supplied API key. Errors during the process are handled gracefully,
    either outputting error messages to the console or returning an empty list in case of an
    unsuccessful operation. If the backend indicates failure, it logs the error message specified
    by the response.

    :param client: The client instance used to make the RPC call.
    :type client: Client
    :param api_key: The API key for which to fetch the environment variables.
    :type api_key: str
    :return: A list of dictionaries representing the fetched environment variables, or an empty
             list if the operation fails.
    :rtype: List[Dict[str, Any]]
    """
    try:
        response = (client.rpc('get_environment_variables_by_api_key',
                               {'api_key_param': api_key})
                    .execute())

        result = response.data[0]

        if not result.get('success'):
            typer.secho(
                f"Error: {result.get('message', 'Unknown error')}",
                fg=typer.colors.RED
            )
            return []

        return result.get('data', [])

    except Exception as e:
        typer.secho(
            f"Error calling RPC function: {str(e)}",
            fg=typer.colors.RED
        )
        return []
