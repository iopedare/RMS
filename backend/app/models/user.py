from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db
import bcrypt
import jwt
from datetime import datetime, timedelta
import os


class User(db.Model):
    """
    User model for authentication and user management.
    
    This model handles user authentication, role assignment, and session management.
    Includes security features like password hashing, account lockout, and audit tracking.
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Session management
    last_login = Column(DateTime, nullable=True)
    last_logout = Column(DateTime, nullable=True)
    current_session_id = Column(String(255), nullable=True)
    device_id = Column(String(255), nullable=True)  # For single device login
    
    # Security settings
    password_changed_at = Column(DateTime, nullable=True)
    password_expires_at = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Self-referencing relationships for audit fields
    created_by_user = relationship('User', foreign_keys=[created_by], remote_side=[id])
    updated_by_user = relationship('User', foreign_keys=[updated_by], remote_side=[id])
    
    # Relationships
    roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan', foreign_keys='UserRole.user_id')
    audit_logs = relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, first_name, last_name, **kwargs):
        """Initialize a new user with hashed password."""
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = self._hash_password(password)
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _hash_password(self, password):
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def change_password(self, new_password):
        """Change user password and update timestamp."""
        self.password_hash = self._hash_password(new_password)
        self.password_changed_at = datetime.utcnow()
        self.force_password_change = False
    
    def generate_jwt_token(self, expires_in=3600):
        """Generate JWT token for user authentication."""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'session_id': self.current_session_id
        }
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def check_password_policy(self, password):
        """Check if password meets security policy requirements."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password meets requirements"
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock account if necessary."""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= 5:
            self.is_locked = True
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        if not self.is_locked:
            return False
        
        if self.locked_until and datetime.utcnow() > self.locked_until:
            # Auto-unlock expired lock
            self.is_locked = False
            self.locked_until = None
            return False
        
        return True
    
    def get_full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def get_roles(self):
        """Get list of role names for this user."""
        return [user_role.role.name for user_role in self.roles]
    
    def has_permission(self, permission):
        """Check if user has a specific permission."""
        for user_role in self.roles:
            if user_role.role.has_permission(permission):
                return True
        return False
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return role_name in self.get_roles()
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.has_role('Admin')
    
    def can_override_single_device(self):
        """Check if user can override single device login restriction."""
        return self.is_admin()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'roles': self.get_roles()
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'current_session_id': self.current_session_id,
                'device_id': self.device_id,
                'password_changed_at': self.password_changed_at.isoformat() if self.password_changed_at else None,
                'password_expires_at': self.password_expires_at.isoformat() if self.password_expires_at else None,
                'force_password_change': self.force_password_change
            })
        
        return data
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>" 