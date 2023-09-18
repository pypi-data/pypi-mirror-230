from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import sqlalchemy as sa

@dataclass
class saConnectionBase:
    """Base class for SQLAlchemy connection models.

    Each model will inherit the connection_string propery,
    which outputs a URL conection object.
    """

    drivername: str = field(default=None)
    host: str = field(default=None)
    username: str = field(default=None)
    ## Hide password from __repr__
    password: str = field(default=None, repr=False)
    port: int = field(default=None)
    database: str = field(default=None)

    @property
    def connection_string(self) -> sa.engine.url.URL:
        _string: sa.engine.url.URL = sa.engine.url.URL.create(
            drivername=self.drivername,
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            database=self.database,
        )

        return _string

    def __post_init__(self):
        """Dataclasses does not have inbuilt validation for class variables.

        Define validator functions below. Classes that inherit from this
        base class will pass their values through these validators as well.

        https://www.slingacademy.com/article/python-how-to-validate-data-in-dataclass/
        """
        if self.drivername and not isinstance(self.drivername, str):
            raise TypeError(
                f"Drivername should be of type str, not {type(self.drivername).__name__}"
            )

        if self.username and not isinstance(self.username, str):
            raise TypeError(
                f"Username should be of type str, not {type(self.username).__name__}"
            )

        if self.password and not isinstance(self.password, str):
            raise TypeError(
                f"Password should be of type str, not {type(self.password).__name__}"
            )

        if self.host and not isinstance(self.host, str):
            raise TypeError(
                f"Host should be of type str, not {type(self.host).__name__}"
            )

        if self.port and not isinstance(self.port, int):
            raise TypeError(
                f"Port should be of type int, not {type(self.port).__name__}"
            )

        if self.port and (self.port <= 0 or self.port > 65535):
            raise ValueError("Port number must be between 1 and 65535")

        if self.database and not isinstance(self.database, str):
            raise TypeError(
                f"Database should be of type str, not {type(self.database).__name__}"
            )


class saConnectionGeneric(saConnectionBase):
    """Generic SQLAlchemy connection class.

    Inherits settings & properties from the base class, and can be
    extended if none of the other saConnection* models meet needs.
    """

    pass


@dataclass
class saSQLiteConnection(saConnectionBase):
    """Default SQLite connection. Useful for local testing.

    Accepts 2 values:
        - drivername: The SQLAlchemy driver string for the database
        - database: The name/path to the SQLite database.
            It is recommended to use .sqlite for the file extension,
            although .db or any other should work fine as well.

    Pass a value for $database to change the name of the database file.
    If you use a path (i.e. db/test.sqlite), you need to create the Path
    manually.
    """

    drivername: str = field(default="sqlite+pysqlite")
    database: str = field(default="default_unnamed.sqlite")

    def ensure_path(self) -> None:
        """Ensure path to self.database exists.

        Use Path() to split the directory path
        from the filename, and ensure directores in path
        exist.
        """
        ## Get absolute path to immediate parent directory without filename.
        _path = Path(self.database).parent.absolute()

        ## Create directories along path if they do not exist
        if not _path.exists():
            try:
                _path.mkdir(parents=True, exist_ok=True)
            except PermissionError as perm_exc:
                raise PermissionError(
                    f"Permission error trying to open {str(_path)}. Details: {perm_exc}"
                )
            except Exception as exc:
                raise Exception(
                    f"Unhandled exception creating directories in path: {str(_path)}. Details: {exc}"
                )


@dataclass
class saPGConnection(saConnectionBase):
    """Default Postgres connection. Useful for local testing.

    For Postgres databases, the database you specify must exist before
    creating the initial connection/engine.
    """

    drivername: str = field(default="postgresql+psycopg2")
    username: str = field(default="postgres")
    ## Hide password from __repr__
    password: str = field(default="postgres", repr=False)
    host: str = field(default="127.0.0.1")
    port: int = field(default=5432)
    database: str = field(default="postgres")


@dataclass
class saMSSQLConnection(saConnectionBase):
    drivername: str = field(default="mssql+pyodbc")
    username: str = field(default="SA")
    ## Hide password from __repr__
    password: str = field(default="1Secure*Password1", repr=False)
    host: str = field(default="127.0.0.1")
    # instance: str = field(default="\\SQLEXPRESS")
    port: int = field(default=1433)
    database: str = field(default="master")

    @property
    def connection_string(self) -> sa.engine.url.URL:
        _string: sa.engine.url.URL = sa.engine.url.URL.create(
            drivername=self.drivername,
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            database=self.database,
            query=dict(driver="ODBC Driver 17 for SQL Server"),
        )

        return _string
