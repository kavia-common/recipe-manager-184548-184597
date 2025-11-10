"""Database setup for the Recipe Backend using SQLAlchemy.

This module configures the SQLite database connection, session factory,
and base class for ORM models. It is intentionally minimal and requires no
migrations for this task.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Determine database file path within the container project directory.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_FILE = os.getenv("RECIPE_DB_FILE", str(DATA_DIR / "recipes.db"))

# SQLite connection URL.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# Create SQLAlchemy engine with SQLite-specific options.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
