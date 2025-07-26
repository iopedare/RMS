from app.extensions import db
import datetime

class DeviceRole(db.Model):
    """
    ORM model for tracking device roles, priorities, and status for master-client failover protocol.
    """
    __tablename__ = 'device_roles'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default='client')  # 'master', 'client'
    priority = db.Column(db.Integer, default=0, nullable=False)  # Higher priority = more likely to become master
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DeviceRole(id={self.id}, device_id={self.device_id}, role={self.role}, priority={self.priority})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'role': self.role,
            'priority': self.priority,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_master_device(cls):
        """Get the current master device."""
        return cls.query.filter_by(role='master', is_active=True).first()

    @classmethod
    def get_active_devices(cls):
        """Get all active devices."""
        return cls.query.filter_by(is_active=True).order_by(cls.priority.desc()).all()

    @classmethod
    def get_device_by_id(cls, device_id):
        """Get device by device_id."""
        return cls.query.filter_by(device_id=device_id).first()

    def update_last_seen(self):
        """Update the last_seen timestamp."""
        self.last_seen = datetime.datetime.utcnow()
        db.session.commit()

    def change_role(self, new_role, reason='manual'):
        """Change device role and log the change."""
        old_role = self.role
        self.role = new_role
        self.updated_at = datetime.datetime.utcnow()
        
        # Log the role change
        from app.models.sync_audit_log import SyncAuditLog
        audit_log = SyncAuditLog(
            event_type='role_change',
            operation='role_update',
            status='success',
            device_id=self.device_id,
            details=f"Role changed from {old_role} to {new_role} (reason: {reason})"
        )
        db.session.add(audit_log)
        db.session.commit()

    def deactivate(self):
        """Deactivate the device."""
        self.is_active = False
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit() 