from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Used on startup for the dev/SQLite path.

    For Postgres in production, prefer Alembic migrations
    (see backend/alembic/) instead of relying on create_all.
    """
    import app.models  # noqa: F401 ensures all models are registered
    Base.metadata.create_all(bind=engine)
    columns = {column["name"] for column in inspect(engine).get_columns("registration_otp_challenges")}
    if "verified" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE registration_otp_challenges "
                "ADD COLUMN verified BOOLEAN NOT NULL DEFAULT FALSE"
            ))
