import json
import pathlib

import typer


def get_role():
    """
    Get the role from the configuration file located in the current working directory.

    This function reads a JSON configuration file named ".envhub" from the
    current working directory. If the file does not exist, it displays an
    error message and exits the program. Upon successfully reading the file,
    it retrieves the "role" key from the JSON object and returns its value.

    :raises SystemExit: If the configuration file is not found in the
        current working directory.
    :return: The value of the "role" key from the JSON configuration file.
    :rtype: str
    """
    config_file = pathlib.Path.cwd() / ".envhub"
    if not config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    with open(config_file, "r") as f:
        config_data = json.load(f)

    return config_data["role"]
