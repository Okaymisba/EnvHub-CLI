import supabase
import typer


def gen_encrypted_project_password(client: supabase.Client, project_id: str, user_id: str):
    """
    Generates a structured dictionary containing encrypted project password parts and the
    associated access password hash for a specific user and project.

    The function retrieves the required data from the "project_members" table in the database
    using the provided client instance. If the encrypted project password or the access password
    hash is missing, it returns None. If the encrypted project password has an invalid format,
    an error is raised, and execution terminates with an error message.

    :param client: The Supabase client instance used for database queries.
    :type client: supabase.Client
    :param project_id: The unique identifier of the project for which the password is being
        retrieved.
    :type project_id: str
    :param user_id: The unique identifier of the user for whom the project password is being
        retrieved.
    :type user_id: str
    :return: A dictionary containing the `ciphertext`, `salt`, `nonce`, `tag`, and
        `access_password_hash` if the operation is successful, otherwise None.
    :rtype: dict | None
    """
    try:
        response = client.table("project_members") \
            .select("encrypted_project_password", "access_password_hash") \
            .eq("project_id", project_id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            return None

        if not response.data[0].get("encrypted_project_password") or not response.data[0].get("access_password_hash"):
            return None

        parts = response.data[0]["encrypted_project_password"].split(":")
        if len(parts) != 4:
            raise ValueError("Invalid encrypted project password format")

        return {
            "ciphertext": parts[0],
            "salt": parts[1],
            "nonce": parts[2],
            "tag": parts[3],
            "access_password_hash": response.data[0]["access_password_hash"]
        }

    except Exception as e:
        typer.secho(f"Error fetching project password: {str(e)}", fg=typer.colors.RED)
        exit(1)
