import json
import os
import pathlib
import shlex
import subprocess

import typer

from envhub.utils.crypto import CryptoUtils


def decrypt_runtime_and_run_command(command: str) -> None:
    """
    Decrypts runtime configurations and executes a specified shell command.

    This function performs environment variable decryption based on either a
    `.envhub` configuration file or the `ENVHUB_PASSWORD` environment variable.
    It securely decrypts the `.env` file and updates the runtime environment
    before running the given shell command. The function exits with an appropriate
    status code if an issue arises, such as missing configurations, decryption
    failures, or command execution errors.

    :param command: The shell command to execute after decrypting the environment.
    :type command: str
    :return: None
    """
    env_file = pathlib.Path.cwd() / ".env"
    envhub_config_file = pathlib.Path.cwd() / ".envhub"

    def execute_command():
        """
        Decrypts runtime files and executes a provided shell command.

        The function is designed to handle the decryption of runtime-related files
        before executing a given shell command in a subprocess. If the command
        is invalid or encounters execution errors, it provides appropriate feedback
        and exit codes. Errors during command execution or missing commands
        are logged as warnings or errors. The function ensures that the execution
        environment is prepared correctly by using the current process environment.

        :return: None
        """
        if not command:
            typer.secho("No command provided to execute.", fg="yellow")
            return

        try:

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

    if envhub_config_file.exists():
        try:
            with open(envhub_config_file, "r") as f:
                json_config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            typer.secho(f"Error reading .envhub config file: {str(e)}", fg="red")
            exit(1)

        crypto_utils = CryptoUtils()
        role = json_config.get("role")
        password = json_config.get("password")

        if not password:
            typer.secho("No password found in .envhub config", fg="red")
            exit(1)

        try:
            if role == "owner":
                decrypted_env = crypto_utils.decrypt_env_file(str(env_file), password)
            elif role in ("user", "admin"):
                decrypted_env = crypto_utils.decrypt_env_file(
                    str(env_file),
                    crypto_utils.decrypt(json_config.get("encrypted_data"), password)
                )
            else:
                typer.secho(f"Unknown role: {role}", fg="red")
                exit(1)

            os.environ.update(decrypted_env)
            execute_command()

        except Exception as e:
            typer.secho(f"Error decrypting environment: {str(e)}", fg="red")
            exit(1)


    elif password := os.getenv("ENVHUB_PASSWORD"):
        try:
            crypto_utils = CryptoUtils()
            decrypted_env = crypto_utils.decrypt_env_file(str(env_file), password)
            os.environ.update(decrypted_env)
            execute_command()
        except Exception as e:
            typer.secho(f"Error decrypting with ENVHUB_PASSWORD: {str(e)}", fg="red")
            exit(1)

    else:
        typer.secho(
            "No valid configuration found. Either create a .envhub config file by running 'envhub clone <project_name>' or set ENVHUB_PASSWORD environment variable.",
            fg="red"
        )
        exit(1)
