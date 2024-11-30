from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ARRAY
from app.models.base import Base
from datetime import datetime


from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    String,
    ARRAY,
    DateTime,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Apartment(Base):
    __tablename__ = "apartments"

    # Primary Fields
    prop_id = Column(Integer, primary_key=True, nullable=False)  # Matches 'propId'
    url = Column(Text, nullable=True)  # Apartment URL
    price = Column(Float)  # Price of the apartment
    size = Column(Float)  # Size in square meters
    rooms = Column(String(10))  # Apartment structure (e.g., "1.0", "3.5")
    municipality = Column(String(255))  # Municipality
    street = Column(String(255))  # Street name
    neighbourhoods = Column(ARRAY(Text))  # Neighbourhoods
    floor = Column(String(10))  # Floor number
    year_of_construction = Column(Integer)  # Year of construction
    heating_options = Column(ARRAY(Text))  # Heating options
    deposit_amount = Column(Float)  # Deposit amount
    available_from = Column(DateTime)  # Availability date
    cover_image = Column(Text)  # Cover photo URL
    youtube_video = Column(Text)  # YouTube video URL
    description = Column(Text)  # Description (if available)
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-set timestamp

    # Features (Furniture and Appliances)
    fur_washer = Column(Boolean, default=False)  # Washing machine
    fur_oven = Column(Boolean, default=False)  # Oven
    fur_fridge = Column(Boolean, default=False)  # Fridge
    fur_tv = Column(Boolean, default=False)  # TV
    fur_aircon = Column(Boolean, default=False)  # Air conditioner
    fur_french_bed = Column(Boolean, default=False)  # French bed
    fur_tub = Column(Boolean, default=False)  # Bathtub
    fur_pullout_bed = Column(Boolean, default=False)  # Pull-out bed
    fur_corner_sofa = Column(Boolean, default=False)  # Corner sofa
    fur_dishwasher = Column(Boolean, default=False)  # Dishwasher
    fur_vacuum = Column(Boolean, default=False)  # Vacuum cleaner

    # Building and Amenities
    bldg_opts_elevator = Column(Boolean, default=False)  # Elevator
    bldg_opts_intercom = Column(Boolean, default=False)  # Intercom
    bldg_opts_surveillance = Column(Boolean, default=False)  # Surveillance
    bldg_opts_ramp = Column(Boolean, default=False)  # Wheelchair ramp

    # Pets and Business Usage
    pets_allowed = Column(Boolean, default=False)  # Whether pets are allowed
    business_usage_allowed = Column(Boolean, default=False)  # For business usage

    # Parking and Distance
    parking_in_price = Column(Float, default=0.0)  # Parking included in price
    distance_to_center = Column(Integer)  # Distance to city center in meters

    # Additional Information
    shared_entrance = Column(Boolean, default=False)  # Shared entrance
    shared_electricity_meter = Column(Boolean, default=False)  # Shared electricity
    renovated = Column(Boolean, default=False)  # Renovated
    num_bathrooms = Column(Integer, default=0)  # Number of bathrooms
    num_bedrooms = Column(Integer, default=0)  # Number of bedrooms
    num_toilets = Column(Integer, default=0)  # Number of toilets
    total_floors = Column(Integer, default=0)  # Total floors in the building

    # Expiry and Leasing Info
    min_lease = Column(Integer, default=None)  # Minimum lease duration
    max_lease = Column(Integer, default=None)  # Maximum lease duration
    max_tenants = Column(Integer, default=None)  # Maximum number of tenants

    def __repr__(self):
        return (
            f"<Apartment(prop_id={self.prop_id}, price={self.price}, size={self.size})>"
        )
