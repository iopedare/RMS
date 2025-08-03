from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db


class AuditLog(db.Model):
    """
    AuditLog model for comprehensive security event tracking.
    
    This model tracks all security-related events including authentication,
    authorization, data access, and system operations for compliance and security.
    """
    
    __tablename__ = 'audit_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event information
    event_type = Column(String(100), nullable=False, index=True)  # e.g., 'login', 'logout', 'permission_denied'
    event_category = Column(String(50), nullable=False, index=True)  # e.g., 'authentication', 'authorization', 'data_access'
    severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    
    # User and session information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    device_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Event details
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional event data
    resource_type = Column(String(50), nullable=True)  # e.g., 'user', 'product', 'order'
    resource_id = Column(String(50), nullable=True)  # ID of the affected resource
    
    # Success/failure tracking
    is_success = Column(String(10), nullable=False, index=True)  # 'success', 'failure', 'warning'
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship('User', back_populates='audit_logs')
    
    def __init__(self, event_type, event_category, severity, description, is_success='success', **kwargs):
        """Initialize a new audit log entry."""
        self.event_type = event_type
        self.event_category = event_category
        self.severity = severity
        self.description = description
        self.is_success = is_success
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_authentication_event(cls, user_id, event_type, description, is_success='success', **kwargs):
        """Log an authentication-related event."""
        severity = 'high' if event_type in ['login_failed', 'account_locked', 'password_reset'] else 'medium'
        return cls(
            event_type=event_type,
            event_category='authentication',
            severity=severity,
            description=description,
            is_success=is_success,
            user_id=user_id,
            **kwargs
        )
    
    @classmethod
    def log_authorization_event(cls, user_id, event_type, description, is_success='success', **kwargs):
        """Log an authorization-related event."""
        severity = 'high' if event_type in ['permission_denied', 'unauthorized_access'] else 'medium'
        return cls(
            event_type=event_type,
            event_category='authorization',
            severity=severity,
            description=description,
            is_success=is_success,
            user_id=user_id,
            **kwargs
        )
    
    @classmethod
    def log_data_access_event(cls, user_id, event_type, description, resource_type=None, resource_id=None, **kwargs):
        """Log a data access event."""
        severity = 'medium'
        return cls(
            event_type=event_type,
            event_category='data_access',
            severity=severity,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            **kwargs
        )
    
    @classmethod
    def log_system_event(cls, event_type, description, severity='medium', **kwargs):
        """Log a system-level event."""
        return cls(
            event_type=event_type,
            event_category='system',
            severity=severity,
            description=description,
            **kwargs
        )
    
    def is_critical_event(self):
        """Check if this is a critical security event."""
        return self.severity == 'critical'
    
    def is_high_severity(self):
        """Check if this is a high severity event."""
        return self.severity in ['high', 'critical']
    
    def is_authentication_event(self):
        """Check if this is an authentication event."""
        return self.event_category == 'authentication'
    
    def is_authorization_event(self):
        """Check if this is an authorization event."""
        return self.event_category == 'authorization'
    
    def is_failed_event(self):
        """Check if this is a failed event."""
        return self.is_success == 'failure'
    
    def get_event_summary(self):
        """Get a summary of the event for reporting."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'severity': self.severity,
            'description': self.description,
            'is_success': self.is_success,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'ip_address': self.ip_address,
            'device_id': self.device_id
        }
    
    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'severity': self.severity,
            'description': self.description,
            'is_success': self.is_success,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'device_id': self.device_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'user_name': self.user.username if self.user else None
        }
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', severity='{self.severity}', created_at='{self.created_at}')>" 