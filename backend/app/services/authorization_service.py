#!/usr/bin/env python3
"""
Authorization Service for Retail Management System.

This service handles permission checking, role-based access control (RBAC),
and authorization middleware for protecting API endpoints.
"""

from typing import Optional, List, Dict, Any, Callable
from sqlalchemy.orm import Session
from app.models import User, Role, Permission, UserRole, RolePermission
from functools import wraps
from flask import request, jsonify, g


class AuthorizationService:
    """
    Authorization service for handling permission checking and role-based access control.
    
    Provides methods to check user permissions, validate role assignments,
    and enforce authorization rules throughout the application.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def check_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User ID to check
            permission_name: Permission name to check (e.g., 'users:create')
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False
            
            # Check if user has the permission through their roles
            return user.has_permission(permission_name)
            
        except Exception:
            return False
    
    def check_role(self, user_id: int, role_name: str) -> bool:
        """
        Check if a user has a specific role.
        
        Args:
            user_id: User ID to check
            role_name: Role name to check
            
        Returns:
            True if user has role, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False
            
            return user.has_role(role_name)
            
        except Exception:
            return False
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission names
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return []
            
            permissions = set()
            for user_role in user.roles:
                if user_role.is_active and user_role.role.is_active:
                    permissions.update(user_role.role.get_permissions())
            
            return list(permissions)
            
        except Exception:
            return []
    
    def get_user_roles(self, user_id: int) -> List[str]:
        """
        Get all roles for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of role names
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return []
            
            return user.get_roles()
            
        except Exception:
            return []
    
    def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user is admin, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False
            
            return user.is_admin()
            
        except Exception:
            return False
    
    def can_manage_users(self, user_id: int) -> bool:
        """
        Check if a user can manage other users.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user can manage users, False otherwise
        """
        return self.check_permission(user_id, 'users:create') or \
               self.check_permission(user_id, 'users:update') or \
               self.check_permission(user_id, 'users:delete')
    
    def can_manage_roles(self, user_id: int) -> bool:
        """
        Check if a user can manage roles.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user can manage roles, False otherwise
        """
        return self.check_permission(user_id, 'roles:create') or \
               self.check_permission(user_id, 'roles:update') or \
               self.check_permission(user_id, 'roles:delete')
    
    def can_access_system_settings(self, user_id: int) -> bool:
        """
        Check if a user can access system settings.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user can access system settings, False otherwise
        """
        return self.check_permission(user_id, 'system:*') or \
               self.check_permission(user_id, 'system:configure_sync')
    
    def can_override_single_device(self, user_id: int) -> bool:
        """
        Check if a user can override single device login restriction.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user can override, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False
            
            return user.can_override_single_device()
            
        except Exception:
            return False
    
    def validate_resource_access(self, user_id: int, resource: str, action: str) -> bool:
        """
        Validate if a user can perform an action on a resource.
        
        Args:
            user_id: User ID
            resource: Resource name (e.g., 'users', 'inventory')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')
            
        Returns:
            True if user can perform action on resource, False otherwise
        """
        permission_name = f"{resource}:{action}"
        return self.check_permission(user_id, permission_name)
    
    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user context including roles and permissions.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user context information
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return {}
            
            return {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'is_admin': user.is_admin(),
                'roles': user.get_roles(),
                'permissions': self.get_user_permissions(user_id),
                'can_manage_users': self.can_manage_users(user_id),
                'can_manage_roles': self.can_manage_roles(user_id),
                'can_access_system_settings': self.can_access_system_settings(user_id),
                'can_override_single_device': user.can_override_single_device()
            }
            
        except Exception:
            return {}


def require_permission(permission_name: str):
    """
    Decorator to require a specific permission for an endpoint.
    
    Args:
        permission_name: Permission name required
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from request context (set by auth middleware)
            user_id = getattr(g, 'user_id', None)
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check permission
            auth_service = AuthorizationService(g.db)
            if not auth_service.check_permission(user_id, permission_name):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role_name: str):
    """
    Decorator to require a specific role for an endpoint.
    
    Args:
        role_name: Role name required
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from request context (set by auth middleware)
            user_id = getattr(g, 'user_id', None)
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check role
            auth_service = AuthorizationService(g.db)
            if not auth_service.check_role(user_id, role_name):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin():
    """
    Decorator to require admin role for an endpoint.
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from request context (set by auth middleware)
            user_id = getattr(g, 'user_id', None)
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user is admin
            auth_service = AuthorizationService(g.db)
            if not auth_service.is_admin(user_id):
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_resource_access(resource: str, action: str):
    """
    Decorator to require access to a specific resource and action.
    
    Args:
        resource: Resource name (e.g., 'users', 'inventory')
        action: Action name (e.g., 'create', 'read', 'update', 'delete')
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from request context (set by auth middleware)
            user_id = getattr(g, 'user_id', None)
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check resource access
            auth_service = AuthorizationService(g.db)
            if not auth_service.validate_resource_access(user_id, resource, action):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class AuthorizationMiddleware:
    """
    Authorization middleware for Flask applications.
    
    Provides middleware functions to check permissions and roles
    for incoming requests.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.auth_service = AuthorizationService(db_session)
    
    def check_request_permission(self, permission_name: str) -> bool:
        """
        Check if the current request has the required permission.
        
        Args:
            permission_name: Permission name to check
            
        Returns:
            True if permission granted, False otherwise
        """
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            return False
        
        return self.auth_service.check_permission(user_id, permission_name)
    
    def check_request_role(self, role_name: str) -> bool:
        """
        Check if the current request has the required role.
        
        Args:
            role_name: Role name to check
            
        Returns:
            True if role granted, False otherwise
        """
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            return False
        
        return self.auth_service.check_role(user_id, role_name)
    
    def get_request_user_context(self) -> Dict[str, Any]:
        """
        Get user context for the current request.
        
        Returns:
            Dictionary with user context information
        """
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            return {}
        
        return self.auth_service.get_user_context(user_id) 