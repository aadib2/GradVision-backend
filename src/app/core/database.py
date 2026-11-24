"""
Database setup: engine, session factory, and the declarative Base
that gradvision_models.py builds on.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def normalize_database_url(url: str) -> str:
    """Rewrite Render-style Postgres URLs for SQLAlchemy + psycopg."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


# Swap this for your real Postgres URL in production / via env var.
# Example Postgres URL: postgresql+psycopg://user:pass@localhost:5432/gradvision
DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./gradvision.db")
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SQLite ignores foreign keys (incl. ON DELETE CASCADE) unless this is set per connection.
# Postgres enforces them already, so this only applies to local SQLite.
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect") # run this each time a new connection is made
    def _enable_sqlite_fks(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# FastAPI dependency: `db: Session = Depends(get_db)`
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
