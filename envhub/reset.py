# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pathlib

import typer


def reset():
    """
    Resets the current folder by removing the ".envhub" configuration file if it exists.
    If the file is removed, it prints a confirmation message to indicate the success
    of the operation.

    :raises FileNotFoundError: Raised implicitly if the file cannot be accessed during
        the unlinking process.

    :return: None
    """
    envhub_config_file = pathlib.Path.cwd() / ".envhub"
    if envhub_config_file.exists():
        envhub_config_file.unlink()
    typer.secho("Folder reset successfully.")
