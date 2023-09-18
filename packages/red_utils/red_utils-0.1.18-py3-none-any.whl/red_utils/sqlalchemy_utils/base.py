"""SQLAlchemy DeclarativeBase, MetaData, and registry objects.

Import this Base into SQLAlchemy model files and let classes inherit from
the DeclarativeBase declared here.

The registry() function sets the global SQLAlchemy registry for the DeclarativeBase object.

Docs for DeclarativeBase and registry():
https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html#using-a-declarative-base-class

Docs for MetaData object:
- Unified tutorial
    https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#tutorial-working-with-metadata
- MetaData Docs
    https://docs.sqlalchemy.org/en/20/core/metadata.html
- Impose a table naming scheme with MetaData object
    https://docs.sqlalchemy.org/en/20/core/metadata.html#specifying-a-default-schema-name-with-metadata
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, registry

## Global SQLAlchemy MetaData object
metadata: MetaData = MetaData()

## Registry object stores mappings & config hooks
reg = registry()


## SQLAlchemy DeclarativeBase is the parent class object table classes will inherit from
class Base(DeclarativeBase):
    """Default/Base class for SQLAlchemy models.

    Child classes inheriting from this Base object will be treated as SQLAlchemy
    models. Set child class tables with __tablename__ = ....

    Global defaults can be set on this object (i.e. a SQLAlchemy registry), and will
    be inherited/accessible by all child classes.
    """

    registry: registry = reg
    metadata: MetaData = metadata
