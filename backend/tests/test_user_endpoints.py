#!/usr/bin/env python3
"""
Test suite for user management endpoints.

This module tests all user management REST endpoints including
CRUD operations, role assignment, and account management.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app
from app.models import User, Role, UserRole, AuditLog, Permission, RolePermission
from app.database import get_db_session
from app.services import AuthService


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session."""
    with app.app_context():
        from app.extensions import db
        db.create_all()
        session = get_db_session()
        yield session
        session.close()


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""
    # Create permissions
    permissions = [
        Permission(name='users:read', resource='users', action='read', category='user_management', description='Read user information'),
        Permission(name='users:create', resource='users', action='create', category='user_management', description='Create new users'),
        Permission(name='users:update', resource='users', action='update', category='user_management', description='Update user information'),
        Permission(name='users:delete', resource='users', action='delete', category='user_management', description='Delete users'),
        Permission(name='auth:login', resource='auth', action='login', category='authentication', description='User login'),
        Permission(name='auth:logout', resource='auth', action='logout', category='authentication', description='User logout'),
    ]
    
    for permission in permissions:
        db_session.add(permission)
    db_session.flush()
    
    # Create admin role
    admin_role = Role(
        name='Admin',
        description='System Administrator',
        priority=1,
        created_by=1
    )
    db_session.add(admin_role)
    db_session.flush()
    
    # Assign all permissions to admin role
    for permission in permissions:
        role_permission = RolePermission(
            role_id=admin_role.id,
            permission_id=permission.id,
            is_active=True,
            created_by=1
        )
        db_session.add(role_permission)
    
    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password='Admin123!',  # Strong password with uppercase, lowercase, number, and special character
        first_name='Admin',
        last_name='User',
        is_active=True,
        created_by=1
    )
    db_session.add(admin_user)
    db_session.flush()
    
    # Assign admin role
    user_role = UserRole(
        user_id=admin_user.id,
        role_id=admin_role.id,
        is_primary=True,
        created_by=1
    )
    db_session.add(user_role)
    db_session.commit()
    
    return admin_user


@pytest.fixture
def manager_user(db_session):
    """Create manager user for testing."""
    # Create manager role
    manager_role = Role(
        name='Manager',
        description='Store Manager',
        priority=2,
        created_by=1
    )
    db_session.add(manager_role)
    db_session.flush()
    
    # Create manager user
    manager_user = User(
        username='manager',
        email='manager@example.com',
        password='Manager123!',  # Strong password with uppercase, lowercase, number, and special character
        first_name='Store',
        last_name='Manager',
        is_active=True,
        created_by=1
    )
    db_session.add(manager_user)
    db_session.flush()
    
    # Assign manager role
    user_role = UserRole(
        user_id=manager_user.id,
        role_id=manager_role.id,
        is_primary=True,
        created_by=1
    )
    db_session.add(user_role)
    db_session.commit()
    
    return manager_user


@pytest.fixture
def auth_token(admin_user, client):
    """Get authentication token for admin user."""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin123!'
    })
    data = response.get_json()
    return data['token']


class TestUserEndpoints:
    """Test user management endpoints."""
    
    def test_list_users_success(self, client, auth_token, db_session):
        """Test successful user listing."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/users', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
        assert 'pagination' in data
        assert len(data['users']) > 0
    
    def test_list_users_with_pagination(self, client, auth_token, db_session):
        """Test user listing with pagination."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/users?page=1&per_page=5', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['users']) <= 5
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 5
    
    def test_list_users_with_search(self, client, auth_token, db_session):
        """Test user listing with search filter."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/users?search=admin', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['users']) > 0
        # Check that all returned users contain 'admin' in their data
        for user in data['users']:
            assert 'admin' in user['username'].lower() or 'admin' in user['email'].lower()
    
    def test_list_users_with_role_filter(self, client, auth_token, db_session):
        """Test user listing with role filter."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/users?role=Admin', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['users']) > 0
        # Check that all returned users have Admin role
        for user in data['users']:
            assert 'Admin' in user['roles']
    
    def test_list_users_with_status_filter(self, client, auth_token, db_session):
        """Test user listing with status filter."""
        # Ensure we have active users in the database
        from app.models import User, Role, UserRole
        
        # Create a test user if not exists
        existing_user = db_session.query(User).filter(User.username == 'manager').first()
        if not existing_user:
            # Create manager role if not exists
            manager_role = db_session.query(Role).filter(Role.name == 'Manager').first()
            if not manager_role:
                manager_role = Role(
                    name='Manager',
                    description='Store Manager',
                    priority=2,
                    created_by=1
                )
                db_session.add(manager_role)
                db_session.flush()
            
            # Create manager user
            manager_user = User(
                username='manager',
                email='manager@example.com',
                password='Manager123!',
                first_name='Store',
                last_name='Manager',
                is_active=True,
                created_by=1
            )
            db_session.add(manager_user)
            db_session.flush()
            
            # Assign manager role
            user_role = UserRole(
                user_id=manager_user.id,
                role_id=manager_role.id,
                is_primary=True,
                created_by=1
            )
            db_session.add(user_role)
            db_session.commit()
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = client.get('/api/users?status=active', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['users']) > 0
        # Check that all returned users are active
        for user in data['users']:
            assert user['is_active'] is True
            assert user['is_locked'] is False
    
    def test_list_users_unauthorized(self, client, db_session):
        """Test user listing without authentication."""
        response = client.get('/api/users')
        
        assert response.status_code == 401
    
    def test_get_user_success(self, client, auth_token, admin_user, db_session):
        """Test successful user retrieval."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # Get user ID from database to avoid detached instance issues
        user = db_session.query(User).filter(User.username == 'admin').first()
        user_id = user.id
        response = client.get(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['id'] == user_id
        assert data['user']['username'] == 'admin'
        assert 'roles' in data['user']
        assert 'permissions' in data['user']
    
    def test_get_user_not_found(self, client, auth_token, db_session):
        """Test user retrieval for non-existent user."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/users/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'User not found' in data['error']
    
    def test_get_user_unauthorized(self, client, admin_user, db_session):
        """Test user retrieval without authentication."""
        response = client.get(f'/api/users/{admin_user.id}')
        
        assert response.status_code == 401
    
    def test_create_user_success(self, client, auth_token, db_session):
        """Test successful user creation."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+1234567890',
            'is_active': True
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'
        assert data['user']['is_active'] is True
    
    def test_create_user_with_roles(self, client, auth_token, db_session):
        """Test user creation with role assignment."""
        # Create a role first
        role = Role(name='Assistant', description='Assistant Role', created_by=1)
        db_session.add(role)
        db_session.commit()
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'assistant',
            'email': 'assistant@example.com',
            'password': 'Password123!',
            'first_name': 'Assistant',
            'last_name': 'User',
            'roles': [role.id]
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'Assistant' in data['user']['roles']
    
    def test_create_user_duplicate_username(self, client, auth_token, admin_user, db_session):
        """Test user creation with duplicate username."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'admin',  # Already exists
            'email': 'newadmin@example.com',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'Admin'
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'Username or email already exists' in data['error']
    
    def test_create_user_duplicate_email(self, client, auth_token, admin_user, db_session):
        """Test user creation with duplicate email."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newadmin',
            'email': 'admin@example.com',  # Already exists
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'Admin'
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'Username or email already exists' in data['error']
    
    def test_create_user_missing_fields(self, client, auth_token, db_session):
        """Test user creation with missing required fields."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
            # Missing password, first_name, last_name
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required fields' in data['error']
    
    def test_create_user_weak_password(self, client, auth_token, db_session):
        """Test user creation with weak password."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'weak',  # Weak password
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must be at least 8 characters long' in data['error']
    
    def test_create_user_password_missing_uppercase(self, client, auth_token, db_session):
        """Test user creation with password missing uppercase."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123!',  # Missing uppercase
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must contain at least one uppercase letter' in data['error']
    
    def test_create_user_password_missing_special_char(self, client, auth_token, db_session):
        """Test user creation with password missing special character."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',  # Missing special character
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users', json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must contain at least one special character' in data['error']
    
    def test_create_user_unauthorized(self, client, db_session):
        """Test user creation without authentication."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users', json=user_data)
        
        assert response.status_code == 401
    
    def test_update_user_success(self, client, auth_token, manager_user, db_session):
        """Test successful user update."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Manager',
            'phone': '+9876543210'
        }
        
        response = client.put(f'/api/users/{manager_user.id}', json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['last_name'] == 'Manager'
        assert data['user']['phone'] == '+9876543210'
    
    def test_update_user_email(self, client, auth_token, manager_user, db_session):
        """Test user update with email change."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        update_data = {
            'email': 'updated@example.com'
        }
        
        response = client.put(f'/api/users/{manager_user.id}', json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['email'] == 'updated@example.com'
    
    def test_update_user_email_conflict(self, client, auth_token, admin_user, manager_user, db_session):
        """Test user update with conflicting email."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        update_data = {
            'email': 'admin@example.com'  # Already used by admin_user
        }
        
        response = client.put(f'/api/users/{manager_user.id}', json=update_data, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'Email already exists' in data['error']
    
    def test_update_user_not_found(self, client, auth_token, db_session):
        """Test user update for non-existent user."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        update_data = {
            'first_name': 'Updated'
        }
        
        response = client.put('/api/users/999', json=update_data, headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'User not found' in data['error']
    
    def test_update_user_unauthorized(self, client, manager_user, db_session):
        """Test user update without authentication."""
        update_data = {
            'first_name': 'Updated'
        }
        
        response = client.put(f'/api/users/{manager_user.id}', json=update_data)
        
        assert response.status_code == 401
    
    def test_delete_user_success(self, client, auth_token, manager_user, db_session):
        """Test successful user deletion."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        user_id = manager_user.id  # Get ID before user becomes detached
        response = client.delete(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'User deleted successfully' in data['message']
        
        # Verify user is soft deleted
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user.is_active is False
    
    def test_delete_user_not_found(self, client, auth_token, db_session):
        """Test user deletion for non-existent user."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.delete('/api/users/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'User not found' in data['error']
    
    def test_delete_user_self(self, client, auth_token, admin_user, db_session):
        """Test user deletion of own account."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # Get user ID from database to avoid detached instance issues
        user = db_session.query(User).filter(User.username == 'admin').first()
        user_id = user.id
        response = client.delete(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Cannot delete your own account' in data['error']
    
    def test_delete_user_unauthorized(self, client, manager_user, db_session):
        """Test user deletion without authentication."""
        response = client.delete(f'/api/users/{manager_user.id}')
        
        assert response.status_code == 401
    
    def test_audit_logging(self, client, auth_token, manager_user, admin_user, db_session):
        """Test that user operations are properly logged."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Get user IDs from database to avoid detached instance issues
        admin_user_db = db_session.query(User).filter(User.username == 'admin').first()
        manager_user_db = db_session.query(User).filter(User.username == 'manager').first()
        admin_id = admin_user_db.id
        manager_id = manager_user_db.id
        
        # Perform a user operation
        response = client.get(f'/api/users/{manager_id}', headers=headers)
        assert response.status_code == 200
        
        # Check that audit log was created
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.event_type == 'get_user'
        ).all()
        
        assert len(audit_logs) > 0
        latest_log = audit_logs[-1]
        assert latest_log.user_id == admin_id
        assert latest_log.resource_id == str(manager_id)  # Convert to string for comparison
        assert latest_log.is_success == '1'  # Stored as string in database
    
    def test_invalid_json_request(self, client, auth_token, db_session):
        """Test handling of invalid JSON requests."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/users', data='invalid json', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Content-Type must be application/json' in data['error']
    
    def test_wrong_content_type(self, client, auth_token, db_session):
        """Test handling of wrong content type."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.put('/api/users/1', data='some data', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Content-Type must be application/json' in data['error'] 