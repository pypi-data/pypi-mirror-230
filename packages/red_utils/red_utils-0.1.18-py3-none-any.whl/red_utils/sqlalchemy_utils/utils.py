from __future__ import annotations

from typing import Any, Optional, Union

from .connection_models import (
    saConnectionGeneric,
    saMSSQLConnection,
    saPGConnection,
    saSQLiteConnection,
)
from .constants import valid_db_types

import sqlalchemy as sa

from sqlalchemy import (
    create_engine,
    orm as sa_orm,
)

## Import SQLAlchemy exceptions
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import CreateTable

def debug_metadata_obj(metadata_obj: sa.MetaData = None) -> None:
    """Debug-print a SQLAlchemy MetaData object.

    Loop over tables and print names.
    """
    if not metadata_obj:
        raise ValueError("Missing a SQLAlchemy metadata object.")

    if not isinstance(metadata_obj, sa.MetaData):
        raise ValueError(
            f"Expected a MetaData obj, not object of type '{type(metadata_obj).__name__}'"
        )

    for _table in metadata_obj.sorted_tables:
        print(f"Table name: {_table.name}")


## Ensure a supported database is used
def validate_db_type(in_str: str = None) -> bool:
    """Validate db_type string in functions that utilize db_type."""
    if not in_str:
        raise ValueError("Missing input string to validate")

    if in_str not in valid_db_types:
        return False

    return True


def generate_metadata(
    metadata_obj: sa.MetaData = None, engine: sa.Engine = None
) -> None:
    """Create SQLAlchemy table metadata.

    Accept a SQLalchemy MetaData object, run .create_all(engine) to create
    table metadata.
    """
    if not metadata_obj:
        raise ValueError("Missing a SQLAlchemy MetaData object.")

    if not isinstance(metadata_obj, sa.MetaData):
        raise ValueError(
            f"Expected a MetaData obj, not object of type '{type(metadata_obj).__name__}'"
        )

    if not engine:
        raise ValueError("Missing a SQLAlchemy engine object.")

    if not isinstance(engine, sa.Engine):
        raise ValueError(
            f"Expected a SQLAlchemy engine obj, not object of type '{type(engine).__name__}"
        )

    try:
        metadata_obj.create_all(engine)

        return True
    except OperationalError as op_exc:
        raise op_exc
    except DBAPIError as dbapi_exc:
        raise dbapi_exc
    except Exception as exc:
        raise Exception(f"Unhandled exception creating Base metadata. Details: {exc}")


def create_base_metadata(
    base_obj: sa_orm.DeclarativeBase = None, engine: sa.Engine = None
) -> bool:
    """Create Base object's metadata.

    Import this function early in your app/script (i.e. main.py) and run as soon as
    possible, i.e. after imports.

    This function accepts a SQLAlchemy DeclarativeBase object, and creates the table
    metadata from that object using the engine passed.

    This function will only ever return True if successful. It does not return False,
    as an exception is raised if metadata creation fails and the program is halted.
    """
    try:
        base_obj.metadata.create_all(bind=engine)

        return True
    except OperationalError as op_exc:
        raise op_exc
    except DBAPIError as dbapi_exc:
        raise dbapi_exc
    except Exception as exc:
        raise Exception(f"Unhandled exception creating Base metadata. Details: {exc}")


def get_engine(
    connection: Union[saSQLiteConnection, saPGConnection, str] = None,
    db_type: str = "sqlite",
    echo: bool = False,
    pool_pre_ping: bool = False,
) -> sa.Engine:
    """Return a SQLAlchemy Engine object.

    https://docs.sqlalchemy.org/en/20/tutorial/engine.html

    To use a database other than SQLite, i.e. Postgres or MySQL, pass
    the lowercase string name of the database.

    Currently supported:
        - [x] SQLite
        - [x] Postgres
        - [ ] MySQL
        - [x] MSSQL
        - [ ] Azure Cosmos
    """
    if not connection:
        raise ValueError("Missing connection object/string.")

    if isinstance(connection, str):
        if db_type == "sqlite":
            connection: saSQLiteConnection = saSQLiteConnection(database=connection)

    ## Validate db_type input
    if db_type:
        _valid: bool = validate_db_type(db_type)

        if not _valid:
            raise ValueError(
                f"Invalid db_type: {db_type}. Must be one of: {valid_db_types}"
            )

    else:
        ## Default to sqlite if no db_type is passed
        db_type = "sqlite"

    if db_type == "sqlite":
        ## Ensure path to database file exists
        connection.ensure_path()

    if db_type == "postgres":
        pass

    if db_type == "mssql":
        pass

    try:
        engine = create_engine(
            connection.connection_string, echo=echo, pool_pre_ping=pool_pre_ping
        )

        return engine

    except OperationalError as op_exc:
        raise OperationalError(
            f"SQLAlchemy OperationalError exception occurred connecting to database {connection.database}. Details: {op_exc}"
        )

    except Exception as exc:
        raise Exception(f"Unhandled exception creating database engine. Details: {exc}")


def get_session(
    engine: sa.Engine = None,
    autoflush: bool = False,
    expire_on_commit: bool = False,
    class_=Session,
) -> sessionmaker[Session]:
    """Define a factory for creating SQLAlchemy sessions.

    Returns a sqlalchemy.orm.sessionmaker Session instance. Import this
    function in scripts that interact with the database, and create a
    SessionLocal object with SessionLocal = get_session(**args)
    """
    try:
        _sess = sessionmaker(
            bind=engine,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            class_=class_,
        )

        return _sess
    except Exception as exc:
        raise Exception(
            f"Unhandled exception creating a sessionmaker Session. Details: {exc}"
        )
