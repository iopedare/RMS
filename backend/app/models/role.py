from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class Role(db.Model):
    """
    Role model for role-based access control (RBAC).
    
    This model defines roles that can be assigned to users and contains
    the permissions associated with each role.
    """
    
    __tablename__ = 'roles'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Role information
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Role hierarchy
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    priority = Column(Integer, default=0, nullable=False)  # For master election
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # User relationships for audit fields
    created_by_user = relationship('User', foreign_keys=[created_by])
    updated_by_user = relationship('User', foreign_keys=[updated_by])
    
    # Relationships
    parent_role = relationship('Role', remote_side=[id], backref='child_roles')
    permissions = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan', foreign_keys='RolePermission.role_id')
    users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan', foreign_keys='UserRole.role_id')
    
    def __init__(self, name, description=None, **kwargs):
        """Initialize a new role."""
        self.name = name
        self.description = description
        self.is_active = True  # Set default value
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_permission(self, permission):
        """Add a permission to this role."""
        from .role_permission import RolePermission
        role_permission = RolePermission(role_id=self.id, permission_id=permission.id)
        self.permissions.append(role_permission)
        return role_permission
    
    def remove_permission(self, permission):
        """Remove a permission from this role."""
        for role_permission in self.permissions:
            if role_permission.permission_id == permission.id:
                self.permissions.remove(role_permission)
                break
    
    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        # Check direct permissions
        for role_permission in self.permissions:
            if role_permission.permission.name == permission_name:
                return True
        
        # Check inherited permissions from parent role
        if self.parent_role:
            return self.parent_role.has_permission(permission_name)
        
        return False
    
    def get_permissions(self):
        """Get list of permission names for this role."""
        permissions = set()
        
        # Add direct permissions
        for role_permission in self.permissions:
            permissions.add(role_permission.permission.name)
        
        # Add inherited permissions from parent role
        if self.parent_role:
            permissions.update(self.parent_role.get_permissions())
        
        return list(permissions)
    
    def get_all_permissions(self):
        """Get all permissions including inherited ones."""
        return self.get_permissions()
    
    def is_admin_role(self):
        """Check if this is an admin role."""
        return self.name == 'Admin'
    
    def can_manage_users(self):
        """Check if role can manage users."""
        return self.has_permission('users:create') or self.has_permission('users:update')
    
    def can_manage_roles(self):
        """Check if role can manage roles."""
        return self.has_permission('roles:create') or self.has_permission('roles:update')
    
    def can_access_system_settings(self):
        """Check if role can access system settings."""
        return self.has_permission('system:*') or self.has_permission('system:configure_sync')
    
    def get_role_hierarchy(self):
        """Get the role hierarchy as a list."""
        hierarchy = []
        current_role = self
        
        while current_role:
            hierarchy.append(current_role.name)
            current_role = current_role.parent_role
        
        return hierarchy[::-1]  # Reverse to get root to leaf order
    
    def get_child_roles(self):
        """Get all child roles recursively."""
        children = []
        
        for child in self.child_roles:
            children.append(child)
            children.extend(child.get_child_roles())
        
        return children
    
    def to_dict(self, include_permissions=False):
        """Convert role to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'priority': self.priority,
            'parent_role_id': self.parent_role_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'hierarchy': self.get_role_hierarchy()
        }
        
        if include_permissions:
            data['permissions'] = self.get_permissions()
        
        return data
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>" 