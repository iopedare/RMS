from app.extensions import db
import datetime

class SyncAuditLog(db.Model):
    """
    ORM model for logging all sync operations and errors for audit trail.
    """
    __tablename__ = 'sync_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String, nullable=True)  # e.g., 'sync', 'conflict', 'failover', etc.
    operation = db.Column(db.String, nullable=False)  # e.g., 'push', 'pull', 'broadcast', 'resolve', etc.
    status = db.Column(db.String, nullable=False)     # 'success', 'error', etc.
    device_id = db.Column(db.String, nullable=True)
    user_id = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    details = db.Column(db.Text, nullable=True)       # JSON or string with extra info

    def __repr__(self):
        return f"<SyncAuditLog(id={self.id}, op={self.operation}, status={self.status}, device={self.device_id})>" 