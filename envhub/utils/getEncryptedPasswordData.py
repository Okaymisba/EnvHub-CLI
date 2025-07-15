# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import pathlib

import typer


def get_encrypted_password_data():
    """
    Retrieves and returns the encrypted password data from a configuration file
    located in the current working directory. If the file does not exist,
    the function will terminate the program execution.

    The function checks for the existence of a `.envhub` file in the current
    working directory. If it exists, the file is read, and the encrypted
    password data is retrieved from it under the key `"encrypted_data"`.
    If the file does not exist, an error message is printed, and the program exits.

    :return: Encrypted password data retrieved from the `.envhub` file if present
    :rtype: dict or None
    """
    config_file = pathlib.Path.cwd() / ".envhub"
    if not config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    with open(config_file, "r") as f:
        config_data = json.load(f)
        encrypted_data = config_data.get("encrypted_data")

    return encrypted_data
