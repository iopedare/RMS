from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class RolePermission(db.Model):
    """
    RolePermission model for many-to-many relationship between roles and permissions.
    
    This model links roles to their assigned permissions and tracks when permissions
    were assigned or modified.
    """
    
    __tablename__ = 'role_permissions'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False, index=True)
    
    # Permission assignment status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # User relationships for audit fields
    created_by_user = relationship('User', foreign_keys=[created_by])
    updated_by_user = relationship('User', foreign_keys=[updated_by])
    
    # Relationships
    role = relationship('Role', back_populates='permissions', foreign_keys=[role_id])
    permission = relationship('Permission', back_populates='role_permissions', foreign_keys=[permission_id])
    
    def __init__(self, role_id, permission_id, **kwargs):
        """Initialize a new role permission assignment."""
        self.role_id = role_id
        self.permission_id = permission_id
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def activate(self):
        """Activate this permission assignment."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate this permission assignment."""
        self.is_active = False
    
    def to_dict(self):
        """Convert role permission to dictionary representation."""
        return {
            'id': self.id,
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'role_name': self.role.name if self.role else None,
            'permission_name': self.permission.name if self.permission else None
        }
    
    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>" 