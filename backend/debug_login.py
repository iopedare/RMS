#!/usr/bin/env python3
"""
Debug script to test login functionality.
"""

from app import create_app
from app.extensions import db
from app.models import User, Role, UserRole, Permission, RolePermission

def debug_login():
    """Debug the login process."""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create permissions (only if they don't exist)
        permission_names = [
            'users:read', 'users:create', 'users:update', 'users:delete', 'auth:login', 'auth:logout'
        ]
        permissions = []
        
        for name in permission_names:
            existing = db.session.query(Permission).filter(Permission.name == name).first()
            if not existing:
                permission = Permission(
                    name=name,
                    resource=name.split(':')[0],
                    action=name.split(':')[1],
                    category='user_management' if 'users:' in name else 'authentication',
                    description=f'{name.replace(":", " ").title()} permission'
                )
                db.session.add(permission)
                permissions.append(permission)
            else:
                permissions.append(existing)
        
        db.session.flush()

        # Create admin role (only if it doesn't exist)
        admin_role = db.session.query(Role).filter(Role.name == 'Admin').first()
        if not admin_role:
            admin_role = Role(
                name='Admin',
                description='System Administrator',
                priority=1,
                created_by=1
            )
            db.session.add(admin_role)
            db.session.flush()

            # Assign all permissions to admin role
            for permission in permissions:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    is_active=True,
                    created_by=1
                )
                db.session.add(role_permission)

        # Create admin user (only if it doesn't exist)
        admin_user = db.session.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='Admin123!',
                first_name='Admin',
                last_name='User',
                is_active=True,
                created_by=1
            )
            db.session.add(admin_user)
            db.session.flush()
            
            # Assign admin role
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                is_primary=True,
                created_by=1
            )
            db.session.add(user_role)
            db.session.commit()
        
        print(f"Created user: {admin_user.username}")
        print(f"User ID: {admin_user.id}")
        print(f"Password hash: {admin_user.password_hash}")
        print(f"Role ID: {admin_user.role_id}")
        print(f"User roles: {[ur.role.name for ur in admin_user.roles]}")
        
        # Test password check
        print(f"Password check result: {admin_user.check_password('Admin123!')}")
        
        # Test login with Flask test client
        with app.test_client() as client:
            response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'Admin123!'
            })
            
            print(f"Login response status: {response.status_code}")
            print(f"Login response data: {response.get_json()}")
            
            # Test direct authentication
            from app.services import AuthService
            auth_service = AuthService(db.session)
            success, user_data, error = auth_service.authenticate_user('admin', 'Admin123!')
            print(f"Direct auth success: {success}")
            print(f"Direct auth user_data: {user_data}")
            print(f"Direct auth error: {error}")

if __name__ == '__main__':
    debug_login() 