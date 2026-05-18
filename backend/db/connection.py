from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create engine (SQLite-specific arguments are supplied dynamically if SQLite is chosen)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
