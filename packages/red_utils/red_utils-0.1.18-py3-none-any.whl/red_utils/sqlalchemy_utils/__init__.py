"""SQLAlchemy common database code.

Contains SQLAlchemy setup code, engine, and session(s). Uses dataclasses to define
database connection, and builds a default engine & session. The use of dataclasses is
to minimize depdencies for this common SQLAlchemy code so it can be easily re-used in
other projects utilizing SQLAlchemy for database operations.

The default engine and session are customizable using the get_engine() and get_session()
functions. These functions can be imported & called from another app, with customized
values to control engine & session behavior.

Currently supported databases:
    - [x] SQLite
    - [x] Postgres
    - [ ] MySQL
    - [x] MSSQL
    - [ ] Azure Cosmos
    
Be sure to import the Base object from this script and run Base.metadata.create_all(bind=engine)
as early as possible. For example, import the Base object from this script into main.py,
create/import an engine, and immediately run the metadata create function.
"""
from __future__ import annotations

from . import custom_types

## Import SQLAlchemy dependencies
## Import SQLAlchemy DeclarativeBase object
from .base import Base

## Import SQLAlchemy connection classes
from .connection_models import (
    saConnectionGeneric,
    saMSSQLConnection,
    saPGConnection,
    saSQLiteConnection,
)

## Import constants
from .constants import valid_db_types
from .custom_types import CompatibleUUID

## Import custom SQLAlchemy utils
from .utils import (
    create_base_metadata,
    debug_metadata_obj,
    generate_metadata,
    get_engine,
    get_session,
    validate_db_type,
)

import sqlalchemy as sa

from sqlalchemy import (
    create_engine,
    orm as sa_orm,
)
from sqlalchemy.orm import Session, scoped_session, sessionmaker
