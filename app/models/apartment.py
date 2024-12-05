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
from app.models.base import Base
from datetime import datetime


class Apartment(Base):
    __tablename__ = "apartments"

    # Primary Fields
    property_id = Column(Integer, primary_key=True, nullable=False)  # Matches 'propId'
    listing_url = Column(Text, nullable=True)  # Apartment URL
    price_per_month = Column(Float)  # Price of the apartment
    size_sqm = Column(Float)  # Size in square meters
    room_count = Column(String(10))  # Apartment structure (e.g., "1.0", "3.5")
    municipality_name = Column(String(255))  # Municipality
    street_name = Column(String(255))  # Street name
    neighborhoods = Column(ARRAY(Text))  # Neighborhoods
    floor_number = Column(String(10))  # Floor number
    construction_year = Column(Integer)  # Year of construction
    heating_types = Column(ARRAY(Text))  # Heating options
    deposit = Column(Float)  # Deposit amount
    available_date = Column(DateTime)  # Availability date
    cover_image_url = Column(Text)  # Cover photo URL
    youtube_video_url = Column(Text)  # YouTube video URL
    description_text = Column(Text)  # Description (if available)
    created_date = Column(DateTime, default=datetime.utcnow)  # Auto-set timestamp

    # Features (Furniture and Appliances)
    has_washing_machine = Column(Boolean, default=False)  # Washing machine
    has_oven = Column(Boolean, default=False)  # Oven
    has_fridge = Column(Boolean, default=False)  # Fridge
    has_tv = Column(Boolean, default=False)  # TV
    has_air_conditioning = Column(Boolean, default=False)  # Air conditioner
    has_french_bed = Column(Boolean, default=False)  # French bed
    has_bathtub = Column(Boolean, default=False)  # Bathtub
    has_pullout_bed = Column(Boolean, default=False)  # Pull-out bed
    has_corner_sofa = Column(Boolean, default=False)  # Corner sofa
    has_dishwasher = Column(Boolean, default=False)  # Dishwasher
    has_vacuum_cleaner = Column(Boolean, default=False)  # Vacuum cleaner

    # Building and Amenities
    has_elevator = Column(Boolean, default=False)  # Elevator
    has_intercom = Column(Boolean, default=False)  # Intercom
    has_surveillance = Column(Boolean, default=False)  # Surveillance
    has_wheelchair_ramp = Column(Boolean, default=False)  # Wheelchair ramp

    # Pets and Business Usage
    allows_pets = Column(Boolean, default=False)  # Whether pets are allowed
    allows_business_use = Column(Boolean, default=False)  # For business usage

    # Parking and Distance
    parking_cost = Column(Float, default=0.0)  # Parking included in price
    distance_to_city_center_m = Column(Integer)  # Distance to city center in meters

    # Additional Information
    has_shared_entrance = Column(Boolean, default=False)  # Shared entrance
    has_shared_electricity_meter = Column(Boolean, default=False)  # Shared electricity
    is_renovated = Column(Boolean, default=False)  # Renovated
    bathroom_count = Column(Integer, default=0)  # Number of bathrooms
    bedroom_count = Column(Integer, default=0)  # Number of bedrooms
    toilet_count = Column(Integer, default=0)  # Number of toilets
    total_floors_in_building = Column(
        Integer, default=0
    )  # Total floors in the building

    # Expiry and Leasing Info
    minimum_lease_duration = Column(Integer, default=None)  # Minimum lease duration
    maximum_lease_date = Column(DateTime, default=None)  # Maximum lease duration
    max_number_of_tenants = Column(Integer, default=None)  # Maximum number of tenants
