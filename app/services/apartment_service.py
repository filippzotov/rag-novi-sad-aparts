from app.models import Apartment
from app.database import SessionLocal
from sqlalchemy.exc import IntegrityError
from pprint import pprint


def save_apartments(apartments):
    db = SessionLocal()
    for apartment in apartments:
        try:
            # Extracting values from the 'onsite' dictionary
            onsite = apartment.get("onsite", {})

            transformed_apartment = {
                # Primary Fields
                "property_id": apartment.get("propId"),
                "listing_url": apartment.get("url"),
                "price_per_month": apartment.get("price"),
                "size_sqm": apartment.get("size"),
                "room_count": apartment.get("structure"),
                "municipality_name": apartment.get("municipality"),
                "street_name": apartment.get("street"),
                "neighborhoods": apartment.get("neighbourhoods", []),
                "floor_number": apartment.get("floor"),
                "construction_year": onsite.get("basInfYearOfConstruction", 0),
                "heating_types": onsite.get("heatingOptions", []),
                "deposit": onsite.get("expDepositAmount"),
                "available_date": onsite.get("basInfAvailableFrom"),
                "cover_image_url": onsite.get("coverImage"),
                "youtube_video_url": onsite.get("youtubeVideo"),
                "description_text": onsite.get("addDescriptionSr"),
                # Features (Furniture and Appliances)
                "has_washing_machine": bool(onsite.get("furWasher", False)),
                "has_oven": bool(onsite.get("furOven", False)),
                "has_fridge": bool(onsite.get("furFridge", False)),
                "has_tv": bool(onsite.get("furTV", False)),
                "has_air_conditioning": bool(onsite.get("furAircon", False)),
                "has_french_bed": bool(onsite.get("furFrenchBed", False)),
                "has_bathtub": bool(onsite.get("furTub", False)),
                "has_pullout_bed": bool(onsite.get("furPullOutBed", False)),
                "has_corner_sofa": bool(onsite.get("furCornerSofa", False)),
                "has_dishwasher": bool(onsite.get("furDishWasher", False)),
                "has_vacuum_cleaner": bool(onsite.get("furVacuum", False)),
                # Building and Amenities
                "has_elevator": bool(onsite.get("bldgOptsElevator", False)),
                "has_intercom": bool(onsite.get("bldgOptsIntercom", False)),
                "has_surveillance": bool(onsite.get("bldgOptsSurveillance", False)),
                "has_wheelchair_ramp": bool(onsite.get("bldgOptsRamp", False)),
                # Pets and Business Usage
                "allows_pets": bool(onsite.get("tolPets", False)),
                "allows_business_use": bool(onsite.get("tolBusiness", False)),
                # Parking and Distance
                "parking_cost": onsite.get("basInfParkingInPrice", 0.0),
                "distance_to_city_center_m": onsite.get("basInfDistanceCenter"),
                # Additional Information
                "has_shared_entrance": bool(onsite.get("basInfSharedEntrance", False)),
                "has_shared_electricity_meter": bool(
                    onsite.get("basInfSharedElectricityMeter", False)
                ),
                "is_renovated": bool(onsite.get("basInfRenovated", False)),
                "bathroom_count": onsite.get("numBathrooms", 0),
                "bedroom_count": onsite.get("numBedrooms", 0),
                "toilet_count": onsite.get("numToilets", 0),
                "total_floors_in_building": onsite.get("basInfFloorTotal", 0),
                # Expiry and Leasing Info
                "minimum_lease_duration": onsite.get("tolMinLease"),
                "maximum_lease_date": onsite.get("tolMaxLease"),
                "max_number_of_tenants": onsite.get("tolMaxTenants"),
            }

            # Check if the apartment already exists
            existing = (
                db.query(Apartment)
                .filter_by(property_id=transformed_apartment["property_id"])
                .first()
            )
            if existing:
                # Update existing record
                print(
                    f"Debug: Apartment with property_id {transformed_apartment['property_id']} exists. Updating record."
                )
                for key, value in transformed_apartment.items():
                    setattr(existing, key, value)
            else:
                # Add new apartment
                new_apartment = Apartment(**transformed_apartment)
                db.add(new_apartment)

        except IntegrityError as e:
            db.rollback()  # Skip problematic apartment but maintain the transaction for others
            print(f"IntegrityError for apartment {apartment.get('propId')}: {e}")
        except Exception as e:
            db.rollback()
            print(
                f"Unexpected error for apartment {apartment.get('propId', 'Unknown')}: {e}"
            )

    try:
        # Commit changes to the database
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during commit: {e}")
    finally:
        db.close()


def delete_all_apartments():
    db = SessionLocal()
    try:
        # Delete all records from the apartments table
        db.query(Apartment).delete()
        db.commit()
        print("All apartments have been deleted from the database.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred while deleting apartments: {e}")
    finally:
        db.close()
