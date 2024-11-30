from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ARRAY
from app.models.base import Base
from datetime import datetime


class Apartment(Base):
    __tablename__ = "apartments"

    prop_id = Column(
        Integer, primary_key=True, nullable=False
    )  # Matches 'propId' from API and is now the primary key
    url = Column(Text, nullable=True)
    price = Column(Float)  # Price of the apartment
    size = Column(Float)  # Size in square meters
    rooms = Column(String(10))  # Apartment structure (e.g., "1.0", "3.5")
    municipality = Column(String(255))  # Municipality (e.g., "Novi Sad")
    street = Column(String(255))  # Street name
    neighbourhoods = Column(ARRAY(Text))  # Use 'neighbourhoods' field from API
    floor = Column(String(10))  # Floor number
    year_of_construction = Column(Integer)  # Year of construction
    heating_options = Column(ARRAY(Text))  # Use 'heatingOptions' from API
    deposit_amount = Column(Float)  # Deposit amount (e.g., 'expDepositAmount')
    available_from = Column(
        DateTime
    )  # Date when the apartment is available (e.g., 'basInfAvailableFrom')
    cover_image = Column(Text)  # Cover photo URL (e.g., 'onsite.coverImage')
    description = Column(Text)  # Description (if available)
    youtube_video = Column(Text)  # YouTube video URL (e.g., 'onsite.youtubeVideo')
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-set timestamp
