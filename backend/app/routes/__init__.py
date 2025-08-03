#!/usr/bin/env python3
"""
Routes package for Retail Management System.

This package contains all Flask Blueprint routes for the application.
"""

from .auth import auth_bp
from .users import users_bp

__all__ = [
    'auth_bp',
    'users_bp'
] 