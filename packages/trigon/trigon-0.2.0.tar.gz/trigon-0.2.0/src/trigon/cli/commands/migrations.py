import subprocess

import typer

group: typer.Typer = typer.Typer()


@group.callback()
def migrations():
    """Database migrations related commands."""


@group.command()
def check():
    """Check whether the database is up to date."""
    try:
        subprocess.run(["alembic", "check"])
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


@group.command()
def generate(commit_message: str):
    """Auto-generate a migration script."""
    try:
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", f'"{commit_message}"'])
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


@group.command()
def apply(revision: str = "head"):
    """Apply migrations."""
    try:
        subprocess.run(["alembic", "upgrade", revision])
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


@group.command()
def revert(revision: str = "head"):
    """Revert the previous migrations."""
    try:
        subprocess.run(["alembic", "downgrade", revision])
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)
