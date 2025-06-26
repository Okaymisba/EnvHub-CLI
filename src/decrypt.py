import json
import os
import pathlib
import shlex
import subprocess

import typer

from src.auth import get_authenticated_client
from src.services.getCurrentEnvVariables import get_current_env_variables
from src.utils.crypto import CryptoUtils


def decrypt_runtime_and_run_command(command: str) -> None:
    """
    Decrypts runtime environment variables and executes a command.

    This function retrieves environment variables linked to a specific project,
    decrypts them using cryptographic utilities, updates the current process's
    environment with the decrypted variables, and executes a shell command. If
    any error occurs during the decryption or command execution process, it
    provides appropriate feedback to the user and exits with an error code.

    :param command: The command to be executed after setting up decrypted
        environment variables
    :type command: str
    :return: None
    """
    client = get_authenticated_client()
    envhub_config_file = pathlib.Path.cwd() / ".envhub"

    if not envhub_config_file.exists():
        typer.secho("No config file found for this folder.", fg="red")
        typer.secho("Please run 'envhub clone' first.", fg="yellow")
        exit(1)

    try:
        with open(envhub_config_file, "r") as f:
            json_config = json.load(f)
    except json.JSONDecodeError:
        typer.secho("Invalid .envhub config file.", fg="red")
        exit(1)

    # Get and decrypt environment variables
    crypto_utils = CryptoUtils()
    envs = get_current_env_variables(client, json_config.get("project_id"))
    decrypted_envs = {}

    role = json_config.get("role")
    password = json_config.get("password")

    for env in envs:
        try:
            key = env.get("key")
            if not key:
                continue

            if role == "owner":
                decrypted_value = crypto_utils.decrypt(env, password)
            elif role == "member":
                decrypted_value = crypto_utils.decrypt(
                    env,
                    crypto_utils.decrypt(
                        json_config.get("encrypted_data"),
                        password
                    )
                )
            else:
                typer.secho(f"Unknown role: {role}", fg="red")
                exit(1)

            decrypted_envs[key] = decrypted_value

        except Exception as e:
            typer.secho(f"Error decrypting variable: {str(e)}", fg="red")
            continue

    os.environ.update(decrypted_envs)

    try:
        if not command:
            typer.secho("No command provided to execute.", fg="yellow")
            return

        command_parts = shlex.split(command)

        process = subprocess.Popen(
            command_parts,
            env=os.environ,
            shell=False
        )
        process.communicate()

        if process.returncode != 0:
            typer.secho(f"Command failed with exit code {process.returncode}", fg="red")
            exit(process.returncode)

    except Exception as e:
        typer.secho(f"Error executing command: {str(e)}", fg="red")
        exit(1)
