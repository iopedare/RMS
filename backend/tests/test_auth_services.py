#!/usr/bin/env python3
"""
Test script for authentication services.
This script verifies that all authentication services work correctly.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services import AuthService, AuthorizationService, SessionService
from app.models import User, Role, Permission, UserRole, RolePermission, AuditLog
from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import jwt
from datetime import datetime, timedelta


def test_auth_service():
    """Test AuthService functionality."""
    print("\n✅ Testing AuthService...")
    
    try:
        # Create test database
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create test role
        role = Role(name="TestRole", description="Test role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Assign role to user
        user_role = UserRole(user_id=user.id, role_id=role.id, is_primary=True)
        db_session.add(user_role)
        db_session.commit()
        
        # Test AuthService
        auth_service = AuthService(db_session)
        
        # Test authentication
        success, user_data, error = auth_service.authenticate_user(
            username="testuser",
            password="SecurePass123!",
            device_id="test-device-1"
        )
        
        assert success, f"Authentication should succeed: {error}"
        assert user_data is not None, "User data should be returned"
        assert 'token' in user_data, "Token should be included in response"
        assert 'session_id' in user_data, "Session ID should be included in response"
        
        # Test invalid password
        success, user_data, error = auth_service.authenticate_user(
            username="testuser",
            password="wrongpassword"
        )
        
        assert not success, "Authentication should fail with wrong password"
        assert error is not None, "Error message should be provided"
        
        # Test token verification
        token = user_data['token'] if user_data else None
        if token:
            is_valid, user_data, error = auth_service.verify_token(token)
            assert is_valid, f"Token should be valid: {error}"
        
        # Create Admin role first
        admin_role = Role(name="Admin", description="Admin role")
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Test network admin creation
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'AdminPass123!',
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        success, admin_user_data, error = auth_service.create_network_admin(
            admin_data, device_id="admin-device"
        )
        
        assert success, f"Admin creation should succeed: {error}"
        assert admin_user_data is not None, "Admin user data should be returned"
        
        # Test network admin check
        admin_exists = auth_service.check_network_admin_exists()
        assert admin_exists, "Admin should exist after creation"
        
        # Test that second admin creation fails
        second_admin_data = {
            'username': 'second_admin',
            'email': 'admin2@example.com',
            'password': 'AdminPass123!',
            'first_name': 'Second',
            'last_name': 'Admin'
        }
        
        success, admin_user_data, error = auth_service.create_network_admin(
            second_admin_data, device_id="second-device"
        )
        
        assert not success, "Second admin creation should fail"
        assert "already exists" in error, "Error should mention admin already exists"
        
        print("✅ AuthService tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AuthService: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authorization_service():
    """Test AuthorizationService functionality."""
    print("\n✅ Testing AuthorizationService...")
    
    try:
        # Create test database
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create test roles
        admin_role = Role(name="Admin", description="Admin role")
        manager_role = Role(name="Manager", description="Manager role")
        db_session.add_all([admin_role, manager_role])
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(manager_role)
        
        # Create test permissions
        user_create_perm = Permission(
            name="users:create",
            resource="users",
            action="create",
            category="user_management"
        )
        user_read_perm = Permission(
            name="users:read",
            resource="users",
            action="read",
            category="user_management"
        )
        db_session.add_all([user_create_perm, user_read_perm])
        db_session.commit()
        db_session.refresh(user_create_perm)
        db_session.refresh(user_read_perm)
        
        # Assign permissions to roles
        admin_user_perm = RolePermission(role_id=admin_role.id, permission_id=user_create_perm.id)
        manager_user_perm = RolePermission(role_id=manager_role.id, permission_id=user_read_perm.id)
        db_session.add_all([admin_user_perm, manager_user_perm])
        db_session.commit()
        
        # Assign roles to user
        user_admin_role = UserRole(user_id=user.id, role_id=admin_role.id, is_primary=True)
        user_manager_role = UserRole(user_id=user.id, role_id=manager_role.id, is_primary=False)
        db_session.add_all([user_admin_role, user_manager_role])
        db_session.commit()
        
        # Test AuthorizationService
        auth_service = AuthorizationService(db_session)
        
        # Test permission checking
        has_create_perm = auth_service.check_permission(user.id, "users:create")
        assert has_create_perm, "User should have users:create permission"
        
        has_read_perm = auth_service.check_permission(user.id, "users:read")
        assert has_read_perm, "User should have users:read permission"
        
        has_delete_perm = auth_service.check_permission(user.id, "users:delete")
        assert not has_delete_perm, "User should not have users:delete permission"
        
        # Test role checking
        has_admin_role = auth_service.check_role(user.id, "Admin")
        assert has_admin_role, "User should have Admin role"
        
        has_manager_role = auth_service.check_role(user.id, "Manager")
        assert has_manager_role, "User should have Manager role"
        
        has_sales_role = auth_service.check_role(user.id, "Sales Assistant")
        assert not has_sales_role, "User should not have Sales Assistant role"
        
        # Test admin checking
        is_admin = auth_service.is_admin(user.id)
        assert is_admin, "User should be admin"
        
        # Test user context
        user_context = auth_service.get_user_context(user.id)
        assert user_context is not None, "User context should be returned"
        assert 'user_id' in user_context, "User context should contain user_id"
        assert 'roles' in user_context, "User context should contain roles"
        assert 'permissions' in user_context, "User context should contain permissions"
        
        print("✅ AuthorizationService tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AuthorizationService: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_service():
    """Test SessionService functionality."""
    print("\n✅ Testing SessionService...")
    
    try:
        # Create test database
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test SessionService
        session_service = SessionService(db_session)
        
        # Test session creation
        success, session_id, error = session_service.create_session(
            user_id=user.id,
            device_id="test-device-1"
        )
        
        assert success, f"Session creation should succeed: {error}"
        assert session_id is not None, "Session ID should be returned"
        
        # Test session validation
        is_valid, error = session_service.validate_session(user.id, session_id)
        assert is_valid, f"Session should be valid: {error}"
        
        # Test session info
        session_info = session_service.get_session_info(user.id)
        assert session_info is not None, "Session info should be returned"
        assert session_info['session_id'] == session_id, "Session ID should match"
        assert session_info['is_session_active'], "Session should be active"
        
        # Test session invalidation
        success = session_service.invalidate_session(user.id, session_id)
        assert success, "Session invalidation should succeed"
        
        # Test session validation after invalidation
        is_valid, error = session_service.validate_session(user.id, session_id)
        assert not is_valid, "Session should be invalid after invalidation"
        
        print("✅ SessionService tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing SessionService: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_network_auth_flow():
    """Test network-based authentication flow."""
    print("\n✅ Testing Network Authentication Flow...")
    
    try:
        # Create test database
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create Admin role first
        admin_role = Role(name="Admin", description="Admin role")
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Test AuthService
        auth_service = AuthService(db_session)
        
        # Test initial state - no admin exists
        admin_exists = auth_service.check_network_admin_exists()
        assert not admin_exists, "No admin should exist initially"
        
        # Create first admin for network
        admin_data = {
            'username': 'network_admin',
            'email': 'admin@example.com',
            'password': 'AdminPass123!',
            'first_name': 'Network',
            'last_name': 'Admin'
        }
        
        success, admin_user_data, error = auth_service.create_network_admin(
            admin_data, device_id="first-device"
        )
        
        assert success, f"First admin creation should succeed: {error}"
        assert admin_user_data is not None, "Admin user data should be returned"
        assert 'token' in admin_user_data, "Token should be included for immediate login"
        
        # Test that admin now exists
        admin_exists = auth_service.check_network_admin_exists()
        assert admin_exists, "Admin should exist after creation"
        
        # Test that second admin creation fails
        second_admin_data = {
            'username': 'second_admin',
            'email': 'admin2@example.com',
            'password': 'AdminPass123!',
            'first_name': 'Second',
            'last_name': 'Admin'
        }
        
        success, admin_user_data, error = auth_service.create_network_admin(
            second_admin_data, device_id="second-device"
        )
        
        assert not success, "Second admin creation should fail"
        assert "already exists" in error, "Error should mention admin already exists"
        
        print("✅ Network Authentication Flow tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Network Authentication Flow: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all authentication service tests."""
    print("🧪 Testing Authentication Services")
    print("=" * 50)
    
    tests = [
        test_auth_service,
        test_authorization_service,
        test_session_service,
        test_network_auth_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication service tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 