import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from fastapi import HTTPException


def normalize_database_url(url: str) -> str:
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = (
    create_engine(
        normalize_database_url(DATABASE_URL),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5}
        if DATABASE_URL.startswith(("postgres",))
        else {},
    )
    if DATABASE_URL
    else None
)
SessionLocal = (
    sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None
)


class Base(DeclarativeBase):
    pass


def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
