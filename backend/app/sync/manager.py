from app.extensions import db, socketio
from app.models.sync_event import SyncEvent
from app.services.conflict_resolver import ConflictResolver
from app.models.sync_audit_log import SyncAuditLog

class SyncManager:
    """
    Coordinates periodic and immediate sync logic for the backend.
    Handles queueing, batching, and dispatching sync events between clients and the master node.
    Responsible for triggering periodic sync, processing immediate sync requests, and integrating with WebSocket and REST APIs.
    """
    def __init__(self):
        self.conflict_resolver = ConflictResolver()

    def log_audit(self, event_type, operation, status, device_id=None, user_id=None, details=None):
        """Log a sync operation or error to the audit trail."""
        log = SyncAuditLog(
            event_type=event_type,
            operation=operation,
            status=status,
            device_id=device_id,
            user_id=user_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()

    def periodic_sync(self):
        """Trigger periodic sync for queued changes (to be called every 30 seconds)."""
        # Query all pending (non-critical) sync events
        pending_events = SyncEvent.query.filter(SyncEvent.status == 'pending').all()
        for event in pending_events:
            try:
                # Broadcast event to all clients (non-critical events)
                socketio.emit('sync_update', {
                    'id': event.id,
                    'event_type': event.event_type,
                    'payload': event.payload,
                    'timestamp': event.timestamp.isoformat() if event.timestamp else None,
                    'status': event.status,
                    'device_id': event.device_id,
                    'user_id': event.user_id
                }, broadcast=True)
                # Mark event as synced
                event.status = 'synced'
                self.log_audit('sync', 'periodic_broadcast', 'success', event.device_id, event.user_id, f'Event {event.id} broadcasted')
            except Exception as e:
                db.session.rollback()
                self.log_audit('sync', 'periodic_broadcast', 'error', event.device_id, event.user_id, str(e))
        db.session.commit()

    def immediate_sync(self, event):
        """Process an immediate sync event (e.g., critical stock change)."""
        try:
            socketio.emit('critical_event', {
                'id': event.id,
                'event_type': event.event_type,
                'payload': event.payload,
                'timestamp': event.timestamp.isoformat() if event.timestamp else None,
                'status': event.status,
                'device_id': event.device_id,
                'user_id': event.user_id
            }, broadcast=True)
            event.status = 'synced'
            self.log_audit('sync', 'immediate_broadcast', 'success', event.device_id, event.user_id, f'Critical event {event.id} broadcasted')
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.log_audit('sync', 'immediate_broadcast', 'error', event.device_id, event.user_id, str(e))

    def broadcast_update(self, update):
        """Broadcast updates to all connected clients via WebSocket."""
        pass

    def queue_event(self, event):
        """Queue a sync event for later synchronization, with conflict resolution."""
        # For demonstration, assume event.payload contains 'record_id' to identify the record
        record_id = event.payload.get('record_id')
        # Find existing event for the same record (if any)
        existing_event = SyncEvent.query.filter_by(payload={'record_id': record_id}).first()
        if existing_event:
            # Resolve conflict
            winner, status = self.conflict_resolver.resolve(existing_event, event)
            if winner == event:
                db.session.add(event)
                db.session.commit()
                return {'result': 'accepted', 'event_id': event.id}
            else:
                return {'result': 'rejected', 'event_id': existing_event.id}
        else:
            db.session.add(event)
            db.session.commit()
            return {'result': 'accepted', 'event_id': event.id} 