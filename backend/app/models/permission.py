from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class Permission(db.Model):
    """
    Permission model for granular access control.
    
    This model defines individual permissions that can be assigned to roles.
    Permissions follow a resource:action format (e.g., 'users:create').
    """
    
    __tablename__ = 'permissions'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Permission information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False, index=True)  # e.g., 'users', 'inventory'
    action = Column(String(50), nullable=False, index=True)    # e.g., 'create', 'read', 'update'
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Permission category for organization
    category = Column(String(50), nullable=False, index=True)  # e.g., 'authentication', 'pos', 'inventory'
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # User relationships for audit fields
    created_by_user = relationship('User', foreign_keys=[created_by])
    updated_by_user = relationship('User', foreign_keys=[updated_by])
    
    # Relationships
    role_permissions = relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan', foreign_keys='RolePermission.permission_id')
    
    def __init__(self, name, resource, action, category, description=None, **kwargs):
        """Initialize a new permission."""
        self.name = name
        self.resource = resource
        self.action = action
        self.category = category
        self.description = description
        self.is_active = True  # Set default value
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_full_name(self):
        """Get the full permission name (resource:action)."""
        return f"{self.resource}:{self.action}"
    
    def is_wildcard_permission(self):
        """Check if this is a wildcard permission (e.g., '*:*')."""
        return self.resource == '*' or self.action == '*'
    
    def matches_permission(self, permission_name):
        """Check if this permission matches a given permission name."""
        if self.is_wildcard_permission():
            return True
        
        return self.name == permission_name
    
    def is_crud_permission(self):
        """Check if this is a CRUD operation permission."""
        crud_actions = ['create', 'read', 'update', 'delete']
        return self.action in crud_actions
    
    def is_system_permission(self):
        """Check if this is a system-level permission."""
        return self.category == 'system'
    
    def is_authentication_permission(self):
        """Check if this is an authentication permission."""
        return self.category == 'authentication'
    
    def is_financial_permission(self):
        """Check if this is a financial operation permission."""
        return self.category in ['pos', 'financial']
    
    def to_dict(self):
        """Convert permission to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'category': self.category,
            'is_active': self.is_active,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>" 