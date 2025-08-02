from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
from datetime import datetime
from app.models import DeviceRole, SyncState, MasterElectionLog, SyncAuditLog
from app.extensions import db
from app.utils.validation import validate_device_registration_data, validate_sync_event_data

# SocketIO instance will be initialized in app/__init__.py

"""
This module defines SocketIO event handlers for real-time sync operations.
"""

connected_devices = {}
master_device_id = None
device_priorities = {}  # Track device priorities for master election

def register_socketio_events(socketio: SocketIO):
    """Register all sync-related SocketIO event handlers."""

    @socketio.on('connect')
    def handle_connect():
        """Handle new device connection."""
        # TODO: Add authentication/registration logic
        emit('connected', {'message': 'Connected to sync server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle device disconnection."""
        # TODO: Handle cleanup if needed
        print('Client disconnected')

    # ===== DEVICE MANAGEMENT EVENTS =====

    @socketio.on('device_online')
    def handle_device_online(data):
        """Handle device coming back online."""
        # Validate input data
        is_valid, error_msg, validated_data = validate_device_registration_data(data)
        if not is_valid:
            emit('error', {'error': error_msg})
            return
        
        device_id = validated_data['device_id']
        role = validated_data['role']
        priority = validated_data['priority']
        now = datetime.now()
        
        # Upsert DeviceRole
        device = DeviceRole.get_device_by_id(device_id)
        if not device:
            device = DeviceRole(device_id=device_id, role=role, priority=priority, last_seen=now, is_active=True)
            db.session.add(device)
        else:
            device.role = role
            device.priority = priority
            device.last_seen = now
            device.is_active = True
        db.session.commit()
        # Audit log
        audit = SyncAuditLog(event_type='device_online', operation='online', status='success', device_id=device_id, details=f"Device online as {role}")
        db.session.add(audit)
        db.session.commit()
        
        # If this device was previously master, it becomes client to current master
        global master_device_id
        if role == 'master' and master_device_id and master_device_id != device_id:
            device.change_role('client', reason='former_master_restart')
            emit('role_change', {
                'device_id': device_id,
                'new_role': 'client',
                'reason': 'former_master_restart'
            }, broadcast=True)
        
        print(f"Device {device_id} came online with role: {role}")
        emit('device_online_ack', {
            'device_id': device_id,
            'current_master': master_device_id,
            'role': device.role
        })

    @socketio.on('device_offline')
    def handle_device_offline(data):
        """Handle device going offline gracefully."""
        device_id = data.get('device_id')
        
        if device_id in connected_devices:
            connected_devices[device_id]['is_active'] = False
            connected_devices[device_id]['last_seen'] = datetime.now().isoformat()
            
            print(f"Device {device_id} went offline")
            emit('device_offline_ack', {'device_id': device_id})

    @socketio.on('device_shutdown')
    def handle_device_shutdown(data):
        """Handle master device shutdown and trigger master election."""
        device_id = data.get('device_id')
        
        if device_id == master_device_id:
            # Master is shutting down, trigger master election
            trigger_master_election(socketio, 'shutdown')
        else:
            # Regular client shutdown
            handle_device_offline(data)

    @socketio.on('master_election')
    def handle_master_election(data):
        """Handle master election process."""
        election_reason = data.get('reason', 'manual')
        # Find eligible devices
        eligible_devices = DeviceRole.get_active_devices()
        if not eligible_devices:
            print("No eligible devices for master election")
            return
        # Sort by priority
        eligible_devices.sort(key=lambda d: d.priority, reverse=True)
        new_master = eligible_devices[0]
        old_master = DeviceRole.get_master_device()
        if old_master:
            old_master.change_role('client', reason=election_reason)
        new_master.change_role('master', reason=election_reason)
        db.session.commit()
        # Log election
        election_log = MasterElectionLog(
            previous_master_id=old_master.device_id if old_master else None,
            new_master_id=new_master.device_id,
            election_reason=election_reason,
            election_timestamp=datetime.now(),
            devices_participating=len(eligible_devices)
        )
        db.session.add(election_log)
        db.session.commit()
        # Audit log
        audit = SyncAuditLog(event_type='master_election', operation='election', status='success', device_id=new_master.device_id, details=f"Master elected: {new_master.device_id} (reason: {election_reason})")
        db.session.add(audit)
        db.session.commit()
        # Notify all devices
        election_data = {
            'previous_master_id': old_master.device_id if old_master else None,
            'new_master_id': new_master.device_id,
            'election_reason': election_reason,
            'election_timestamp': datetime.now().isoformat(),
            'devices_participating': len(eligible_devices)
        }
        print(f"Master election: {old_master.device_id if old_master else None} -> {new_master.device_id} (reason: {election_reason})")
        socketio.emit('master_elected', election_data, broadcast=True)

    @socketio.on('role_change')
    def handle_role_change(data):
        """Handle device role change notification."""
        device_id = data.get('device_id')
        new_role = data.get('new_role')
        reason = data.get('reason', 'manual')
        device = DeviceRole.get_device_by_id(device_id)
        if device:
            device.change_role(new_role, reason=reason)
            db.session.commit()
            
            if new_role == 'master':
                global master_device_id
                master_device_id = device_id
            
            print(f"Device {device_id} role changed to {new_role} (reason: {reason})")
            emit('role_change_ack', {
                'device_id': device_id,
                'new_role': new_role,
                'reason': reason
            }, broadcast=True)

    # ===== SYNC EVENTS =====

    @socketio.on('sync_request')
    def handle_sync_request(data):
        """Handle sync request from client to master."""
        device_id = data.get('device_id')
        sync_type = data.get('sync_type', 'full')  # 'full', 'incremental'
        last_sync_timestamp = data.get('last_sync_timestamp')
        
        if not device_id:
            emit('error', {'error': 'Missing device_id'})
            return
        
        # Update SyncState
        sync_state = SyncState.get_device_sync_state(device_id)
        if not sync_state:
            sync_state = SyncState(device_id=device_id, sync_status='pending', pending_changes_count=0)
            db.session.add(sync_state)
        else:
            sync_state.sync_status = 'pending'
            sync_state.updated_at = datetime.now()
        db.session.commit()
        # Audit log
        audit = SyncAuditLog(event_type='sync', operation='request', status='pending', device_id=device_id, details=f"Sync requested: {sync_type}")
        db.session.add(audit)
        db.session.commit()

        # Only master can respond to sync requests
        if device_id != master_device_id:
            emit('sync_error', {
                'error': 'Only master can respond to sync requests',
                'device_id': device_id
            })
            return
        
        # TODO: Implement actual sync logic here
        # For now, send a mock sync response
        sync_data = {
            'sync_type': sync_type,
            'timestamp': datetime.now().isoformat(),
            'changes': [],  # TODO: Get actual changes from database
            'master_device_id': master_device_id
        }
        
        emit('sync_response', sync_data)

    @socketio.on('sync_response')
    def handle_sync_response(data):
        """Handle sync response from master to client."""
        # This is typically handled by the requesting client
        # Master broadcasts sync response to requesting client
        target_device_id = data.get('target_device_id')
        sync_data = data.get('sync_data', {})
        
        if target_device_id in connected_devices:
            target_sid = connected_devices[target_device_id]['sid']
            emit('sync_response', sync_data, room=target_sid)

    @socketio.on('sync_complete')
    def handle_sync_complete(data):
        """Handle sync completion notification."""
        device_id = data.get('device_id')
        sync_timestamp = data.get('sync_timestamp')
        changes_count = data.get('changes_count', 0)
        
        sync_state = SyncState.get_device_sync_state(device_id)
        if sync_state:
            sync_state.update_last_sync()
        # Audit log
        audit = SyncAuditLog(event_type='sync', operation='complete', status='success', device_id=device_id, details=f"Sync completed: {changes_count} changes at {sync_timestamp}")
        db.session.add(audit)
        db.session.commit()

        print(f"Sync completed for device {device_id}: {changes_count} changes")
        emit('sync_complete_ack', {
            'device_id': device_id,
            'sync_timestamp': sync_timestamp,
            'changes_count': changes_count
        }, broadcast=True)

    @socketio.on('sync_conflict')
    def handle_sync_conflict(data):
        """Handle sync conflict detection and resolution."""
        device_id = data.get('device_id')
        table_name = data.get('table_name')
        record_id = data.get('record_id')
        conflict_data = data.get('conflict_data', {})
        
        # Master resolves conflicts using last-writer-wins
        resolution = {
            'table_name': table_name,
            'record_id': record_id,
            'resolution_method': 'last_writer_wins',
            'resolved_data': conflict_data.get('newest', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Sync conflict resolved for {table_name}:{record_id}")
        emit('sync_conflict_resolved', resolution, broadcast=True)

    @socketio.on('sync_error')
    def handle_sync_error(data):
        """Handle sync error notification."""
        device_id = data.get('device_id')
        error_message = data.get('error_message')
        error_code = data.get('error_code')
        
        sync_state = SyncState.get_device_sync_state(device_id)
        if sync_state:
            sync_state.update_sync_status('error', error_message=error_message)
        # Audit log
        audit = SyncAuditLog(event_type='sync', operation='error', status='error', device_id=device_id, details=f"Sync error: {error_message} (code: {error_code})")
        db.session.add(audit)
        db.session.commit()

        print(f"Sync error for device {device_id}: {error_message}")
        emit('sync_error_ack', {
            'device_id': device_id,
            'error_message': error_message,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat()
        })

    # ===== DATA EVENTS =====

    @socketio.on('data_update')
    def handle_data_update(data):
        """Handle data update and broadcast to all clients."""
        device_id = data.get('device_id')
        table_name = data.get('table_name')
        record_id = data.get('record_id')
        new_data = data.get('new_data', {})
        operation = data.get('operation', 'update')  # 'insert', 'update', 'delete'
        
        if not all([device_id, table_name, record_id]):
            emit('error', {'error': 'Missing required fields for data update'})
            return
        
        # Broadcast update to all connected clients
        update_payload = {
            'device_id': device_id,
            'table_name': table_name,
            'record_id': record_id,
            'new_data': new_data,
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Broadcasting data update: {table_name}:{record_id}")
        emit('data_update', update_payload, broadcast=True)

    @socketio.on('data_request')
    def handle_data_request(data):
        """Handle data request from client to master."""
        device_id = data.get('device_id')
        table_name = data.get('table_name')
        record_id = data.get('record_id')
        
        if not all([device_id, table_name, record_id]):
            emit('error', {'error': 'Missing required fields for data request'})
            return
        
        # Only master can respond to data requests
        if device_id != master_device_id:
            emit('data_error', {
                'error': 'Only master can respond to data requests',
                'device_id': device_id
            })
            return
        
        # TODO: Implement actual data retrieval logic
        # For now, send a mock response
        response_data = {
            'table_name': table_name,
            'record_id': record_id,
            'data': {},  # TODO: Get actual data from database
            'timestamp': datetime.now().isoformat()
        }
        
        emit('data_response', response_data)

    @socketio.on('data_response')
    def handle_data_response(data):
        """Handle data response from master to client."""
        # This is typically handled by the requesting client
        # Master broadcasts data response to requesting client
        target_device_id = data.get('target_device_id')
        response_data = data.get('response_data', {})
        
        if target_device_id in connected_devices:
            target_sid = connected_devices[target_device_id]['sid']
            emit('data_response', response_data, room=target_sid)

    @socketio.on('queue_status')
    def handle_queue_status(data):
        """Handle sync queue status request/response."""
        device_id = data.get('device_id')
        queue_type = data.get('queue_type', 'sync')  # 'sync', 'offline'
        
        # TODO: Implement actual queue status logic
        queue_status = {
            'device_id': device_id,
            'queue_type': queue_type,
            'pending_count': 0,  # TODO: Get actual pending count
            'last_processed': datetime.now().isoformat(),
            'status': 'idle'  # 'idle', 'processing', 'error'
        }
        
        emit('queue_status_response', queue_status)

    # ===== LEGACY EVENTS (keeping for backward compatibility) =====

    @socketio.on('critical_event')
    def handle_critical_event(data):
        """Broadcast a critical sync event to all connected clients."""
        # Validate required fields for a critical event
        required_fields = ['event_type', 'payload', 'device_id']
        missing = [f for f in required_fields if f not in data]
        if missing:
            emit('error', {'error': f'Missing fields: {", ".join(missing)}'})
            return
        # Log the event (could also queue in DB if needed)
        print(f"Broadcasting critical event: {data}")
        # Broadcast to all clients
        emit('critical_event', data, broadcast=True)

    @socketio.on('acknowledge')
    def handle_acknowledge(data):
        """Handle client acknowledgement of a critical event (optional, for reliability/audit)."""
        # Log acknowledgement for audit
        print(f"Acknowledgement received: {data}")
        # Optionally, update event status in DB or perform other logic
        emit('acknowledged', {'message': 'Acknowledgement received'})

    @socketio.on('register_device')
    def handle_register_device(data):
        """Register a device and announce its role (master/client)."""
        # Validate input data
        is_valid, error_msg, validated_data = validate_device_registration_data(data)
        if not is_valid:
            emit('error', {'error': error_msg})
            return
        
        device_id = validated_data['device_id']
        role = validated_data['role']
        priority = validated_data['priority']
        
        connected_devices[device_id] = {
            'sid': request.sid,
            'role': role,
            'priority': priority,
            'last_seen': datetime.now().isoformat(),
            'is_active': True
        }
        
        global master_device_id
        if role == 'master':
            master_device_id = device_id
        
        emit('registered', {'device_id': device_id, 'role': role})

    @socketio.on('heartbeat')
    def handle_heartbeat(data):
        """Handle heartbeat from device to detect master failure."""
        device_id = data.get('device_id')
        # Update last seen timestamp, etc. (for demo, just acknowledge)
        emit('heartbeat_ack', {'device_id': device_id})

def trigger_master_election(socketio, reason='manual'):
    """Trigger master election process."""
    global master_device_id
    
    # Find the device with highest priority that is active
    eligible_devices = [
        (device_id, info) for device_id, info in connected_devices.items()
        if info['is_active'] and info['role'] != 'master'
    ]
    
    if not eligible_devices:
        print("No eligible devices for master election")
        return
    
    # Sort by priority (higher priority first)
    eligible_devices.sort(key=lambda x: x[1]['priority'], reverse=True)
    new_master_id = eligible_devices[0][0]
    
    # Update master
    old_master_id = master_device_id
    master_device_id = new_master_id
    connected_devices[new_master_id]['role'] = 'master'
    
    # Notify all devices of the new master
    election_data = {
        'previous_master_id': old_master_id,
        'new_master_id': new_master_id,
        'election_reason': reason,
        'election_timestamp': datetime.now().isoformat(),
        'devices_participating': len(eligible_devices)
    }
    
    print(f"Master election: {old_master_id} -> {new_master_id} (reason: {reason})")
    socketio.emit('master_elected', election_data, broadcast=True) 