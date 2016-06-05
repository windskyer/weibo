"""Database setup and migration commands."""

from weibo.db.sqlalchemy import migration


INIT_VERSION = 81


def db_sync(version=None):
    """Migrate the database to `version` or the most recent version."""
    return migration.db_sync(version=version)


def db_version():
    """Display the current database version."""
    return migration.db_version()
