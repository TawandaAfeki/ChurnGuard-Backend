import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read database URL from environment variable ONLY
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine with Supabase-compatible settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Prevent stale connections
    pool_size=5,
    max_overflow=5,
    connect_args={
        "sslmode": "require"     # Supabase requires SSL
    },
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()
