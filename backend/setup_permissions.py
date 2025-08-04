#!/usr/bin/env python3
"""
Setup script to initialize permissions and assign them to roles.
This script should be run after the database is created to set up the basic permission structure.
"""

from app import create_app
from app.extensions import db
from app.models import User, Role, Permission, RolePermission
from app.services.auth_service import AuthService
from app.services.authorization_service import AuthorizationService

def setup_permissions():
    """Set up basic permissions and assign them to roles."""
    app = create_app()
    
    with app.app_context():
        # Create permissions
        permissions = [
            # User management permissions
            Permission(name='users:read', resource='users', action='read', category='authentication', description='View user list and details'),
            Permission(name='users:create', resource='users', action='create', category='authentication', description='Create new users'),
            Permission(name='users:update', resource='users', action='update', category='authentication', description='Update user information'),
            Permission(name='users:delete', resource='users', action='delete', category='authentication', description='Delete users'),
            
            # Role management permissions
            Permission(name='roles:read', resource='roles', action='read', category='authentication', description='View roles and permissions'),
            Permission(name='roles:create', resource='roles', action='create', category='authentication', description='Create new roles'),
            Permission(name='roles:update', resource='roles', action='update', category='authentication', description='Update role information'),
            Permission(name='roles:delete', resource='roles', action='delete', category='authentication', description='Delete roles'),
            
            # System permissions
            Permission(name='system:settings', resource='system', action='settings', category='system', description='Access system settings'),
            Permission(name='system:reports', resource='system', action='reports', category='system', description='Access system reports'),
            
            # Inventory permissions
            Permission(name='inventory:read', resource='inventory', action='read', category='inventory', description='View inventory'),
            Permission(name='inventory:create', resource='inventory', action='create', category='inventory', description='Create inventory items'),
            Permission(name='inventory:update', resource='inventory', action='update', category='inventory', description='Update inventory'),
            Permission(name='inventory:delete', resource='inventory', action='delete', category='inventory', description='Delete inventory items'),
            
            # POS permissions
            Permission(name='pos:read', resource='pos', action='read', category='pos', description='View POS operations'),
            Permission(name='pos:create', resource='pos', action='create', category='pos', description='Create sales transactions'),
            Permission(name='pos:update', resource='pos', action='update', category='pos', description='Update sales transactions'),
            Permission(name='pos:delete', resource='pos', action='delete', category='pos', description='Delete sales transactions'),
            
            # Admin full access
            Permission(name='admin:full_access', resource='admin', action='full_access', category='system', description='Full system access'),
        ]
        
        # Add permissions to database
        for permission in permissions:
            existing = db.session.query(Permission).filter_by(name=permission.name).first()
            if not existing:
                db.session.add(permission)
                print(f"Created permission: {permission.name}")
        
        db.session.commit()
        
        # Get or create Admin role
        admin_role = db.session.query(Role).filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator with full system access')
            db.session.add(admin_role)
            db.session.commit()
            print("Created Admin role")
        
        # Assign all permissions to Admin role
        for permission in permissions:
            existing_role_permission = db.session.query(RolePermission).filter_by(
                role_id=admin_role.id, 
                permission_id=permission.id
            ).first()
            
            if not existing_role_permission:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    is_active=True
                )
                db.session.add(role_permission)
                print(f"Assigned permission {permission.name} to Admin role")
        
        db.session.commit()
        print("Permission setup completed successfully!")

if __name__ == '__main__':
    setup_permissions() 