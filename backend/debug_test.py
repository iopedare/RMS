#!/usr/bin/env python3
"""
Debug script to test authentication and user endpoints.
"""

from app import create_app
from app.models import User, Role, UserRole, Permission, RolePermission
from app.database import get_db_session
from app.extensions import db

def debug_test():
    """Debug authentication and user endpoints."""
    
    # Create app
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Get database session
        session = get_db_session()
        
        try:
            print("=== Setting up database ===")
            
            # Create permissions
            permissions = [
                Permission(name='users:read', resource='users', action='read', category='user_management'),
                Permission(name='users:create', resource='users', action='create', category='user_management'),
                Permission(name='users:update', resource='users', action='update', category='user_management'),
                Permission(name='users:delete', resource='users', action='delete', category='user_management'),
                Permission(name='auth:login', resource='auth', action='login', category='authentication'),
            ]
            
            for permission in permissions:
                session.add(permission)
            session.flush()
            print(f"✅ Created {len(permissions)} permissions")
            
            # Create admin role
            admin_role = Role(
                name='Admin',
                description='System Administrator',
                priority=1,
                created_by=1
            )
            session.add(admin_role)
            session.flush()
            print(f"✅ Created admin role with ID: {admin_role.id}")
            
            # Assign permissions to admin role
            for permission in permissions:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    is_active=True,
                    created_by=1
                )
                session.add(role_permission)
            print("✅ Assigned permissions to admin role")
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='Admin123!',
                first_name='Admin',
                last_name='User',
                is_active=True,
                created_by=1
            )
            session.add(admin_user)
            session.flush()
            print(f"✅ Created admin user with ID: {admin_user.id}")
            
            # Assign admin role to user
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                is_primary=True,
                created_by=1
            )
            session.add(user_role)
            session.commit()
            print("✅ Assigned admin role to user")
            
            print("\n=== Testing Login ===")
            
            # Test login
            client = app.test_client()
            response = client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'Admin123!'
            })
            
            print(f"Login status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                token = data.get('token')
                print(f"✅ Login successful")
                print(f"Token: {token[:50]}...")
                
                # Check user permissions
                user = session.query(User).filter(User.id == admin_user.id).first()
                print(f"User roles: {[ur.role.name for ur in user.roles]}")
                print(f"User session ID: {user.current_session_id}")
                
                print("\n=== Testing User Endpoints ===")
                
                # Test user listing
                headers = {'Authorization': f'Bearer {token}'}
                response = client.get('/api/users', headers=headers)
                print(f"User listing status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"✅ User listing successful, found {len(data.get('users', []))} users")
                else:
                    print(f"❌ User listing failed: {response.get_json()}")
                    
                # Test get specific user
                response = client.get(f'/api/users/{admin_user.id}', headers=headers)
                print(f"Get user status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"✅ Get user successful")
                else:
                    print(f"❌ Get user failed: {response.get_json()}")
                
                print("\n=== Testing User Endpoints ===")
                
                # Test user listing
                headers = {'Authorization': f'Bearer {token}'}
                response = client.get('/api/users', headers=headers)
                print(f"User listing status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"✅ User listing successful, found {len(data.get('users', []))} users")
                else:
                    print(f"❌ User listing failed: {response.get_json()}")
                    
            else:
                print(f"❌ Login failed: {response.get_json()}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    debug_test() 