#!/usr/bin/env python3
"""
Database initialization script for the Retail Management System.
Creates all database tables and initializes the database.
"""

from app import create_app
from app.extensions import db

def init_database():
    """Initialize the database with all tables."""
    print("🔧 Initializing database...")
    
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    init_database() 