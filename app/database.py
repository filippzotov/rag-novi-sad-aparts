from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base  # Import Base to create tables
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if they don't exist)
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency for getting a database session. Use this in your application
    to interact with the database.
    Example:
        db = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
