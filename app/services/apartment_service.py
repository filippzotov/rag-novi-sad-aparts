from app.models import Apartment
from app.database import SessionLocal
from sqlalchemy.exc import IntegrityError


def save_apartments(apartments):
    db = SessionLocal()
    for apartment in apartments:
        try:
            transformed_apartment = {
                "prop_id": apartment.get("propId"),
                "price": apartment.get("price"),
                "size": apartment.get("size"),
                "rooms": apartment.get("structure"),
                "municipality": apartment.get("municipality"),
                "street": apartment.get("street"),
                "neighbourhoods": apartment.get("neighbourhoods", []),
                "floor": apartment.get("floor"),
                "year_of_construction": apartment.get("yearOfConstruction"),
                "heating_options": apartment.get("heatingOptions", []),
                "deposit_amount": apartment.get("expDepositAmount"),
                "available_from": apartment.get("basInfAvailableFrom"),
                "cover_image": apartment.get("onsite", {}).get("coverImage"),
                "description": apartment.get("addDescriptionSr"),
                "url": apartment.get("url"),
                "youtube_video": apartment.get("onsite", {}).get("youtubeVideo"),
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
