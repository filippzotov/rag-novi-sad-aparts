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
                "prop_id": apartment.get("propId"),
                "url": apartment.get("url"),
                "price": apartment.get("price"),
                "size": apartment.get("size"),
                "rooms": apartment.get("structure"),
                "municipality": apartment.get("municipality"),
                "street": apartment.get("street"),
                "neighbourhoods": apartment.get("neighbourhoods", []),
                "floor": apartment.get("floor"),
                "year_of_construction": onsite.get("basInfYearOfConstruction", 0),
                "heating_options": onsite.get("heatingOptions", []),
                "deposit_amount": onsite.get("expDepositAmount"),
                "available_from": onsite.get("basInfAvailableFrom"),
                "cover_image": onsite.get("coverImage"),
                "youtube_video": onsite.get("youtubeVideo"),
                "description": onsite.get("addDescriptionSr"),
                # Features (Furniture and Appliances)
                "fur_washer": bool(onsite.get("furWasher", False)),
                "fur_oven": bool(onsite.get("furOven", False)),
                "fur_fridge": bool(onsite.get("furFridge", False)),
                "fur_tv": bool(onsite.get("furTV", False)),
                "fur_aircon": bool(onsite.get("furAircon", False)),
                "fur_french_bed": bool(onsite.get("furFrenchBed", False)),
                "fur_tub": bool(onsite.get("furTub", False)),
                "fur_pullout_bed": bool(onsite.get("furPullOutBed", False)),
                "fur_corner_sofa": bool(onsite.get("furCornerSofa", False)),
                "fur_dishwasher": bool(onsite.get("furDishWasher", False)),
                "fur_vacuum": bool(onsite.get("furVacuum", False)),
                # Building and Amenities
                "bldg_opts_elevator": bool(onsite.get("bldgOptsElevator", False)),
                "bldg_opts_intercom": bool(onsite.get("bldgOptsIntercom", False)),
                "bldg_opts_surveillance": bool(
                    onsite.get("bldgOptsSurveillance", False)
                ),
                "bldg_opts_ramp": bool(onsite.get("bldgOptsRamp", False)),
                # Pets and Business Usage
                "pets_allowed": bool(onsite.get("tolPets", False)),
                "business_usage_allowed": bool(onsite.get("tolBusiness", False)),
                # Parking and Distance
                "parking_in_price": onsite.get("basInfParkingInPrice", 0.0),
                "distance_to_center": onsite.get("basInfDistanceCenter"),
                # Additional Information
                "shared_entrance": bool(onsite.get("basInfSharedEntrance", False)),
                "shared_electricity_meter": bool(
                    onsite.get("basInfSharedElectricityMeter", False)
                ),
                "renovated": bool(onsite.get("basInfRenovated", False)),
                "num_bathrooms": onsite.get("numBathrooms", 0),
                "num_bedrooms": onsite.get("numBedrooms", 0),
                "num_toilets": onsite.get("numToilets", 0),
                "total_floors": onsite.get("basInfFloorTotal", 0),
                # Expiry and Leasing Info
                "min_lease": onsite.get("tolMinLease"),
                "max_lease": onsite.get("tolMaxLease"),
                "max_tenants": onsite.get("tolMaxTenants"),
            }

            # Check if the apartment already exists
            existing = (
                db.query(Apartment)
                .filter_by(prop_id=transformed_apartment["prop_id"])
                .first()
            )
            if existing:
                # Update existing record
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
