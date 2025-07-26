import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'dart:async';

// Callback function types for advanced sync events
typedef RoleChangeCallback = void Function(
    String deviceId, String newRole, String reason);
typedef MasterElectionCallback = void Function(
    String newMasterId, String reason);
typedef SyncStatusCallback = void Function(
    String deviceId, String status, Map<String, dynamic> details);
typedef SyncConflictCallback = void Function(
    String deviceId, Map<String, dynamic> conflictData);
typedef SyncErrorCallback = void Function(
    String deviceId, String error, Map<String, dynamic> details);

class SyncSocketService {
  IO.Socket? socket;

  // Callbacks for advanced sync events
  RoleChangeCallback? onRoleChange;
  MasterElectionCallback? onMasterElection;
  SyncStatusCallback? onSyncStatus;
  SyncConflictCallback? onSyncConflict;
  SyncErrorCallback? onSyncError;

  // Connection state
  bool _isConnected = false;
  bool _isReconnecting = false;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 10;
  static const int heartbeatInterval = 30000; // 30 seconds
  static const int heartbeatTimeout = 10000; // 10 seconds

  // Device info
  String? _deviceId;
  String? _currentRole;

  // Sync status tracking
  Map<String, dynamic> _syncState = {
    'status': 'disconnected',
    'lastSync': null,
    'pendingChanges': 0,
    'errorMessage': null,
  };

  bool get isConnected => _isConnected;
  bool get isReconnecting => _isReconnecting;
  Map<String, dynamic> get syncState => Map.unmodifiable(_syncState);

  void connect(String wsUrl, String deviceId, String role) {
    _deviceId = deviceId;
    _currentRole = role;

    socket = IO.io(wsUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
      'reconnection': false, // We'll handle reconnection manually
      'timeout': 20000,
      'forceNew': true,
    });

    _setupEventListeners();
    socket?.connect();
  }

  void _setupEventListeners() {
    socket?.onConnect((_) {
      print('Connected to backend');
      _isConnected = true;
      _isReconnecting = false;
      _reconnectAttempts = 0;
      _updateSyncState('connected', null);
      registerDevice(_deviceId!, _currentRole!);
      _startHeartbeat();
    });

    socket?.onDisconnect((_) {
      print('Socket disconnected');
      _isConnected = false;
      _stopHeartbeat();
      _updateSyncState('disconnected', 'Connection lost');
      _scheduleReconnection();
    });

    socket?.onConnectError((error) {
      print('Connection error: $error');
      _isConnected = false;
      _stopHeartbeat();
      _updateSyncState('error', 'Connection failed: $error');
      _scheduleReconnection();
    });

    // Basic sync events
    socket?.on('critical_event', (data) {
      print('Received critical_event: $data');
      _handleCriticalEvent(data);
    });

    socket?.on('registered', (data) {
      print('Device registered: $data');
      _updateSyncState('registered', null);
    });

    socket?.on('acknowledged', (data) {
      print('Acknowledgement received: $data');
    });

    // Advanced sync events
    socket?.on('role_change', (data) {
      print('Role change event: $data');
      _handleRoleChange(data);
    });

    socket?.on('master_election', (data) {
      print('Master election event: $data');
      _handleMasterElection(data);
    });

    // Add missing event listeners for new backend events
    socket?.on('device_online_ack', (data) {
      print('Device online acknowledged: $data');
      _handleDeviceOnlineAck(data);
    });

    socket?.on('device_offline_ack', (data) {
      print('Device offline acknowledged: $data');
      _handleDeviceOfflineAck(data);
    });

    socket?.on('master_elected', (data) {
      print('Master elected event: $data');
      _handleMasterElected(data);
    });

    socket?.on('role_change_ack', (data) {
      print('Role change acknowledged: $data');
      _handleRoleChangeAck(data);
    });

    socket?.on('sync_complete_ack', (data) {
      print('Sync complete acknowledged: $data');
      _handleSyncCompleteAck(data);
    });

    socket?.on('sync_conflict_resolved', (data) {
      print('Sync conflict resolved: $data');
      _handleSyncConflictResolved(data);
    });

    socket?.on('sync_error_ack', (data) {
      print('Sync error acknowledged: $data');
      _handleSyncErrorAck(data);
    });

    socket?.on('data_response', (data) {
      print('Data response received: $data');
      _handleDataResponse(data);
    });

    socket?.on('queue_status_response', (data) {
      print('Queue status response: $data');
      _handleQueueStatusResponse(data);
    });

    socket?.on('heartbeat_ack', (data) {
      print('Heartbeat acknowledged: $data');
      _handleHeartbeatAck(data);
    });

    socket?.on('sync_request', (data) {
      print('Sync request received: $data');
      _handleSyncRequest(data);
    });

    socket?.on('sync_response', (data) {
      print('Sync response received: $data');
      _handleSyncResponse(data);
    });

    socket?.on('sync_complete', (data) {
      print('Sync complete: $data');
      _handleSyncComplete(data);
    });

    socket?.on('sync_conflict', (data) {
      print('Sync conflict detected: $data');
      _handleSyncConflict(data);
    });

    socket?.on('sync_error', (data) {
      print('Sync error: $data');
      _handleSyncError(data);
    });

    socket?.on('data_update', (data) {
      print('Data update received: $data');
      _handleDataUpdate(data);
    });

    socket?.on('queue_status', (data) {
      print('Queue status update: $data');
      _handleQueueStatus(data);
    });

    socket?.on('error', (data) {
      print('Socket error: $data');
      _handleSocketError(data);
    });
  }

  void _scheduleReconnection() {
    if (_isReconnecting || _reconnectAttempts >= maxReconnectAttempts) {
      if (_reconnectAttempts >= maxReconnectAttempts) {
        print(
            'Max reconnection attempts reached. Manual reconnection required.');
        _updateSyncState('error', 'Max reconnection attempts reached');
      }
      return;
    }

    _isReconnecting = true;
    _reconnectAttempts++;

    final delay = _calculateReconnectDelay();
    print('Scheduling reconnection attempt $_reconnectAttempts in ${delay}ms');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(Duration(milliseconds: delay), () {
      if (!_isConnected && !_isReconnecting) {
        print('Attempting reconnection...');
        _attemptReconnection();
      }
    });
  }

  void _attemptReconnection() {
    if (_isConnected || _isReconnecting) return;

    _isReconnecting = true;
    print('Attempting reconnection...');

    try {
      socket?.connect();

      // Set a timeout for the reconnection attempt
      Timer(Duration(milliseconds: 10000), () {
        if (!_isConnected) {
          print('Reconnection attempt timed out');
          _isReconnecting = false;
          _scheduleReconnection();
        }
      });
    } catch (e) {
      print('Reconnection attempt failed: $e');
      _isReconnecting = false;
      _scheduleReconnection();
    }
  }

  int _calculateReconnectDelay() {
    // Exponential backoff with jitter
    final baseDelay =
        1000 * (1 << (_reconnectAttempts - 1)); // 1s, 2s, 4s, 8s...
    final jitter =
        (baseDelay * 0.1 * (DateTime.now().millisecondsSinceEpoch % 100)) / 100;
    return (baseDelay + jitter).round();
  }

  void _updateSyncState(String status, String? errorMessage) {
    _syncState['status'] = status;
    _syncState['lastSync'] = status == 'synced'
        ? DateTime.now().toIso8601String()
        : _syncState['lastSync'];
    _syncState['errorMessage'] = errorMessage;

    if (onSyncStatus != null) {
      onSyncStatus!(_deviceId!, status, _syncState);
    }
  }

  void _handleCriticalEvent(dynamic data) {
    // Handle critical events that require immediate attention
    if (data is Map<String, dynamic>) {
      final eventType = data['event_type'];
      final eventData = data['data'];

      switch (eventType) {
        case 'master_shutdown':
          _handleMasterShutdown(eventData);
          break;
        case 'network_partition':
          _handleNetworkPartition(eventData);
          break;
        case 'data_corruption':
          _handleDataCorruption(eventData);
          break;
        default:
          print('Unknown critical event type: $eventType');
      }
    }
  }

  void _handleRoleChange(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final newRole = data['new_role'];
      final reason = data['reason'] ?? 'unknown';

      if (deviceId == _deviceId) {
        _currentRole = newRole;
        print('Our role changed to: $newRole (reason: $reason)');
      }

      if (onRoleChange != null) {
        onRoleChange!(deviceId, newRole, reason);
      }
    }
  }

  void _handleMasterElection(dynamic data) {
    if (data is Map<String, dynamic>) {
      final newMasterId = data['new_master_id'];
      final reason = data['reason'] ?? 'unknown';
      final participants = data['participants'] ?? [];

      print(
          'Master election: $newMasterId elected (reason: $reason, participants: $participants)');

      if (onMasterElection != null) {
        onMasterElection!(newMasterId, reason);
      }
    }
  }

  void _handleSyncRequest(dynamic data) {
    if (data is Map<String, dynamic>) {
      final requestId = data['request_id'];
      final requestingDevice = data['requesting_device'];
      final syncType = data['sync_type'] ?? 'full';

      print('Sync request from $requestingDevice (type: $syncType)');

      // Respond to sync request
      emitSyncResponse(requestId, 'accepted', null);
    }
  }

  void _handleSyncResponse(dynamic data) {
    if (data is Map<String, dynamic>) {
      final requestId = data['request_id'];
      final status = data['status'];
      final responseData = data['data'];

      print('Sync response for request $requestId: $status');

      if (status == 'accepted') {
        // Proceed with data exchange
        emitDataRequest(requestId);
      }
    }
  }

  void _handleSyncComplete(dynamic data) {
    if (data is Map<String, dynamic>) {
      final requestId = data['request_id'];
      final changesCount = data['changes_count'] ?? 0;

      print('Sync completed for request $requestId with $changesCount changes');
      _updateSyncState('synced', null);
      _syncState['pendingChanges'] = 0;
    }
  }

  void _handleSyncConflict(dynamic data) {
    if (data is Map<String, dynamic>) {
      final conflictType = data['conflict_type'];
      final conflictData = data['conflict_data'];
      final deviceId = data['device_id'];

      print('Sync conflict detected: $conflictType');

      if (onSyncConflict != null) {
        onSyncConflict!(deviceId, data);
      }
    }
  }

  void _handleSyncError(dynamic data) {
    if (data is Map<String, dynamic>) {
      final error = data['error'];
      final details = data['details'] ?? {};
      final deviceId = data['device_id'];

      print('Sync error: $error');
      _updateSyncState('error', error);

      if (onSyncError != null) {
        onSyncError!(deviceId, error, details);
      }
    }
  }

  void _handleDataUpdate(dynamic data) {
    if (data is Map<String, dynamic>) {
      final updateType = data['update_type'];
      final updateData = data['data'];
      final sourceDevice = data['source_device'];

      print('Data update from $sourceDevice: $updateType');

      // Handle different types of data updates
      switch (updateType) {
        case 'product_update':
          _handleProductUpdate(updateData);
          break;
        case 'inventory_update':
          _handleInventoryUpdate(updateData);
          break;
        case 'order_update':
          _handleOrderUpdate(updateData);
          break;
        default:
          print('Unknown data update type: $updateType');
      }
    }
  }

  void _handleQueueStatus(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final queueSize = data['queue_size'] ?? 0;
      final pendingOperations = data['pending_operations'] ?? [];

      print('Queue status for $deviceId: $queueSize pending operations');

      _syncState['pendingChanges'] = queueSize;
      _updateSyncState('pending', null);
    }
  }

  void _handleSocketError(dynamic data) {
    print('Socket error: $data');
    _updateSyncState('error', 'Socket error: $data');
  }

  void _handleMasterShutdown(dynamic data) {
    print('Master device is shutting down');
    // Prepare for potential role change
  }

  void _handleNetworkPartition(dynamic data) {
    print('Network partition detected');
    _updateSyncState('partitioned', 'Network partition detected');
  }

  void _handleDataCorruption(dynamic data) {
    print('Data corruption detected');
    _updateSyncState('error', 'Data corruption detected');
  }

  // New event handler methods for advanced sync events
  void _handleDeviceOnlineAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final currentMaster = data['current_master'];
      final role = data['role'];

      print(
          'Device online acknowledged: $deviceId as $role, current master: $currentMaster');

      if (deviceId == _deviceId) {
        _currentRole = role;
        _updateSyncState('connected', null);
      }
    }
  }

  void _handleDeviceOfflineAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      print('Device offline acknowledged: $deviceId');

      // Prepare for potential role changes if this was the master
      if (deviceId != _deviceId) {
        print('Another device went offline, monitoring for role changes');
      }
    }
  }

  void _handleMasterElected(dynamic data) {
    if (data is Map<String, dynamic>) {
      final previousMasterId = data['previous_master_id'];
      final newMasterId = data['new_master_id'];
      final electionReason = data['election_reason'];
      final electionTimestamp = data['election_timestamp'];
      final devicesParticipating = data['devices_participating'];

      print(
          'Master election: $previousMasterId -> $newMasterId (reason: $electionReason)');

      // Update our role if we became the new master
      if (newMasterId == _deviceId) {
        _currentRole = 'master';
        print('We are now the master device');
      } else if (previousMasterId == _deviceId) {
        _currentRole = 'client';
        print('We are no longer the master device');
      }

      if (onMasterElection != null) {
        onMasterElection!(newMasterId, electionReason);
      }
    }
  }

  void _handleRoleChangeAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final newRole = data['new_role'];
      final reason = data['reason'];

      print(
          'Role change acknowledged: $deviceId -> $newRole (reason: $reason)');

      if (deviceId == _deviceId) {
        _currentRole = newRole;
        print('Our role changed to: $newRole');
      }

      if (onRoleChange != null) {
        onRoleChange!(deviceId, newRole, reason);
      }
    }
  }

  void _handleSyncCompleteAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final syncTimestamp = data['sync_timestamp'];
      final changesCount = data['changes_count'];

      print(
          'Sync complete acknowledged: $deviceId, $changesCount changes at $syncTimestamp');

      if (deviceId == _deviceId) {
        _updateSyncState('synced', null);
        _syncState['lastSync'] = syncTimestamp;
        _syncState['pendingChanges'] = 0;
      }
    }
  }

  void _handleSyncConflictResolved(dynamic data) {
    if (data is Map<String, dynamic>) {
      final tableName = data['table_name'];
      final recordId = data['record_id'];
      final resolutionMethod = data['resolution_method'];
      final resolvedData = data['resolved_data'];
      final timestamp = data['timestamp'];

      print(
          'Sync conflict resolved: $tableName:$recordId using $resolutionMethod');

      // Apply resolved data to local database
      _applyResolvedData(tableName, recordId, resolvedData);

      if (onSyncConflict != null) {
        onSyncConflict!(_deviceId!, {
          'table_name': tableName,
          'record_id': recordId,
          'resolution_method': resolutionMethod,
          'resolved_data': resolvedData,
        });
      }
    }
  }

  void _handleSyncErrorAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final errorMessage = data['error_message'];
      final errorCode = data['error_code'];
      final timestamp = data['timestamp'];

      print(
          'Sync error acknowledged: $deviceId - $errorMessage (code: $errorCode)');

      if (deviceId == _deviceId) {
        _updateSyncState('error', errorMessage);
      }

      if (onSyncError != null) {
        onSyncError!(deviceId, errorMessage, {
          'error_code': errorCode,
          'timestamp': timestamp,
        });
      }
    }
  }

  void _handleDataResponse(dynamic data) {
    if (data is Map<String, dynamic>) {
      final tableName = data['table_name'];
      final recordId = data['record_id'];
      final responseData = data['data'];
      final timestamp = data['timestamp'];

      print('Data response: $tableName:$recordId');

      // Update local data with response
      _updateLocalData(tableName, recordId, responseData);
    }
  }

  void _handleQueueStatusResponse(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      final queueType = data['queue_type'];
      final pendingCount = data['pending_count'];
      final lastProcessed = data['last_processed'];
      final status = data['status'];

      print(
          'Queue status response: $deviceId, $queueType queue - $pendingCount pending, status: $status');

      if (deviceId == _deviceId) {
        _syncState['pendingChanges'] = pendingCount;
        _syncState['queueStatus'] = status;
        _syncState['lastProcessed'] = lastProcessed;

        if (onSyncStatus != null) {
          onSyncStatus!(deviceId, status, _syncState);
        }
      }
    }
  }

  void _handleHeartbeatAck(dynamic data) {
    if (data is Map<String, dynamic>) {
      final deviceId = data['device_id'];
      print('Heartbeat acknowledged: $deviceId');

      // Reset heartbeat timer and update connection status
      _updateSyncState('connected', null);
    }
  }

  // Helper methods for data operations
  void _applyResolvedData(
      String tableName, int recordId, dynamic resolvedData) {
    // TODO: Implement actual database update logic
    print('Applying resolved data to $tableName:$recordId: $resolvedData');
  }

  void _updateLocalData(String tableName, int recordId, dynamic data) {
    // TODO: Implement actual database update logic
    print('Updating local data for $tableName:$recordId: $data');
  }

  // Heartbeat functionality for connection monitoring
  void _startHeartbeat() {
    _stopHeartbeat(); // Stop any existing heartbeat
    _heartbeatTimer =
        Timer.periodic(Duration(milliseconds: heartbeatInterval), (timer) {
      if (_isConnected && socket != null) {
        _sendHeartbeat();
      } else {
        _stopHeartbeat();
      }
    });
  }

  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }

  void _sendHeartbeat() {
    if (_isConnected && socket != null && _deviceId != null) {
      socket?.emit('heartbeat', {
        'device_id': _deviceId,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  }

  void _handleProductUpdate(dynamic data) {
    // Handle product updates
    print('Processing product update: $data');
  }

  void _handleInventoryUpdate(dynamic data) {
    // Handle inventory updates
    print('Processing inventory update: $data');
  }

  void _handleOrderUpdate(dynamic data) {
    // Handle order updates
    print('Processing order update: $data');
  }

  // Emit methods for advanced sync events
  void emitDeviceOnline() {
    socket?.emit('device_online', {
      'device_id': _deviceId,
      'role': _currentRole,
      'priority': 0, // Default priority
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitDeviceOffline() {
    socket?.emit('device_offline', {
      'device_id': _deviceId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitDeviceShutdown() {
    socket?.emit('device_shutdown', {
      'device_id': _deviceId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitMasterElection(String reason) {
    socket?.emit('master_election', {
      'reason': reason,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitRoleChange(String deviceId, String newRole, String reason) {
    socket?.emit('role_change', {
      'device_id': deviceId,
      'new_role': newRole,
      'reason': reason,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitSyncRequest(String targetDevice, String syncType) {
    final requestId = DateTime.now().millisecondsSinceEpoch.toString();
    socket?.emit('sync_request', {
      'device_id': _deviceId,
      'target_device': targetDevice,
      'sync_type': syncType,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitSyncResponse(String requestId, String status, dynamic data) {
    socket?.emit('sync_response', {
      'request_id': requestId,
      'responding_device': _deviceId,
      'status': status,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitSyncComplete(String deviceId, int changesCount) {
    socket?.emit('sync_complete', {
      'device_id': deviceId,
      'sync_timestamp': DateTime.now().toIso8601String(),
      'changes_count': changesCount,
    });
  }

  void emitSyncConflict(
      String deviceId, String tableName, int recordId, dynamic conflictData) {
    socket?.emit('sync_conflict', {
      'device_id': deviceId,
      'table_name': tableName,
      'record_id': recordId,
      'conflict_data': conflictData,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitSyncError(String deviceId, String errorMessage, String errorCode) {
    socket?.emit('sync_error', {
      'device_id': deviceId,
      'error_message': errorMessage,
      'error_code': errorCode,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitDataRequest(String requestId) {
    socket?.emit('data_request', {
      'device_id': _deviceId,
      'request_id': requestId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitDataResponse(String requestId, dynamic data) {
    socket?.emit('data_response', {
      'request_id': requestId,
      'responding_device': _deviceId,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitDataUpdate(
      String tableName, int recordId, dynamic newData, String operation) {
    socket?.emit('data_update', {
      'device_id': _deviceId,
      'table_name': tableName,
      'record_id': recordId,
      'new_data': newData,
      'operation': operation,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitQueueStatusRequest(String queueType) {
    socket?.emit('queue_status', {
      'device_id': _deviceId,
      'queue_type': queueType,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void emitHeartbeat() {
    _sendHeartbeat();
  }

  // Legacy methods for backward compatibility
  void registerDevice(String deviceId, String role) {
    socket?.emit('register_device', {'device_id': deviceId, 'role': role});
  }

  void acknowledge(String eventType, String deviceId) {
    socket
        ?.emit('acknowledge', {'event_type': eventType, 'device_id': deviceId});
  }

  void removeAllListeners() {
    if (socket != null) {
      socket!.clearListeners();
    }
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
    _isReconnecting = false;
    _reconnectAttempts = 0;
    _isConnected = false;
    socket?.disconnect();
    socket?.dispose();
    socket = null;
    _updateSyncState('disconnected', null);
  }

  // Manual reconnection
  void reconnect() {
    if (!_isConnected && !_isReconnecting) {
      _reconnectAttempts = 0;
      socket?.connect();
    }
  }

  // Get current device info
  String? get deviceId => _deviceId;
  String? get currentRole => _currentRole;
}
