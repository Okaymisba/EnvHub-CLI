import json
import pathlib

import typer

from envhub.utils.crypto import CryptoUtils


def decrypt_and_store():
    """
    Decrypts an environment file using credentials stored in a configuration file and saves the
    decrypted environment variables into a `.env` file. The function validates user roles and
    handles encryption and decryption logic accordingly. If the required configuration or
    password is missing, or if any errors occur while processing the decryption, appropriate
    error messages will be displayed, and the execution will terminate.

    :raises IOError: If there is an error reading the `.envhub` configuration file.
    :raises json.JSONDecodeError: If the `.envhub` configuration file contains invalid JSON.
    :raises Exception: For any error encountered during the decryption process.
    :returns: None
    """
    env_file = pathlib.Path.cwd() / ".env"
    envhub_config_file = pathlib.Path.cwd() / ".envhub"
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

            with open(".env", "w") as f:
                for key, value in decrypted_env.items():
                    f.write(f"{key}={value}\n")
                typer.secho("Successfully decrypted and stored environment variables in .env file", fg="green")

        except Exception as e:
            typer.secho(f"Error decrypting environment: {str(e)}", fg="red")
            exit(1)

    else:
        typer.secho("No .envhub config file found", fg="red")
        exit(1)
