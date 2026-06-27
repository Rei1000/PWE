"""Engine und Session-Factory für PostgreSQL."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL ist nicht gesetzt")
    return url


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    url = database_url or get_database_url()
    engine = create_engine(url, future=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
