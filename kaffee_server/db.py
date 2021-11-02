import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    current_app.logger.debug("Database connection requested")
    if "db" not in g:
        conn = sqlite3.connect(
            current_app.config.get("DATABASE"), detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        g.db = conn
        current_app.logger.debug("Added database to global")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        current_app.logger.debug("Closing database")
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
        current_app.logger.debug("Executed setup script")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
