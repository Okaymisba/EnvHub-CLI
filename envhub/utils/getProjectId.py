import json
import pathlib

import typer


def get_project_id():
    """
    Retrieve the project ID from the configuration file.

    This function checks for the existence of a `.envhub` configuration
    file in the current working directory. If the file exists, it attempts
    to read and parse the file as a JSON object and returns the value
    associated with the `project_id` key. If the file does not exist, it
    prints an error message and terminates the program with a non-zero exit code.

    :raises SystemExit: If the configuration file is not found in the
        current working directory.
    :return: The `project_id` value if present in the configuration file;
        otherwise, returns `None`.
    :rtype: Optional[Any]
    """
    config_file = pathlib.Path.cwd() / ".envhub"
    if not config_file.exists():
        typer.secho("No config file found for this folder.", fg=typer.colors.RED)
        exit(1)

    with open(config_file, "r") as f:
        config = json.load(f)

    return config.get("project_id")
