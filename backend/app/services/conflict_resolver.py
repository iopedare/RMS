"""
ConflictResolver: Handles conflict resolution logic for sync events.
Implements first-come, first-served by timestamp and other strategies as needed.
"""

from app.models.sync_audit_log import SyncAuditLog
from app.extensions import db

class ConflictResolver:
    def resolve(self, event_a, event_b):
        """Resolve a conflict between two events. Returns (winning_event, resolution_status)."""
        # Compare timestamps (first-come, first-served)
        if event_a.timestamp <= event_b.timestamp:
            # event_a wins
            log = SyncAuditLog(
                event_type='conflict',
                operation='resolve',
                status='accepted',
                device_id=event_a.device_id,
                user_id=event_a.user_id,
                details=f'event_a wins: {event_a.id} vs {event_b.id}'
            )
            db.session.add(log)
            db.session.commit()
            return event_a, 'accepted'
        else:
            # event_b wins
            log = SyncAuditLog(
                event_type='conflict',
                operation='resolve',
                status='rejected',
                device_id=event_b.device_id,
                user_id=event_b.user_id,
                details=f'event_b wins: {event_b.id} vs {event_a.id}'
            )
            db.session.add(log)
            db.session.commit()
            return event_b, 'rejected' 