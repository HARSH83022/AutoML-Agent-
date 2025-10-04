from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite database
DATABASE_URL = "sqlite:///memory.db"

Base = declarative_base()

# Event model
class Event(Base):
    __tablename__ = "events"

    run_id = Column(String, primary_key=True)
    agent = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
if __name__ == "__main__":
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("✅ Database initialized with events table")
