#!/usr/bin/env python3
"""
Authentication Middleware for Retail Management System.

This middleware handles JWT token validation, user context management,
and authentication for Flask API endpoints.
"""

from functools import wraps
from flask import request, jsonify, g, current_app
from app.services.auth_service import AuthService
from app.services.authorization_service import AuthorizationService
from app.services.session_service import SessionService
from sqlalchemy.orm import Session
import jwt


def auth_required(f):
    """
    Decorator to require authentication for an endpoint.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        # Get token from request
        token = _get_token_from_request()
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Verify token
        auth_service = AuthService(db_session)
        is_valid, user_data, error = auth_service.verify_token(token)
        
        if not is_valid:
            return jsonify({'error': error or 'Invalid authentication token'}), 401
        
        # Set user context in Flask g object
        g.user_id = user_data.get('id')
        g.user_data = user_data
        g.db = db_session
        
        return f(*args, **kwargs)
    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication - endpoint works with or without auth.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        # Get token from request
        token = _get_token_from_request()
        
        if token:
            # Verify token if provided
            auth_service = AuthService(db_session)
            is_valid, user_data, error = auth_service.verify_token(token)
            
            if is_valid:
                # Set user context in Flask g object
                g.user_id = user_data.get('id')
                g.user_data = user_data
                g.db = db_session
            else:
                # Token is invalid, but don't fail the request
                g.user_id = None
                g.user_data = None
        else:
            # No token provided
            g.user_id = None
            g.user_data = None
        
        return f(*args, **kwargs)
    return decorated_function


def network_auth_required(f):
    """
    Decorator for network-based authentication - checks if admin exists for network.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        # Check if admin exists for this network
        auth_service = AuthService(db_session)
        admin_exists = auth_service.check_network_admin_exists()
        
        if not admin_exists:
            return jsonify({
                'error': 'No admin user found for this network',
                'requires_admin_registration': True
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


def setup_auth_middleware(app, db_session_factory):
    """
    Setup authentication middleware for Flask app.
    
    Args:
        app: Flask application
        db_session_factory: Database session factory
    """
    
    @app.before_request
    def before_request():
        """Set up database session and user context before each request."""
        # Create database session
        db_session = db_session_factory()
        g.db = db_session
        
        # Set default user context
        g.user_id = None
        g.user_data = None
    
    @app.after_request
    def after_request(response):
        """Clean up after each request."""
        # Close database session
        db_session = getattr(g, 'db', None)
        if db_session:
            db_session.close()
        
        return response
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized requests."""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden requests."""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403


def _get_token_from_request() -> str:
    """
    Extract JWT token from request headers or query parameters.
    
    Returns:
        Token string or None if not found
    """
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        elif auth_header.startswith('Token '):
            return auth_header[6:]  # Remove 'Token ' prefix
    
    # Check query parameter
    token = request.args.get('token')
    if token:
        return token
    
    # Check form data
    token = request.form.get('token')
    if token:
        return token
    
    # Check JSON body
    if request.is_json:
        data = request.get_json()
        if data and 'token' in data:
            return data['token']
    
    return None


def get_current_user():
    """
    Get current user information from request context.
    
    Returns:
        User data dictionary or None if not authenticated
    """
    return getattr(g, 'user_data', None)


def get_current_user_id():
    """
    Get current user ID from request context.
    
    Returns:
        User ID or None if not authenticated
    """
    return getattr(g, 'user_id', None)


def get_user_context():
    """
    Get comprehensive user context including roles and permissions.
    
    Returns:
        User context dictionary or empty dict if not authenticated
    """
    user_id = get_current_user_id()
    if not user_id:
        return {}
    
    db_session = getattr(g, 'db', None)
    if not db_session:
        return {}
    
    auth_service = AuthorizationService(db_session)
    return auth_service.get_user_context(user_id)


def validate_session():
    """
    Validate current user session.
    
    Returns:
        Tuple of (valid, error_message)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "No authenticated user"
    
    user_data = get_current_user()
    if not user_data:
        return False, "Invalid user data"
    
    session_id = user_data.get('session_id')
    if not session_id:
        return False, "No session ID"
    
    db_session = getattr(g, 'db', None)
    if not db_session:
        return False, "Database session not available"
    
    session_service = SessionService(db_session)
    return session_service.validate_session(user_id, session_id)


def refresh_user_session():
    """
    Refresh current user session.
    
    Returns:
        Tuple of (success, error_message)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "No authenticated user"
    
    user_data = get_current_user()
    if not user_data:
        return False, "Invalid user data"
    
    session_id = user_data.get('session_id')
    if not session_id:
        return False, "No session ID"
    
    db_session = getattr(g, 'db', None)
    if not db_session:
        return False, "Database session not available"
    
    session_service = SessionService(db_session)
    return session_service.refresh_session(user_id, session_id)


def log_auth_event(event_type: str, description: str, is_success: str = "success", **kwargs):
    """
    Log authentication event.
    
    Args:
        event_type: Type of authentication event
        description: Event description
        is_success: Success status ('success' or 'failure')
        **kwargs: Additional event parameters
    """
    user_id = get_current_user_id()
    db_session = getattr(g, 'db', None)
    
    if db_session and user_id:
        auth_service = AuthService(db_session)
        auth_service._log_auth_event(
            event_type=event_type,
            description=description,
            is_success=is_success,
            user_id=user_id,
            **kwargs
        ) 