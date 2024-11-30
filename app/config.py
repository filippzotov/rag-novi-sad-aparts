import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://username:password@localhost:5432/cityexpert"
)
