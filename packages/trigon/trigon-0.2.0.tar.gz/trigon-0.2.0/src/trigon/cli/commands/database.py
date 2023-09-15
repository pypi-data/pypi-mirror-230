from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from trigon.resources.database import Database

group: typer.Typer = typer.Typer()


@group.callback()
def db():
    """Database related commands."""


@group.command()
def create(ctx: typer.Context):
    """Create the database."""
    db: Database = ctx.obj["db"]

    db.create_database()
