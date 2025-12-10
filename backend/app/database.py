from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- DATABASE CONNECTION STRING ---
# Format: postgresql://<username>:<password>@<host>/<database_name>
# REPLACE 'your_password' with the password you set during installation.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgress@localhost/edugen_db"

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class
# Each instance of this class will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
Base = declarative_base()

# Dependency function to get a database session for a request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()