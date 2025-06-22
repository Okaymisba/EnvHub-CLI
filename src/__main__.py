import typer

from src import auth

app = typer.Typer()


@app.command("login")
def login():
    if auth.is_logged_in():
        typer.secho(f"Already logged in as {auth.get_logged_in_email()}", fg=typer.colors.YELLOW)
        typer.echo("Use `logout` to log out")
        return

    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)

    if auth.login(email, password):
        typer.secho("Logged in successfully", fg=typer.colors.GREEN)
    else:
        typer.secho("Login failed", fg=typer.colors.RED)


@app.command("logout")
def logout():
    auth.logout()
    typer.secho("Logged out successfully", fg=typer.colors.GREEN)


@app.command("whoami")
def whoami():
    email = auth.get_logged_in_email()
    if email:
        typer.secho(f"Logged in as: {email}", fg=typer.colors.CYAN)
    else:
        typer.secho("You are not logged in", fg=typer.colors.RED)


if __name__ == "__main__":
    app()
