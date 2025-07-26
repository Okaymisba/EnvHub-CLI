import typer


def decrypt_prod_by_api_key(command: str = None):
    """
    Decrypts environment variables from the EnvHub platform using the provided
    API key and saves them to a `.env` file or injects them into a subprocess
    executing a given command. This function ensures that sensitive environment
    variables are securely retrieved and decrypted before being used or
    persisted.

    :param command: The command to be executed with the decrypted environment
        variables injected. If not provided, the variables are saved to a `.env` file.

    :return: None
    """
    import supabase
    import os
    import shlex
    import subprocess

    from envhub.services.get_env_vars_by_api_key_rpc import get_env_vars_by_api_key
    from envhub.auth import SUPABASE_URL
    from envhub.auth import SUPABASE_KEY
    from envhub.utils.crypto import CryptoUtils

    client = supabase.create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

    envhub_api_key = os.getenv("ENVHUB_API_KEY")
    if not envhub_api_key:
        typer.secho("ENVHUB_API_KEY is not set", fg="red")
        exit(1)

    envhub_password = os.getenv("ENVHUB_PASSWORD")
    if not envhub_password:
        typer.secho("ENVHUB_PASSWORD is not set", fg="red")
        exit(1)
    crypto_utils = CryptoUtils()
    envs = get_env_vars_by_api_key(client=client, api_key=envhub_api_key)
    decrypted_envs = {}

    for env in envs:
        encrypted_data = {
            "ciphertext": env.get("env_value_encrypted"),
            "nonce": env.get("nonce"),
            "tag": env.get("tag"),
            "salt": env.get("salt"),
        }

        decrypted_value = crypto_utils.decrypt(encrypted_data=encrypted_data, password=envhub_password)
        decrypted_envs[env.get("env_name")] = decrypted_value

    if command:
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

    else:
        with open(".env", "w") as f:
            for env_name, env_value in decrypted_envs.items():
                f.write(f"{env_name}={env_value}\n")
        typer.secho("Decrypted environment variables saved to .env", fg="green")
