# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import pathlib

import typer


def get_password():
    """
    Retrieve the password stored in the '.envhub' configuration file.

    This function reads a JSON configuration file located in the current working
    directory and extracts the value associated with the "password" key. If the
    configuration file does not exist, the function provides feedback through a
    console message and terminates execution with a non-zero exit code.

    :raises SystemExit: Raised with exit code 1 if no configuration file is found
                        in the current working directory.
    :return: The password value stored in the '.envhub' configuration file. If the
             "password" key does not exist within the file, the return value will
             be None.
    :rtype: Optional[str]
    """
    config_file = pathlib.Path.cwd() / ".envhub"
    if not config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    with open(config_file, "r") as f:
        config_data = json.load(f)

    return config_data.get("password")
