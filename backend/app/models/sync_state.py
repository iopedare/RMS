from app.extensions import db
import datetime

class SyncState(db.Model):
    """
    ORM model for tracking sync status and pending changes for each device.
    """
    __tablename__ = 'sync_state'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(255), nullable=False, index=True)
    last_sync_timestamp = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.String(50), default='synced', nullable=False)  # 'synced', 'pending', 'error'
    pending_changes_count = db.Column(db.Integer, default=0, nullable=False)
    last_error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SyncState(id={self.id}, device_id={self.device_id}, status={self.sync_status}, pending={self.pending_changes_count})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'last_sync_timestamp': self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            'sync_status': self.sync_status,
            'pending_changes_count': self.pending_changes_count,
            'last_error_message': self.last_error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_device_sync_state(cls, device_id):
        """Get sync state for a specific device."""
        return cls.query.filter_by(device_id=device_id).first()

    @classmethod
    def get_devices_with_pending_changes(cls):
        """Get all devices with pending changes."""
        return cls.query.filter(cls.pending_changes_count > 0).all()

    @classmethod
    def get_devices_with_errors(cls):
        """Get all devices with sync errors."""
        return cls.query.filter_by(sync_status='error').all()

    def update_sync_status(self, status, error_message=None):
        """Update sync status and optionally error message."""
        self.sync_status = status
        if error_message:
            self.last_error_message = error_message
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit()

    def update_last_sync(self):
        """Update last sync timestamp and reset status."""
        self.last_sync_timestamp = datetime.datetime.utcnow()
        self.sync_status = 'synced'
        self.last_error_message = None
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit()

    def increment_pending_changes(self, count=1):
        """Increment pending changes count."""
        self.pending_changes_count += count
        self.sync_status = 'pending'
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit()

    def decrement_pending_changes(self, count=1):
        """Decrement pending changes count."""
        self.pending_changes_count = max(0, self.pending_changes_count - count)
        if self.pending_changes_count == 0:
            self.sync_status = 'synced'
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit()

    def reset_pending_changes(self):
        """Reset pending changes count to zero."""
        self.pending_changes_count = 0
        self.sync_status = 'synced'
        self.updated_at = datetime.datetime.utcnow()
        db.session.commit() 