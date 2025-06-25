from typing import Optional

import supabase
import typer


async def get_current_user_role(client: supabase.Client, project_id: str) -> Optional[str]:
    try:
        user_id = client.auth.get_user().user.id
        if not user_id:
            return None

        response = client \
            .table('project_members') \
            .select('role') \
            .eq('project_id', project_id) \
            .eq('user_id', user_id) \
            .execute()

        data = response.data
        if not data:
            return None

        return data[0].get('role')
    except Exception as e:
        typer.secho(f"Error fetching current user role: {str(e)}", fg=typer.colors.RED)
        exit(1)
