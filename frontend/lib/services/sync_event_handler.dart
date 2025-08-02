import 'package:flutter/foundation.dart';
import '../providers/sync_state_provider.dart';

class SyncEventHandler {
  final SyncStateProvider _stateProvider;

  SyncEventHandler(this._stateProvider);

  void handleEvent(Map<String, dynamic> eventData) {
    try {
      final event = SyncEvent.fromJson(eventData);
      
      switch (event.eventType) {
        case 'device_online':
          _handleDeviceOnline(event);
          break;
        case 'device_offline':
          _handleDeviceOffline(event);
          break;
        case 'master_election':
          _handleMasterElection(event);
          break;
        case 'critical_event':
          _handleCriticalEvent(event);
          break;
        case 'sync_request':
          _handleSyncRequest(event);
          break;
        case 'sync_response':
          _handleSyncResponse(event);
          break;
        case 'role_change':
          _handleRoleChange(event);
          break;
        case 'error':
          _handleError(event);
          break;
        default:
          print('⚠️ Unknown event type: ${event.eventType}');
      }

      // Add to history
      _stateProvider.addEventToHistory(event);
      
    } catch (e) {
      print('❌ Error handling event: $e');
    }
  }

  void _handleDeviceOnline(SyncEvent event) {
    final deviceId = event.payload['device_id'];
    final role = event.payload['role'];
    final priority = event.payload['priority'];

    print('🟢 Device online: $deviceId (Role: $role, Priority: $priority)');

    // Update state if this is our device
    if (deviceId == _stateProvider.deviceId) {
      _stateProvider.updateRole(role);
      _stateProvider.updateStatus(SyncStatus.connected);
      _stateProvider.updateLastSync(DateTime.now());
    }
  }

  void _handleDeviceOffline(SyncEvent event) {
    final deviceId = event.payload['device_id'];
    print('🔴 Device offline: $deviceId');

    // If the master device went offline, clear master
    if (deviceId == _stateProvider.masterDeviceId) {
      _stateProvider.setMasterDevice('');
      print('👑 Master device went offline');
    }
  }

  void _handleMasterElection(SyncEvent event) {
    final masterDeviceId = event.payload['master_device_id'];
    final masterRole = event.payload['master_role'];
    final electionReason = event.payload['election_reason'];

    print('👑 Master election: $masterDeviceId (Role: $masterRole, Reason: $electionReason)');

    _stateProvider.setMasterDevice(masterDeviceId);

    // If we became the master, update our role
    if (masterDeviceId == _stateProvider.deviceId) {
      _stateProvider.updateRole(masterRole);
      print('🎭 We are now the master device');
    }
  }

  void _handleCriticalEvent(SyncEvent event) {
    final eventType = event.payload['event_type'];
    final payload = event.payload['payload'];
    final sourceDeviceId = event.payload['device_id'];

    print('🚨 Critical event: $eventType from $sourceDeviceId');

    // Handle different critical event types
    switch (eventType) {
      case 'stock_update':
        _handleStockUpdate(payload);
        break;
      case 'price_change':
        _handlePriceChange(payload);
        break;
      case 'inventory_alert':
        _handleInventoryAlert(payload);
        break;
      case 'system_maintenance':
        _handleSystemMaintenance(payload);
        break;
      default:
        print('⚠️ Unknown critical event type: $eventType');
    }
  }

  void _handleSyncRequest(SyncEvent event) {
    final requestingDeviceId = event.payload['requesting_device_id'];
    final syncType = event.payload['sync_type'];

    print('📡 Sync request from $requestingDeviceId (Type: $syncType)');

    // If we're the master, we should respond
    if (_stateProvider.isMaster) {
      _handleSyncRequestAsMaster(event);
    }
  }

  void _handleSyncResponse(SyncEvent event) {
    final responseData = event.payload;
    print('📡 Sync response received');

    // Process sync response data
    _processSyncResponse(responseData);
  }

  void _handleRoleChange(SyncEvent event) {
    final deviceId = event.payload['device_id'];
    final newRole = event.payload['new_role'];
    final oldRole = event.payload['old_role'];

    print('🎭 Role change: $deviceId ($oldRole → $newRole)');

    // Update our role if it's our device
    if (deviceId == _stateProvider.deviceId) {
      _stateProvider.updateRole(newRole);
    }
  }

  void _handleError(SyncEvent event) {
    final errorMessage = event.payload['error'] ?? 'Unknown error';
    final errorCode = event.payload['error_code'];

    print('❌ Sync error: $errorMessage (Code: $errorCode)');

    _stateProvider.updateStatus(SyncStatus.error);
  }

  // Specific event handlers
  void _handleStockUpdate(Map<String, dynamic> payload) {
    final productId = payload['product_id'];
    final quantity = payload['quantity'];
    final action = payload['action']; // 'add', 'remove', 'set'

    print('📦 Stock update: Product $productId, Action: $action, Quantity: $quantity');
    
    // TODO: Update local inventory data
    // This would integrate with your inventory management system
  }

  void _handlePriceChange(Map<String, dynamic> payload) {
    final productId = payload['product_id'];
    final oldPrice = payload['old_price'];
    final newPrice = payload['new_price'];

    print('💰 Price change: Product $productId, $oldPrice → $newPrice');
    
    // TODO: Update local pricing data
  }

  void _handleInventoryAlert(Map<String, dynamic> payload) {
    final productId = payload['product_id'];
    final alertType = payload['alert_type']; // 'low_stock', 'out_of_stock', 'expiring'
    final message = payload['message'];

    print('⚠️ Inventory alert: $alertType for Product $productId - $message');
    
    // TODO: Show alert to user
  }

  void _handleSystemMaintenance(Map<String, dynamic> payload) {
    final maintenanceType = payload['maintenance_type'];
    final scheduledTime = payload['scheduled_time'];
    final duration = payload['duration'];

    print('🔧 System maintenance: $maintenanceType at $scheduledTime for $duration');
    
    // TODO: Show maintenance notification to user
  }

  void _handleSyncRequestAsMaster(SyncEvent event) {
    final requestingDeviceId = event.payload['requesting_device_id'];
    final syncType = event.payload['sync_type'];

    print('👑 Processing sync request as master for $requestingDeviceId');

    // TODO: Prepare sync data based on syncType
    // This would involve gathering the requested data and sending a sync_response
  }

  void _processSyncResponse(Map<String, dynamic> responseData) {
    final syncType = responseData['sync_type'];
    final data = responseData['data'];
    final timestamp = responseData['timestamp'];

    print('📡 Processing sync response for $syncType');

    // TODO: Process the sync data based on type
    // This would update local data stores
  }

  // Utility methods
  void handleConnectionEstablished() {
    _stateProvider.updateStatus(SyncStatus.connected);
    _stateProvider.updateLastSync(DateTime.now());
    print('✅ Connection established');
  }

  void handleConnectionLost() {
    _stateProvider.updateStatus(SyncStatus.disconnected);
    print('🔌 Connection lost');
  }

  void handleReconnectionAttempt() {
    _stateProvider.updateStatus(SyncStatus.reconnecting);
    print('🔄 Attempting reconnection');
  }

  void handleConnectionError(String error) {
    _stateProvider.updateStatus(SyncStatus.error);
    print('❌ Connection error: $error');
  }
} 