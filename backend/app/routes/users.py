#!/usr/bin/env python3
"""
User management routes for Retail Management System.

This module provides REST API endpoints for user management,
including CRUD operations, role assignment, and account management.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from typing import Dict, Any, Optional, Tuple, List
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import joinedload

from app.services import AuthService, AuthorizationService, SessionService
from app.models import User, Role, UserRole, AuditLog
from app.database import get_db_session
from app.middleware.auth_middleware import auth_required
from app.services.authorization_service import require_permission

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

def get_auth_service() -> AuthService:
    """Get AuthService instance with database session."""
    db_session = getattr(g, 'db', None)
    if not db_session:
        db_session = get_db_session()
    return AuthService(db_session)

def get_authorization_service() -> AuthorizationService:
    """Get AuthorizationService instance with database session."""
    db_session = getattr(g, 'db', None)
    if not db_session:
        db_session = get_db_session()
    return AuthorizationService(db_session)

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

def log_user_operation(operation: str, user_id: int, target_user_id: Optional[int] = None, 
                      details: Optional[Dict] = None, success: bool = True, error_message: Optional[str] = None):
    """Log user management operations for audit trail."""
    try:
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        audit_log = AuditLog(
            event_type=operation,
            event_category='user_management',
            severity='info' if success else 'warning',
            description=f"User management operation: {operation}",
            user_id=user_id,
            session_id=g.get('session_id'),
            device_id=g.get('device_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            resource_type='user',
            resource_id=target_user_id,
            details=details,
            is_success=success,
            error_message=error_message
        )
        
        db_session.add(audit_log)
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Failed to log user operation: {e}")

@users_bp.route('', methods=['GET'])
@auth_required
@require_permission('users:read')
def list_users():
    """
    List all users with pagination, filtering, and search.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)
        search (str): Search term for username, email, or name
        role (str): Filter by role name
        status (str): Filter by status (active, inactive, locked)
        sort_by (str): Sort field (username, email, created_at, last_login)
        sort_order (str): Sort order (asc, desc)
    
    Response:
        {
            "success": true,
            "users": [
                {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "first_name": "Admin",
                    "last_name": "User",
                    "is_active": true,
                    "is_locked": false,
                    "roles": ["Admin"],
                    "created_at": "2024-12-19T10:00:00Z",
                    "last_login": "2024-12-19T15:30:00Z"
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 50,
                "pages": 3,
                "has_next": true,
                "has_prev": false
            }
        }
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()
        status_filter = request.args.get('status', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort parameters
        valid_sort_fields = ['username', 'email', 'first_name', 'last_name', 'created_at', 'last_login']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        # Build query
        query = db_session.query(User).options(
            joinedload(User.roles).joinedload(UserRole.role)
        )
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        # Apply role filter
        if role_filter:
            query = query.join(UserRole, User.id == UserRole.user_id).join(Role, UserRole.role_id == Role.id).filter(Role.name == role_filter)
        
        # Apply status filter
        if status_filter:
            if status_filter == 'active':
                query = query.filter(User.is_active == True, User.is_locked == False)
            elif status_filter == 'inactive':
                query = query.filter(User.is_active == False)
            elif status_filter == 'locked':
                query = query.filter(User.is_locked == True)
        
        # Apply sorting
        sort_field = getattr(User, sort_by)
        if sort_order == 'desc':
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        users = query.offset(offset).limit(per_page).all()
        
        # Prepare response data
        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_locked': user.is_locked,
                'roles': [user_role.role.name for user_role in user.roles if user_role.is_active],
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            users_data.append(user_data)
        
        # Calculate pagination metadata
        pages = (total + per_page - 1) // per_page
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }
        
        # Log operation
        current_user_id = g.get('user_id')
        log_user_operation('list_users', current_user_id, details={
            'page': page,
            'per_page': per_page,
            'search': search,
            'role_filter': role_filter,
            'status_filter': status_filter,
            'total_results': total
        })
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        
        # Log error
        current_user_id = g.get('user_id')
        log_user_operation('list_users', current_user_id, success=False, error_message=str(e))
        
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve users'
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@auth_required
@require_permission('users:read')
def get_user(user_id: int):
    """
    Get specific user details by ID.
    
    Response:
        {
            "success": true,
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "phone": "+1234567890",
                "is_active": true,
                "is_locked": false,
                "failed_login_attempts": 0,
                "locked_until": null,
                "roles": [
                    {
                        "id": 1,
                        "name": "Admin",
                        "description": "System Administrator",
                        "is_primary": true
                    }
                ],
                "permissions": ["users:create", "users:read", "users:update", "users:delete"],
                "created_at": "2024-12-19T10:00:00Z",
                "updated_at": "2024-12-19T15:30:00Z",
                "last_login": "2024-12-19T15:30:00Z",
                "password_changed_at": "2024-12-19T10:00:00Z"
            }
        }
    """
    try:
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        # Get user with roles and permissions
        user = db_session.query(User).options(
            joinedload(User.roles).joinedload(UserRole.role)
        ).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user permissions
        auth_service = get_auth_service()
        authorization_service = get_authorization_service()
        permissions = authorization_service.get_user_permissions(user.id)
        
        # Prepare response data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_active': user.is_active,
            'is_locked': user.is_locked,
            'failed_login_attempts': user.failed_login_attempts,
            'locked_until': user.locked_until.isoformat() if user.locked_until else None,
            'roles': [
                {
                    'id': user_role.role.id,
                    'name': user_role.role.name,
                    'description': user_role.role.description,
                    'is_primary': user_role.is_primary
                }
                for user_role in user.roles if user_role.is_active
            ],
            'permissions': permissions,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'password_changed_at': user.password_changed_at.isoformat() if user.password_changed_at else None
        }
        
        # Log operation
        current_user_id = g.get('user_id')
        log_user_operation('get_user', current_user_id, user_id)
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        
        # Log error
        current_user_id = g.get('user_id')
        log_user_operation('get_user', current_user_id, user_id, success=False, error_message=str(e))
        
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user'
        }), 500

@users_bp.route('', methods=['POST'])
@auth_required
@require_permission('users:create')
def create_user():
    """
    Create a new user with role assignment.
    
    Request:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "first_name": "string",
            "last_name": "string",
            "phone": "string" (optional),
            "roles": [1, 2] (optional),
            "is_active": true (optional, default: true)
        }
    
    Response:
        {
            "success": true,
            "user": {
                "id": 2,
                "username": "manager",
                "email": "manager@example.com",
                "first_name": "Store",
                "last_name": "Manager",
                "is_active": true,
                "roles": ["Manager"],
                "created_at": "2024-12-19T16:00:00Z"
            }
        }
    """
    try:
        # Validate request data
        success, data, error = validate_request_data(['username', 'email', 'password', 'first_name', 'last_name'])
        if not success:
            return jsonify({'error': error}), 400
        
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        # Check if username or email already exists
        existing_user = db_session.query(User).filter(
            or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 409
        
        # Create new user
        auth_service = get_auth_service()
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            is_active=data.get('is_active', True),
            created_by=g.get('user_id')
        )
        
        # Validate password requirements
        is_valid, error_message = user.check_password_policy(data['password'])
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        # Password is already hashed in User.__init__
        
        # Add to database
        db_session.add(user)
        db_session.flush()  # Get the user ID
        
        # Assign roles if provided
        if 'roles' in data and data['roles']:
            role_ids = data['roles']
            roles = db_session.query(Role).filter(Role.id.in_(role_ids)).all()
            
            for role in roles:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    is_primary=len(user.roles) == 0,  # First role is primary
                    created_by=g.get('user_id')
                )
                db_session.add(user_role)
        
        db_session.commit()
        
        # Prepare response data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'roles': [user_role.role.name for user_role in user.roles if user_role.is_active],
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        
        # Log operation
        current_user_id = g.get('user_id')
        log_user_operation('create_user', current_user_id, user.id, {
            'username': user.username,
            'email': user.email,
            'roles': data.get('roles', [])
        })
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        
        # Log error
        current_user_id = g.get('user_id')
        log_user_operation('create_user', current_user_id, success=False, error_message=str(e))
        
        return jsonify({
            'success': False,
            'error': 'Failed to create user'
        }), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@auth_required
@require_permission('users:update')
def update_user(user_id: int):
    """
    Update user information.
    
    Request:
        {
            "email": "string" (optional),
            "first_name": "string" (optional),
            "last_name": "string" (optional),
            "phone": "string" (optional),
            "is_active": true (optional)
        }
    
    Response:
        {
            "success": true,
            "user": {
                "id": 2,
                "username": "manager",
                "email": "manager@example.com",
                "first_name": "Store",
                "last_name": "Manager",
                "is_active": true,
                "updated_at": "2024-12-19T16:30:00Z"
            }
        }
    """
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        # Get user
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Update fields
        updated_fields = []
        if 'email' in data and data['email'] != user.email:
            # Check if email is already taken
            existing_user = db_session.query(User).filter(
                and_(User.email == data['email'], User.id != user_id)
            ).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 409
            user.email = data['email']
            updated_fields.append('email')
        
        if 'first_name' in data:
            user.first_name = data['first_name']
            updated_fields.append('first_name')
        
        if 'last_name' in data:
            user.last_name = data['last_name']
            updated_fields.append('last_name')
        
        if 'phone' in data:
            user.phone = data['phone']
            updated_fields.append('phone')
        
        if 'is_active' in data:
            user.is_active = data['is_active']
            updated_fields.append('is_active')
        
        # Update audit fields
        user.updated_at = datetime.utcnow()
        user.updated_by = g.get('user_id')
        
        db_session.commit()
        
        # Prepare response data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_active': user.is_active,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
        
        # Log operation
        current_user_id = g.get('user_id')
        log_user_operation('update_user', current_user_id, user_id, {
            'updated_fields': updated_fields
        })
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        
        # Log error
        current_user_id = g.get('user_id')
        log_user_operation('update_user', current_user_id, user_id, success=False, error_message=str(e))
        
        return jsonify({
            'success': False,
            'error': 'Failed to update user'
        }), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@auth_required
@require_permission('users:delete')
def delete_user(user_id: int):
    """
    Soft delete user account.
    
    Response:
        {
            "success": true,
            "message": "User deleted successfully"
        }
    """
    try:
        # Get database session
        db_session = getattr(g, 'db', None)
        if not db_session:
            db_session = get_db_session()
        
        # Get user
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Prevent self-deletion
        current_user_id = g.get('user_id')
        if user_id == current_user_id:
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own account'
            }), 400
        
        # Soft delete user
        user.is_active = False
        user.updated_at = datetime.utcnow()
        user.updated_by = current_user_id
        
        # Invalidate user sessions
        session_service = get_session_service()
        session_service.force_logout_user(user_id, "User account deleted")
        
        db_session.commit()
        
        # Log operation
        log_user_operation('delete_user', current_user_id, user_id, {
            'username': user.username,
            'email': user.email
        })
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        
        # Log error
        current_user_id = g.get('user_id')
        log_user_operation('delete_user', current_user_id, user_id, success=False, error_message=str(e))
        
        return jsonify({
            'success': False,
            'error': 'Failed to delete user'
        }), 500 