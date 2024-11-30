from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ARRAY,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True)  # Auto-incrementing ID
    prop_id = Column(Integer, unique=True, nullable=False)  # Unique property ID
    price = Column(Float)
    size = Column(Float)
    structure = Column(String(10))
    municipality = Column(String(255))
    street = Column(String(255))
    neighbourhoods = Column(ARRAY(Text))  # List of neighbourhoods
    floor = Column(String(10))
    year_of_construction = Column(Integer)
    heating_options = Column(ARRAY(Text))  # List of heating options
    deposit_amount = Column(Float)
    available_from = Column(DateTime)
    cover_image = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-generated timestamp
