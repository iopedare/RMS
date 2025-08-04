from app.extensions import db
import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List

class User(db.Model):
    """
    User model for authentication and authorization.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    device_id = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    current_session_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    role = db.relationship('Role', foreign_keys=[role_id])
    roles = db.relationship('UserRole', back_populates='user', foreign_keys='UserRole.user_id')
    audit_logs = db.relationship('AuditLog', back_populates='user', foreign_keys='AuditLog.user_id')
    created_by_user = db.relationship('User', foreign_keys=[created_by], remote_side=[id])

    def __init__(self, **kwargs):
        """Initialize a new user with optional password hashing."""
        # Handle password parameter if provided
        if 'password' in kwargs:
            password = kwargs.pop('password')
            super().__init__(**kwargs)
            self.set_password(password)
        else:
            super().__init__(**kwargs)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role_id={self.role_id})>"

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def verify_password(self, password):
        """Alias for check_password for compatibility with auth service."""
        return self.check_password(password)

    def check_password_policy(self, password):
        """
        Check if password meets security policy requirements.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password meets policy requirements"

    def is_admin(self):
        """Check if user has admin role."""
        for user_role in self.roles:
            if user_role.role.name == 'Admin':
                return True
        return False

    def can_override_single_device(self):
        """Check if user can override single device login restriction."""
        return self.is_admin()

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        for user_role in self.roles:
            if user_role.is_active and user_role.role.is_active:
                if user_role.role.has_permission(permission_name):
                    return True
        return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        for user_role in self.roles:
            if user_role.is_active and user_role.role.is_active:
                if user_role.role.name == role_name:
                    return True
        return False

    def get_roles(self) -> List[str]:
        """Get list of role names for user."""
        roles = []
        for user_role in self.roles:
            if user_role.is_active and user_role.role.is_active:
                roles.append(user_role.role.name)
        return roles

    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        return self.is_account_locked()

    def get_full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def is_account_locked(self):
        """Check if account is locked due to failed login attempts."""
        if self.locked_until and datetime.datetime.utcnow() < self.locked_until:
            return True
        return False

    def increment_failed_login(self):
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.locked_until = None

    def to_dict(self, include_sensitive=False):
        """Convert model to dictionary for JSON serialization."""
        data = {
            'id': self.id,
            'username': self.username,
            'role_id': self.role_id,
            'device_id': self.device_id,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'roles': [user_role.role.name for user_role in self.roles if user_role.is_active and user_role.role.is_active]
        }
        
        if include_sensitive:
            data['last_login'] = self.last_login.isoformat() if self.last_login else None
            data['current_session_id'] = self.current_session_id
        
        return data

    @classmethod
    def get_by_username(cls, username):
        """Get user by username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_device_id(cls, device_id):
        """Get user by device ID."""
        return cls.query.filter_by(device_id=device_id).first()
