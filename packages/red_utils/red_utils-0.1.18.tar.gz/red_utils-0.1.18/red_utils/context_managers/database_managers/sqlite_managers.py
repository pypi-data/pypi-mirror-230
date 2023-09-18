"""Context manager utilities for interacting with SQLite databases, using
the stdlib sqlite3 library.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3

from typing import Union

class SQLiteConnManager:
    """Handle interactions with a SQLite database.

    Uses built-in functions to query a database, execute SQL statements,
    and gracefully open/close the DB using context managers.

    Usage:
        Provide a path string to the SQLite database:
            sqlite_connection = SQLiteConnManager(path="/path/to/db.sqlite")

        Call sqlite3 functions, i.e. "get_tables()":
            tables = sqlite_conn.get_tables()
    """

    def __init__(self, path: Path):
        """Initialize SQLite connection manager."""
        self.path = path

    def __enter__(self):
        """Run when used like 'with SQLiteConnManager() as conn: ..."""
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.connection.cursor()

        ## Return self, a configured SQLite client
        return self

    def __exit__(self, exc_type, exc_val, exc_traceback):
        """Run on exit, success or failure."""
        self.connection.close()

    def get_cols(self, table: str = None) -> list[str]:
        """Return list of column names from a given table."""
        cols: list[str] = []
        stmt: str = f"SELECT * FROM {table}"

        try:
            with SQLiteConnManager(self.path) as conn:
                cursor = conn.cursor
                res = cursor.execute(stmt).fetchone()

                for col in res.keys():
                    cols.append(col)

                return cols

        except Exception as exc:
            raise Exception(f"Unhandled exception executing SQL. Details: {exc}")

    def get_tables(self) -> list[str]:
        """Get all table names from a SQLite databse."""
        get_tbls_stmt: str = "SELECT name FROM sqlite_master WHERE type='table';"
        tables: list[str] = []

        try:
            with SQLiteConnManager(self.path) as conn:
                cursor = conn.cursor
                res = cursor.execute(get_tbls_stmt).fetchall()

                for row in res:
                    tables.append(row["name"])

                return tables

        except Exception as exc:
            raise Exception(f"Unhandled exception getting tables. Details: {exc}")

    def run_sqlite_stmt(self, stmt: str = None) -> list[sqlite3.Row]:
        """Execute a SQL statement."""
        assert stmt, "Must pass a SQL statement"
        assert isinstance(stmt, str), "Statement must be a Python str"

        try:
            with SQLiteConnManager(self.path) as conn:
                cursor = conn.cursor
                res = cursor.execute(stmt).fetchall()

            return res
        except Exception as exc:
            raise Exception(
                f"Unhandled exception running SQL statement. Details: {exc}"
            )
