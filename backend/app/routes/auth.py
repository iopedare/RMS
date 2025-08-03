#!/usr/bin/env python3
"""
Authentication routes for Retail Management System.

This module provides REST API endpoints for user authentication,
session management, and network-based authentication flow.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

from app.services import AuthService, SessionService
from app.models import User, Role
from app.database import get_db_session
from app.middleware.auth_middleware import auth_required, optional_auth, network_auth_required

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def get_auth_service() -> AuthService:
    """Get AuthService instance with database session."""
    db_session = getattr(g, 'db', None)
    if not db_session:
        db_session = get_db_session()
    return AuthService(db_session)

def get_session_service() -> SessionService:
    """Get SessionService instance with database session."""
    db_session = getattr(g, 'db', None)
    if not db_session:
        db_session = get_db_session()
    return SessionService(db_session)

def validate_request_data(required_fields: list) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Validate request data and return success status, data, and error message."""
    if not request.is_json:
        return False, None, "Content-Type must be application/json"
    
    try:
        data = request.get_json()
        if not data:
            return False, None, "Request body is required"
    except Exception:
        return False, None, "Request body is required"
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, None, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, data, None

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint with network-based authentication.
    
    Request:
        {
            "username": "string",
            "password": "string",
            "device_id": "string" (optional),
            "ip_address": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "token": "jwt_token",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "roles": ["Admin"],
                "permissions": ["user:create", "user:read", ...]
            },
            "session": {
                "session_id": "uuid",
                "expires_at": "2024-12-19T18:00:00Z"
            }
        }
    """
    try:
        # Validate request data
        success, data, error = validate_request_data(['username', 'password'])
        if not success:
            return jsonify({'error': error}), 400
        
        username = data.get('username')
        password = data.get('password')
        device_id = data.get('device_id')
        ip_address = request.remote_addr or data.get('ip_address')
        
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # Authenticate user
        success, user_data, error = auth_service.authenticate_user(
            username, password, device_id, ip_address
        )
        
        if not success:
            return jsonify({'error': error}), 401
        
        # Create session
        session_success, session_data, session_error = session_service.create_session(
            user_data['id'], device_id, ip_address
        )
        
        if not session_success:
            return jsonify({'error': session_error}), 500
        
        # Return success response
        response_data = {
            'success': True,
            'token': user_data['token'],
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data.get('email'),
                'roles': user_data.get('roles', []),
                'permissions': user_data.get('permissions', [])
            },
            'session': session_data
        }
        
        logger.info(f"User {username} logged in successfully from {ip_address}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    """
    User logout endpoint.
    
    Request:
        {
            "device_id": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    try:
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # User is already authenticated by decorator
        user_data = g.user_data
        
        # Get device_id from request
        data = request.get_json() or {}
        device_id = data.get('device_id')
        
        # Invalidate session
        session_success = session_service.invalidate_session(
            user_data['id'], user_data.get('session_id'), request.remote_addr
        )
        
        if not session_success:
            logger.warning("Session invalidation failed")
        
        # Log logout
        logger.info(f"User {user_data['username']} logged out")
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    First device admin registration endpoint.
    
    Request:
        {
            "username": "string",
            "password": "string",
            "email": "string",
            "full_name": "string",
            "device_id": "string" (optional),
            "ip_address": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "token": "jwt_token",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "roles": ["Admin"]
            },
            "message": "Admin user created successfully"
        }
    """
    try:
        # Validate request data
        success, data, error = validate_request_data(['username', 'password', 'email', 'full_name'])
        if not success:
            return jsonify({'error': error}), 400
        
        # Get device info
        device_id = data.get('device_id')
        ip_address = request.remote_addr or data.get('ip_address')
        
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # Create admin user
        # Split full_name into first_name and last_name
        full_name_parts = data['full_name'].split(' ', 1)
        first_name = full_name_parts[0]
        last_name = full_name_parts[1] if len(full_name_parts) > 1 else ''
        
        admin_data = {
            'username': data['username'],
            'password': data['password'],
            'email': data['email'],
            'first_name': first_name,
            'last_name': last_name
        }
        
        success, user_data, error = auth_service.create_network_admin(admin_data, device_id)
        
        if not success:
            return jsonify({'error': error}), 400
        
        # Create session
        session_success, session_data, session_error = session_service.create_session(
            user_data['id'], device_id, ip_address
        )
        
        if not session_success:
            return jsonify({'error': session_error}), 500
        
        # Return success response
        response_data = {
            'success': True,
            'token': user_data['token'],
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'roles': user_data.get('roles', [])
            },
            'session': session_data,
            'message': 'Admin user created successfully'
        }
        
        logger.info(f"Admin user {data['username']} registered successfully from {ip_address}")
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/check-network', methods=['GET'])
def check_network():
    """
    Check if admin exists on the network.
    
    Response:
        {
            "admin_exists": true/false,
            "requires_registration": true/false
        }
    """
    try:
        # Get services
        auth_service = get_auth_service()
        
        # Check if admin exists
        admin_exists = auth_service.check_network_admin_exists()
        
        return jsonify({
            'admin_exists': admin_exists,
            'requires_registration': not admin_exists
        }), 200
        
    except Exception as e:
        logger.error(f"Network check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@auth_required
def refresh_token():
    """
    Refresh JWT token endpoint.
    
    Request:
        {
            "device_id": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "token": "new_jwt_token",
            "expires_at": "2024-12-19T18:00:00Z"
        }
    """
    try:
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # Verify current token
        success, user_data, error = auth_service.verify_token(token)
        if not success:
            return jsonify({'error': error}), 401
        
        # Get device_id from request
        data = request.get_json() or {}
        device_id = data.get('device_id')
        
        # Refresh session
        session_success, session_data, session_error = session_service.refresh_session(
            user_data['id'], device_id
        )
        
        if not session_success:
            return jsonify({'error': session_error}), 401
        
        # Generate new token
        token_success, new_token, token_error = auth_service.refresh_token_simple(user_data['id'])
        
        if not token_success:
            return jsonify({'error': token_error}), 500
        
        return jsonify({
            'success': True,
            'token': new_token,
            'expires_at': session_data.get('expires_at')
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify', methods=['GET'])
@optional_auth
def verify_token():
    """
    Verify token endpoint.
    
    This endpoint allows clients to verify if their current token is valid.
    It can be called with or without a token.
    
    Response (with valid token):
        {
            "valid": true,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "roles": ["Admin"],
                "permissions": ["user:create", "user:read", ...]
            }
        }
    
    Response (without token or invalid token):
        {
            "valid": false,
            "message": "Token is invalid or missing"
        }
    """
    try:
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({
                'valid': False,
                'message': 'No token provided'
            }), 200
        
        # Get services
        auth_service = get_auth_service()
        
        # Verify token
        success, user_data, error = auth_service.verify_token(token)
        
        if not success:
            return jsonify({
                'valid': False,
                'message': error
            }), 200
        
        return jsonify({
            'valid': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'valid': False,
            'message': 'Internal server error'
        }), 200

@auth_bp.route('/change-password', methods=['POST'])
@auth_required
def change_password():
    """
    Change user password endpoint.
    
    Request:
        {
            "current_password": "string",
            "new_password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "Password changed successfully"
        }
    """
    try:
        # Validate request data
        success, data, error = validate_request_data(['current_password', 'new_password'])
        if not success:
            return jsonify({'error': error}), 400
        
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Get services
        auth_service = get_auth_service()
        
        # Verify token and get user
        success, user_data, error = auth_service.verify_token(token)
        if not success:
            return jsonify({'error': error}), 401
        
        # Change password
        change_success, change_error = auth_service.change_password(
            user_data['id'],
            data['current_password'],
            data['new_password']
        )
        
        if not change_success:
            return jsonify({'error': change_error}), 400
        
        logger.info(f"User {user_data['username']} changed password")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """
    Get current user profile endpoint.
    
    Response:
        {
            "success": true,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "roles": ["Admin"],
                "permissions": ["user:create", "user:read", ...],
                "created_at": "2024-12-19T10:00:00Z",
                "last_login": "2024-12-19T15:30:00Z"
            }
        }
    """
    try:
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Get services
        auth_service = get_auth_service()
        
        # Verify token and get user
        success, user_data, error = auth_service.verify_token(token)
        if not success:
            return jsonify({'error': error}), 401
        
        # Get complete user profile
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        user = db_session.query(User).filter(User.id == user_data['id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Build profile data
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'roles': [role.role.name for role in user.roles if role.role.is_active],
            'permissions': user_data.get('permissions', []),
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'failed_login_attempts': user.failed_login_attempts,
            'account_locked_until': user.locked_until.isoformat() if user.locked_until else None
        }
        
        return jsonify({
            'success': True,
            'user': profile_data
        }), 200
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/sessions', methods=['GET'])
@auth_required
def get_sessions():
    """
    Get user sessions endpoint (Admin only).
    
    Response:
        {
            "success": true,
            "sessions": [
                {
                    "session_id": "uuid",
                    "user_id": 1,
                    "username": "admin",
                    "device_id": "device123",
                    "ip_address": "192.168.1.100",
                    "created_at": "2024-12-19T15:30:00Z",
                    "expires_at": "2024-12-19T18:30:00Z",
                    "is_active": true
                }
            ]
        }
    """
    try:
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # Verify token and check admin role
        success, user_data, error = auth_service.verify_token(token)
        if not success:
            return jsonify({'error': error}), 401
        
        # Check if user is admin
        if 'Admin' not in user_data.get('roles', []):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all active sessions
        sessions = session_service.get_all_active_sessions()
        
        return jsonify({
            'success': True,
            'sessions': sessions
        }), 200
        
    except Exception as e:
        logger.error(f"Session retrieval error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/sessions/<int:user_id>', methods=['DELETE'])
@auth_required
def force_logout_user(user_id):
    """
    Force logout user endpoint (Admin only).
    
    Response:
        {
            "success": true,
            "message": "User logged out successfully"
        }
    """
    try:
        # Get token from request
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        # Get services
        auth_service = get_auth_service()
        session_service = get_session_service()
        
        # Verify token and check admin role
        success, user_data, error = auth_service.verify_token(token)
        if not success:
            return jsonify({'error': error}), 401
        
        # Check if user is admin
        if 'Admin' not in user_data.get('roles', []):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Force logout user
        logout_success = session_service.force_logout_user(user_id)
        
        if not logout_success:
            return jsonify({'error': 'Failed to force logout user'}), 400
        
        logger.info(f"Admin {user_data['username']} forced logout for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'User logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Force logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 