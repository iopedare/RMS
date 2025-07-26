import sys
import os

# Ensure the backend/app directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def list_tables():
    app = create_app()
    with app.app_context():
        engine = db.get_engine()
        # Use SQLAlchemy's inspector for compatibility
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in the database:", tables)

if __name__ == "__main__":
    list_tables() 