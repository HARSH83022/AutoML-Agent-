from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# --------------------------
# Database Setup
# --------------------------

# Default SQLite database (stored in project root as memory.db)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./memory.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --------------------------
# Models
# --------------------------

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String, unique=True, index=True)  # unique per run
    user_id = Column(String, index=True)
    mode = Column(String)
    problem_statement = Column(String)
    preferences = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ✅ PK
    run_id = Column(String, index=True)  # ✅ not unique (allows many events per run)
    agent = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String, index=True)
    kind = Column(String)
    uri = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# --------------------------
# Create Tables
# --------------------------

def init_db():
    """Initialize the database (create tables if they don't exist)."""
    Base.metadata.create_all(bind=engine)
