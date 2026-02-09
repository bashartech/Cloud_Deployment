from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

def get_database_url():
    """Get the database URL from environment variable with default fallback."""
    return os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

def get_engine():
    """Get the database engine, dynamically configured from environment."""
    database_url = get_database_url()
    return create_engine(database_url, echo=True)

# Global engine instance
engine = get_engine()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# @app.on_event("startup")
def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.

    This function creates the tables in the database based on the
    SQLModel classes defined throughout the application.
    It reloads the database URL from environment variables to ensure
    it connects to the correct database (Neon vs SQLite for testing).
    """
    global engine
    # Reload the engine to pick up any environment variable changes
    engine = get_engine()
    print(f"Creating database tables at: {get_database_url()}")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")