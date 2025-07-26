# Example using SQLAlchemy ORM for sync event logging
from app.extensions import db
import datetime

class SyncEvent(db.Model):
    """
    ORM model for tracking sync events and logs.
    Stores event type, payload, timestamp, status, and originating device/user.
    Used for audit trail, troubleshooting, and replaying sync events if needed.
    """
    __tablename__ = 'sync_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String, nullable=False)  # e.g., 'stock_update', 'order', etc.
    payload = db.Column(db.JSON, nullable=False)       # The actual data being synced
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)  # When the event was created
    status = db.Column(db.String, default='pending', index=True)  # 'pending', 'synced', 'failed', etc.
    device_id = db.Column(db.String, nullable=False, index=True)  # Originating device
    user_id = db.Column(db.String, nullable=True, index=True)     # Originating user (if applicable)

    # Optional: Add an index for faster queries by device and status
    __table_args__ = (
        db.Index('ix_sync_events_device_status', 'device_id', 'status'),
    )

    def __repr__(self):
        return f"<SyncEvent(id={self.id}, type={self.event_type}, status={self.status}, device={self.device_id})>" 