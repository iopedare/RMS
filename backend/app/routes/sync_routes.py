from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.sync_event import SyncEvent
from app.models.device_role import DeviceRole
from app.models.sync_state import SyncState
from app.models.master_election_log import MasterElectionLog
from app.models.sync_audit_log import SyncAuditLog
import datetime

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/push', methods=['POST'])
def push_sync_event():
    """Endpoint for clients to push new sync events to the master node."""
    data = request.get_json()
    # Validate required fields
    required_fields = ['event_type', 'payload', 'device_id']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    # Create SyncEvent instance
    try:
        event = SyncEvent(
            event_type=data['event_type'],
            payload=data['payload'],
            device_id=data['device_id'],
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp', datetime.datetime.utcnow()),
            status='pending'
        )
        db.session.add(event)
        db.session.commit()
        # Log audit
        log = SyncAuditLog(
            event_type=data['event_type'],
            operation='push',
            status='success',
            device_id=data['device_id'],
            user_id=data.get('user_id'),
            details=f'Event {event.id} pushed'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log the error for debugging and audit
        log = SyncAuditLog(
            event_type=data.get('event_type'),
            operation='push',
            status='error',
            device_id=data.get('device_id'),
            user_id=data.get('user_id'),
            details=str(e)
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': f'Failed to queue event: {str(e)}'}), 500

    # (Optional) Trigger immediate sync for critical events
    # if event.event_type in ["stock_update", "critical_event"]:
    #     current_app.sync_manager.perform_immediate_sync(event)

    return jsonify({'message': 'Event queued', 'event_id': event.id}), 200

@sync_bp.route('/sync/pull', methods=['GET'])
def pull_sync_events():
    """Endpoint for clients to pull pending sync events from the master node."""
    from app.models.sync_event import SyncEvent
    from app import db
    import datetime

    device_id = request.args.get('device_id')
    since = request.args.get('since')

    # Validate device_id
    if not device_id:
        return jsonify({'error': 'Missing device_id parameter'}), 400

    # Build query for pending events not from this device
    query = SyncEvent.query.filter(SyncEvent.device_id != device_id, SyncEvent.status == 'pending')
    if since:
        try:
            since_dt = datetime.datetime.fromisoformat(since)
            query = query.filter(SyncEvent.timestamp > since_dt)
        except Exception:
            return jsonify({'error': 'Invalid since timestamp format. Use ISO format.'}), 400

    events = query.order_by(SyncEvent.timestamp.asc()).all()

    # Serialize events
    def serialize_event(event):
        return {
            'id': event.id,
            'event_type': event.event_type,
            'payload': event.payload,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'status': event.status,
            'device_id': event.device_id,
            'user_id': event.user_id
        }
    events_json = [serialize_event(e) for e in events]

    return jsonify({'events': events_json}), 200

@sync_bp.route('/sync/status', methods=['GET'])
def sync_status():
    """Endpoint to query sync status/history for a device/user."""
    from app.models.sync_event import SyncEvent
    from app import db
    import datetime

    device_id = request.args.get('device_id')
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 20))  # Limit history to last N events

    # Require at least one identifier
    if not device_id and not user_id:
        return jsonify({'error': 'Missing device_id or user_id parameter'}), 400

    # Build query for events
    query = SyncEvent.query
    if device_id:
        query = query.filter(SyncEvent.device_id == device_id)
    if user_id:
        query = query.filter(SyncEvent.user_id == user_id)
    events = query.order_by(SyncEvent.timestamp.desc()).limit(limit).all()

    # Summarize status
    total = query.count()
    pending = query.filter(SyncEvent.status == 'pending').count()
    synced = query.filter(SyncEvent.status == 'synced').count()
    failed = query.filter(SyncEvent.status == 'failed').count()

    # Serialize events
    def serialize_event(event):
        return {
            'id': event.id,
            'event_type': event.event_type,
            'payload': event.payload,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'status': event.status,
            'device_id': event.device_id,
            'user_id': event.user_id
        }
    events_json = [serialize_event(e) for e in events]

    return jsonify({
        'summary': {
            'total': total,
            'pending': pending,
            'synced': synced,
            'failed': failed
        },
        'history': events_json
    }), 200

@sync_bp.route('/device/register', methods=['POST'])
def register_device():
    """Endpoint for device registration from frontend."""
    data = request.get_json()
    device_id = data.get('device_id')
    role = data.get('role')
    if not device_id or not role:
        return jsonify({'error': 'Missing device_id or role'}), 400
    # Here you could add logic to store or validate the device
    return jsonify({'status': 'registered', 'device_id': device_id, 'role': role}), 200

# ===== ADVANCED SYNC ENDPOINTS =====

@sync_bp.route('/device/roles', methods=['GET'])
def get_device_roles():
    """Get all device roles."""
    try:
        devices = DeviceRole.query.all()
        return jsonify({
            'devices': [device.to_dict() for device in devices]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get device roles: {str(e)}'}), 500

@sync_bp.route('/device/roles/<device_id>', methods=['GET'])
def get_device_role(device_id):
    """Get specific device role."""
    try:
        device = DeviceRole.get_device_by_id(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify(device.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get device role: {str(e)}'}), 500

@sync_bp.route('/device/roles/<device_id>', methods=['PUT'])
def update_device_role(device_id):
    """Update device role."""
    data = request.get_json()
    new_role = data.get('role')
    reason = data.get('reason', 'manual')
    
    if not new_role:
        return jsonify({'error': 'Missing role parameter'}), 400
    
    try:
        device = DeviceRole.get_device_by_id(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        device.change_role(new_role, reason)
        return jsonify(device.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update device role: {str(e)}'}), 500

@sync_bp.route('/sync/state/<device_id>', methods=['GET'])
def get_sync_state(device_id):
    """Get sync state for a specific device."""
    try:
        sync_state = SyncState.get_device_sync_state(device_id)
        if not sync_state:
            return jsonify({'error': 'Sync state not found'}), 404
        return jsonify(sync_state.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get sync state: {str(e)}'}), 500

@sync_bp.route('/sync/state/<device_id>', methods=['PUT'])
def update_sync_state(device_id):
    """Update sync state for a specific device."""
    data = request.get_json()
    
    try:
        sync_state = SyncState.get_device_sync_state(device_id)
        if not sync_state:
            # Create new sync state if it doesn't exist
            sync_state = SyncState(device_id=device_id)
            db.session.add(sync_state)
        
        # Update fields
        if 'sync_status' in data:
            sync_state.sync_status = data['sync_status']
        if 'pending_changes_count' in data:
            sync_state.pending_changes_count = data['pending_changes_count']
        if 'last_error_message' in data:
            sync_state.last_error_message = data['last_error_message']
        
        db.session.commit()
        return jsonify(sync_state.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update sync state: {str(e)}'}), 500

@sync_bp.route('/sync/master-election-logs', methods=['GET'])
def get_master_election_logs():
    """Get master election logs."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    try:
        logs = MasterElectionLog.query.order_by(
            MasterElectionLog.election_timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'total': MasterElectionLog.query.count()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get master election logs: {str(e)}'}), 500

@sync_bp.route('/sync/audit-logs', methods=['GET'])
def get_sync_audit_logs():
    """Get sync audit logs with filtering."""
    device_id = request.args.get('device_id')
    event_type = request.args.get('event_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    try:
        query = SyncAuditLog.query
        
        # Apply filters
        if device_id:
            query = query.filter(SyncAuditLog.device_id == device_id)
        if event_type:
            query = query.filter(SyncAuditLog.event_type == event_type)
        if start_date:
            try:
                start_dt = datetime.datetime.fromisoformat(start_date)
                query = query.filter(SyncAuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
        if end_date:
            try:
                end_dt = datetime.datetime.fromisoformat(end_date)
                query = query.filter(SyncAuditLog.timestamp <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format.'}), 400
        
        logs = query.order_by(SyncAuditLog.timestamp.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'logs': [{
                'id': log.id,
                'event_type': log.event_type,
                'operation': log.operation,
                'status': log.status,
                'device_id': log.device_id,
                'user_id': log.user_id,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                'details': log.details
            } for log in logs],
            'total': query.count()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get audit logs: {str(e)}'}), 500 