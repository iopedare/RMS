from sqlalchemy.orm import declarative_base

# This is the base class for all SQLAlchemy ORM models in the backend.
# All models should inherit from this Base to ensure consistent metadata and table creation.
Base = declarative_base() 