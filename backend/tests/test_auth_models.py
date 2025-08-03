#!/usr/bin/env python3
"""
Test script for authentication models.
This script verifies that all authentication models can be imported and created correctly.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import User, Role, Permission, UserRole, RolePermission, AuditLog
from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import jwt
from datetime import datetime, timedelta


def test_model_imports():
    """Test that all authentication models can be imported."""
    print("✅ Testing model imports...")
    
    try:
        # Test imports
        from app.models import User, Role, Permission, UserRole, RolePermission, AuditLog
        print("✅ All authentication models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing models: {e}")
        return False


def test_user_model():
    """Test User model functionality."""
    print("\n✅ Testing User model...")
    
    try:
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        
        # Test password verification
        assert user.verify_password("SecurePass123!")
        assert not user.verify_password("wrongpassword")
        
        # Test password policy
        is_valid, message = user.check_password_policy("SecurePass123!")
        assert is_valid, f"Password should be valid: {message}"
        
        # Test JWT token generation
        token = user.generate_jwt_token()
        assert token is not None
        
        # Test account lockout
        assert not user.is_account_locked()
        # Set initial failed attempts to 0 to ensure proper testing
        user.failed_login_attempts = 0
        user.increment_failed_login()
        user.increment_failed_login()
        user.increment_failed_login()
        user.increment_failed_login()
        user.increment_failed_login()
        assert user.is_account_locked()
        
        print("✅ User model tests passed")
        return True
    except Exception as e:
        print(f"❌ Error testing User model: {e}")
        return False


def test_role_model():
    """Test Role model functionality."""
    print("\n✅ Testing Role model...")
    
    try:
        # Create a test role
        role = Role(
            name="TestRole",
            description="A test role for testing purposes"
        )
        
        # Test role properties
        assert role.name == "TestRole"
        assert role.description == "A test role for testing purposes"
        assert role.is_active == True
        
        # Test role hierarchy
        hierarchy = role.get_role_hierarchy()
        assert len(hierarchy) == 1
        assert hierarchy[0] == "TestRole"
        
        # Test permission methods
        assert not role.has_permission("nonexistent:permission")
        permissions = role.get_permissions()
        assert permissions == []
        
        # Test role methods
        assert not role.is_admin_role()
        assert not role.can_manage_users()
        assert not role.can_manage_roles()
        assert not role.can_access_system_settings()
        
        print("✅ Role model tests passed")
        return True
    except Exception as e:
        print(f"❌ Error testing Role model: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_permission_model():
    """Test Permission model functionality."""
    print("\n✅ Testing Permission model...")
    
    try:
        # Create a test permission
        permission = Permission(
            name="users:create",
            resource="users",
            action="create",
            category="user_management",
            description="Can create new users"
        )
        
        # Test permission properties
        assert permission.name == "users:create"
        assert permission.resource == "users"
        assert permission.action == "create"
        assert permission.category == "user_management"
        assert permission.get_full_name() == "users:create"
        assert permission.is_crud_permission() == True
        
        print("✅ Permission model tests passed")
        return True
    except Exception as e:
        print(f"❌ Error testing Permission model: {e}")
        return False


def test_audit_log_model():
    """Test AuditLog model functionality."""
    print("\n✅ Testing AuditLog model...")
    
    try:
        # Create a test audit log entry
        audit_log = AuditLog(
            event_type="login",
            event_category="authentication",
            severity="medium",
            description="User logged in successfully",
            is_success="success",
            user_id=1,
            ip_address="192.168.1.1"
        )
        
        # Test audit log properties
        assert audit_log.event_type == "login"
        assert audit_log.event_category == "authentication"
        assert audit_log.severity == "medium"
        assert audit_log.is_success == "success"
        assert audit_log.is_authentication_event() == True
        assert audit_log.is_failed_event() == False
        
        # Test class methods
        auth_event = AuditLog.log_authentication_event(
            user_id=1,
            event_type="login_failed",
            description="Failed login attempt",
            is_success="failure"
        )
        assert auth_event.severity == "high"
        assert auth_event.is_authentication_event() == True
        
        print("✅ AuditLog model tests passed")
        return True
    except Exception as e:
        print(f"❌ Error testing AuditLog model: {e}")
        return False


def test_relationships():
    """Test model relationships."""
    print("\n✅ Testing model relationships...")
    
    try:
        # Create test objects
        user = User(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        
        role = Role(
            name="TestRole",
            description="A test role"
        )
        
        permission = Permission(
            name="users:read",
            resource="users",
            action="read",
            category="user_management"
        )
        
        # Test that relationships can be created
        user_role = UserRole(user_id=user.id, role_id=role.id)
        role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
        
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        
        print("✅ Model relationships tests passed")
        return True
    except Exception as e:
        print(f"❌ Error testing model relationships: {e}")
        return False


def main():
    """Run all authentication model tests."""
    print("🧪 Testing Authentication Models")
    print("=" * 50)
    
    tests = [
        test_model_imports,
        test_user_model,
        test_role_model,
        test_permission_model,
        test_audit_log_model,
        test_relationships
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication model tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 