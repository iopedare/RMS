#!/usr/bin/env python3
"""
Database session management for Retail Management System.

This module provides database session management and utilities
for the application.
"""

from flask import g
from app.extensions import db

def get_db_session():
    """
    Get database session.
    
    Returns:
        SQLAlchemy session object
    """
    if 'db' not in g:
        g.db = db.session
    return g.db

def close_db_session(error=None):
    """
    Close database session.
    
    Args:
        error: Error that occurred (if any)
    """
    db_session = g.pop('db', None)
    if db_session is not None:
        db_session.close() 