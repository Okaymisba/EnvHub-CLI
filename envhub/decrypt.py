# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
import pathlib
import shlex
import subprocess

import typer

from envhub.auth import get_authenticated_client
from envhub.services.getCurrentEnvVariables import get_current_env_variables
from envhub.utils.crypto import CryptoUtils


def decrypt_runtime_and_run_command(command: str) -> None:
    """
    Decrypts runtime environment variables and executes a given command.

    This function performs multiple tasks:
    1. Ensures the presence of a `.envhub` configuration file in the current directory.
    2. Reads and validates the `.envhub` configuration file as JSON.
    3. Retrieves the current environment variables from an authenticated client
       and decrypts them based on the user's role and credentials.
    4. Updates the operating system's environment variables with the decrypted
       values.
    5. Executes the specified shell command using the updated environment
       variables.

    If any step fails, the function provides informative error messages to assist
    the user in troubleshooting.

    :param command: The shell command to execute after decrypting environment
                    variables.
    :type command: str
    :return: None

    :raises Exception: Any error encountered during decryption or command
                       execution is logged, and relevant error details are
                       displayed to the user.
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

    crypto_utils = CryptoUtils()
    envs = get_current_env_variables(client, json_config.get("project_id"))
    decrypted_envs = {}

    role = json_config.get("role")
    password = json_config.get("password")

    for env in envs:
        try:
            key = env.get("env_name")
            if not key:
                continue

            if role == "owner":
                decrypted_value = crypto_utils.decrypt(
                    {
                        "ciphertext": env.get("env_value_encrypted"),
                        "salt": env.get("salt"),
                        "nonce": env.get("nonce"),
                        "tag": env.get("tag")
                    },
                    password
                )
            elif role == "user" or role == "admin":
                decrypted_value = crypto_utils.decrypt(
                    {
                        "ciphertext": env.get("env_value_encrypted"),
                        "salt": env.get("salt"),
                        "nonce": env.get("nonce"),
                        "tag": env.get("tag")
                    },
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
