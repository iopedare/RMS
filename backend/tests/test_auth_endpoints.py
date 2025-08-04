#!/usr/bin/env python3
"""
Test authentication REST endpoints.

This module tests all authentication endpoints including login, logout,
registration, token refresh, and session management.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app
from app.models import User, Role, UserRole
from app.services import AuthService, SessionService

class TestAuthEndpoints:
    """Test authentication REST endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }
        app = create_app(config)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        with app.test_client() as client:
            with app.app_context():
                # Set up database
                from app.extensions import db
                db.create_all()
                
                # Create test data
                self._create_test_data()
                
                yield client
    
    def _create_test_data(self):
        """Create test data for authentication tests."""
        from app.extensions import db
        
        # Check if Admin role exists, create if not
        admin_role = db.session.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Admin role")
            db.session.add(admin_role)
            db.session.commit()
            db.session.refresh(admin_role)
        
        # Check if Manager role exists, create if not
        manager_role = db.session.query(Role).filter(Role.name == "Manager").first()
        if not manager_role:
            manager_role = Role(name="Manager", description="Manager role")
            db.session.add(manager_role)
            db.session.commit()
            db.session.refresh(manager_role)
        
        # Note: We don't create admin users by default to allow registration tests
        # Admin users will be created by individual tests as needed
    
    def test_check_network_no_admin(self, client):
        """Test network check when no admin exists."""
        response = client.get('/api/auth/check-network')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['admin_exists'] == False
        assert data['requires_registration'] == True
    
    def test_register_first_admin(self, client):
        """Test first admin registration."""
        admin_data = {
            'username': 'newadmin',
            'password': 'NewAdmin123!',
            'email': 'newadmin@test.com',
            'full_name': 'New Admin User',
            'device_id': 'test-device-1'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(admin_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] == True
        assert 'token' in data
        assert data['user']['username'] == 'newadmin'
        assert 'Admin' in data['user']['roles']
        assert data['message'] == 'Admin user created successfully'
    
    def test_register_second_admin_fails(self, client):
        """Test that second admin registration fails."""
        # First admin registration
        admin_data1 = {
            'username': 'admin1',
            'password': 'Admin123!',
            'email': 'admin1@test.com',
            'full_name': 'Admin 1',
            'device_id': 'device-1'
        }
        
        response1 = client.post('/api/auth/register',
                               data=json.dumps(admin_data1),
                               content_type='application/json')
        
        assert response1.status_code == 201
        
        # Second admin registration should fail
        admin_data2 = {
            'username': 'admin2',
            'password': 'Admin123!',
            'email': 'admin2@test.com',
            'full_name': 'Admin 2',
            'device_id': 'device-2'
        }
        
        response2 = client.post('/api/auth/register',
                               data=json.dumps(admin_data2),
                               content_type='application/json')
        data2 = json.loads(response2.data)
        
        assert response2.status_code == 400
        assert 'already exists' in data2['error']
    
    def test_login_success(self, client):
        """Test successful user login."""
        # First register an admin
        admin_data = {
            'username': 'testadmin',
            'password': 'TestAdmin123!',
            'email': 'testadmin@test.com',
            'full_name': 'Test Admin',
            'device_id': 'test-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        
        # Now login
        login_data = {
            'username': 'testadmin',
            'password': 'TestAdmin123!',
            'device_id': 'test-device'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'token' in data
        assert data['user']['username'] == 'testadmin'
        assert 'Admin' in data['user']['roles']
        assert 'session' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'error' in data
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        login_data = {
            'username': 'testuser'
            # Missing password
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'Missing required fields' in data['error']
    
    def test_logout_success(self, client):
        """Test successful logout."""
        # First register and login
        admin_data = {
            'username': 'logoutadmin',
            'password': 'Logout123!',
            'email': 'logout@test.com',
            'full_name': 'Logout Admin',
            'device_id': 'logout-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Logout
        logout_data = {
            'device_id': 'logout-device'
        }
        
        response = client.post('/api/auth/logout',
                             data=json.dumps(logout_data),
                             content_type='application/json',
                             headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['message'] == 'Logged out successfully'
    
    def test_logout_no_token(self, client):
        """Test logout without authorization token."""
        response = client.post('/api/auth/logout',
                             data=json.dumps({}),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'Authorization token required' in data['error']
    
    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # First register and login
        admin_data = {
            'username': 'refreshadmin',
            'password': 'Refresh123!',
            'email': 'refresh@test.com',
            'full_name': 'Refresh Admin',
            'device_id': 'refresh-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Refresh token
        refresh_data = {
            'device_id': 'refresh-device'
        }
        
        response = client.post('/api/auth/refresh',
                             data=json.dumps(refresh_data),
                             content_type='application/json',
                             headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'token' in data
        assert 'expires_at' in data
    
    def test_change_password_success(self, client):
        """Test successful password change."""
        # First register and login
        admin_data = {
            'username': 'passadmin',
            'password': 'OldPass123!',
            'email': 'pass@test.com',
            'full_name': 'Password Admin',
            'device_id': 'pass-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Change password
        password_data = {
            'current_password': 'OldPass123!',
            'new_password': 'NewPass123!'
        }
        
        response = client.post('/api/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['message'] == 'Password changed successfully'
    
    def test_change_password_wrong_current(self, client):
        """Test password change with wrong current password."""
        # First register and login
        admin_data = {
            'username': 'wrongpassadmin',
            'password': 'Correct123!',
            'email': 'wrongpass@test.com',
            'full_name': 'Wrong Pass Admin',
            'device_id': 'wrongpass-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Change password with wrong current password
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'NewPass123!'
        }
        
        response = client.post('/api/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'Current password is incorrect' in data['error']
    
    def test_get_profile_success(self, client):
        """Test successful profile retrieval."""
        # First register and login
        admin_data = {
            'username': 'profileadmin',
            'password': 'Profile123!',
            'email': 'profile@test.com',
            'full_name': 'Profile Admin',
            'device_id': 'profile-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Get profile
        response = client.get('/api/auth/profile',
                            headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['user']['username'] == 'profileadmin'
        assert data['user']['email'] == 'profile@test.com'
        assert 'Admin' in data['user']['roles']
    
    def test_get_profile_no_token(self, client):
        """Test profile retrieval without token."""
        response = client.get('/api/auth/profile')
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'Authorization token required' in data['error']
    
    def test_get_sessions_admin_only(self, client):
        """Test that sessions endpoint requires admin access."""
        # First register and login
        admin_data = {
            'username': 'sessionsadmin',
            'password': 'Sessions123!',
            'email': 'sessions@test.com',
            'full_name': 'Sessions Admin',
            'device_id': 'sessions-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Get sessions (should work for admin)
        response = client.get('/api/auth/sessions',
                            headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'sessions' in data
    
    def test_force_logout_user_admin_only(self, client):
        """Test force logout endpoint requires admin access."""
        # First register and login
        admin_data = {
            'username': 'forcelogoutadmin',
            'password': 'ForceLogout123!',
            'email': 'forcelogout@test.com',
            'full_name': 'Force Logout Admin',
            'device_id': 'forcelogout-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Force logout user (should work for admin)
        response = client.delete('/api/auth/sessions/1',
                               headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['message'] == 'User logged out successfully'
    
    def test_verify_token_valid(self, client):
        """Test token verification with valid token."""
        # First register and login
        admin_data = {
            'username': 'verifyadmin',
            'password': 'Verify123!',
            'email': 'verify@test.com',
            'full_name': 'Verify Admin',
            'device_id': 'verify-device'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(admin_data),
                                      content_type='application/json')
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Verify token
        response = client.get('/api/auth/verify',
                            headers={'Authorization': f'Bearer {token}'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['valid'] == True
        assert data['user']['username'] == 'verifyadmin'
        assert data['user']['email'] == 'verify@test.com'
        assert 'Admin' in data['user']['roles']
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token."""
        response = client.get('/api/auth/verify',
                            headers={'Authorization': 'Bearer invalid_token'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['valid'] == False
        assert 'message' in data
    
    def test_verify_token_no_token(self, client):
        """Test token verification without token."""
        response = client.get('/api/auth/verify')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['valid'] == False
        assert data['message'] == 'No token provided'
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON requests."""
        response = client.post('/api/auth/login',
                             data='invalid json',
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'Request body is required' in data['error']
    
    def test_wrong_content_type(self, client):
        """Test handling of wrong content type."""
        response = client.post('/api/auth/login',
                             data='{"username": "test", "password": "test"}',
                             content_type='text/plain')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'Content-Type must be application/json' in data['error']

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v']) 