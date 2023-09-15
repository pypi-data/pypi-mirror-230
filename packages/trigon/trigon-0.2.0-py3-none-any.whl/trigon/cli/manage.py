import subprocess
import webbrowser

import typer

from trigon.cli.commands.database import group as database
from trigon.cli.commands.migrations import group as migrations

cli: typer.Typer = typer.Typer()


@cli.callback(name="trigon")
def main(ctx: typer.Context):
    """Trigon CLI."""
    ctx.obj = {"db": app.state.container.resources.database()}


cli.add_typer(database, name="database")
cli.add_typer(migrations, name="migrations")


@cli.command()
def serve(port: int = 8000):
    """Serve the application on localhost."""
    webbrowser.open(f"http://localhost:{port}")

    try:
        subprocess.run(
            [
                "poetry",
                "run",
                "uvicorn",
                "src.trigon.app:app",
                "--port",
                f"{port}",
                "--reload",
                "--log-level=debug",
            ],
        )
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


@cli.command()
def test():
    """Run the test suite."""
    cmd = "poetry run python -m pytest --cov=trigon"

    try:
        subprocess.run(cmd.split())
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


@cli.command()
def docs(port: int = 8000):
    """Build and serve the documentation locally."""
    webbrowser.open(f"http://localhost:{port}")

    try:
        subprocess.run(["poetry", "run", "mkdocs", "serve", "-a", f"localhost:{port}"])
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


if __name__ == "__main__":
    cli()
