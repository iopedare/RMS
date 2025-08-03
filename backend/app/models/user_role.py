from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class UserRole(db.Model):
    """
    UserRole model for many-to-many relationship between users and roles.
    
    This model links users to their assigned roles and tracks when roles
    were assigned or modified.
    """
    
    __tablename__ = 'user_roles'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    
    # Role assignment status
    is_active = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # Primary role for user
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # User relationships for audit fields
    created_by_user = relationship('User', foreign_keys=[created_by])
    updated_by_user = relationship('User', foreign_keys=[updated_by])
    
    # Relationships
    user = relationship('User', back_populates='roles', foreign_keys=[user_id])
    role = relationship('Role', back_populates='users', foreign_keys=[role_id])
    
    def __init__(self, user_id, role_id, **kwargs):
        """Initialize a new user role assignment."""
        self.user_id = user_id
        self.role_id = role_id
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def activate(self):
        """Activate this role assignment."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate this role assignment."""
        self.is_active = False
    
    def set_as_primary(self):
        """Set this as the primary role for the user."""
        self.is_primary = True
    
    def unset_as_primary(self):
        """Unset this as the primary role for the user."""
        self.is_primary = False
    
    def to_dict(self):
        """Convert user role to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'role_name': self.role.name if self.role else None,
            'user_name': self.user.username if self.user else None
        }
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>" 