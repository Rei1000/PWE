"""PostgreSQL-Persistenz-Adapter (Gate 5)."""

from adapters.persistence.postgresql.engine import create_session_factory, get_database_url
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from adapters.persistence.postgresql.schema import init_schema

__all__ = [
    "PostgresKatalogRepository",
    "PostgresPrueflaufRepository",
    "PostgresProtokollRepository",
    "create_session_factory",
    "get_database_url",
    "init_schema",
]
