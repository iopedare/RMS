import 'dart:async';
import 'package:flutter/foundation.dart';
import 'sync_websocket_service.dart';
import 'sync_event_handler.dart';
import '../providers/sync_state_provider.dart';

class SyncService {
  final SyncWebSocketService _webSocketService;
  final SyncEventHandler _eventHandler;
  final SyncStateProvider _stateProvider;

  StreamSubscription? _eventSubscription;
  StreamSubscription? _connectionStatusSubscription;
  StreamSubscription? _errorSubscription;

  SyncService(this._stateProvider)
      : _webSocketService = SyncWebSocketService(),
        _eventHandler = SyncEventHandler(_stateProvider);

  Future<void> initialize({
    required String deviceId,
    required String role,
    required String computerRole,
    required int priority,
    String serverUrl = 'http://localhost:5000',
  }) async {
    try {
      // Set device ID in state provider
      _stateProvider.setDeviceId(deviceId);
      _stateProvider.updateRole(role);
      _stateProvider.updateStatus(SyncStatus.connecting);

      // Set up event listeners
      _setupEventListeners();

      // Connect to WebSocket
      await _webSocketService.connect(
        deviceId: deviceId,
        role: role,
        computerRole: computerRole,
        priority: priority,
        serverUrl: serverUrl,
      );

      print('✅ Sync service initialized successfully');
    } catch (e) {
      print('❌ Failed to initialize sync service: $e');
      _stateProvider.updateStatus(SyncStatus.error);
      rethrow;
    }
  }

  void _setupEventListeners() {
    // Listen for WebSocket events
    _eventSubscription = _webSocketService.events.listen(
      (eventData) {
        _eventHandler.handleEvent(eventData);
      },
      onError: (error) {
        print('❌ Event stream error: $error');
        _stateProvider.updateStatus(SyncStatus.error);
      },
    );

    // Listen for connection status changes
    _connectionStatusSubscription = _webSocketService.connectionStatus.listen(
      (isConnected) {
        if (isConnected) {
          _eventHandler.handleConnectionEstablished();
        } else {
          _eventHandler.handleConnectionLost();
        }
      },
    );

    // Listen for errors
    _errorSubscription = _webSocketService.errors.listen(
      (error) {
        print('❌ WebSocket error: $error');
        _eventHandler.handleConnectionError(error);
      },
    );
  }

  Future<void> disconnect() async {
    try {
      await _webSocketService.disconnect();
      _eventHandler.handleConnectionLost();
      print('🔌 Sync service disconnected');
    } catch (e) {
      print('❌ Error during disconnect: $e');
    }
  }

  void sendEvent(String eventType, Map<String, dynamic> payload) {
    try {
      _webSocketService.sendEvent(eventType, payload);
    } catch (e) {
      print('❌ Failed to send event: $e');
    }
  }

  void sendCriticalEvent(String eventType, Map<String, dynamic> payload) {
    final criticalPayload = {
      'event_type': eventType,
      'payload': payload,
      'device_id': _stateProvider.deviceId,
      'timestamp': DateTime.now().toIso8601String(),
    };

    sendEvent('critical_event', criticalPayload);
  }

  void sendSyncRequest(String syncType) {
    final requestPayload = {
      'requesting_device_id': _stateProvider.deviceId,
      'sync_type': syncType,
      'timestamp': DateTime.now().toIso8601String(),
    };

    sendEvent('sync_request', requestPayload);
  }

  void sendSyncResponse(
      String requestingDeviceId, String syncType, Map<String, dynamic> data) {
    final responsePayload = {
      'requesting_device_id': requestingDeviceId,
      'sync_type': syncType,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    };

    sendEvent('sync_response', responsePayload);
  }

  // Utility methods for common operations
  void updateStock(int productId, int quantity, String action) {
    final payload = {
      'product_id': productId,
      'quantity': quantity,
      'action': action, // 'add', 'remove', 'set'
    };

    sendCriticalEvent('stock_update', payload);
  }

  void updatePrice(int productId, double oldPrice, double newPrice) {
    final payload = {
      'product_id': productId,
      'old_price': oldPrice,
      'new_price': newPrice,
    };

    sendCriticalEvent('price_change', payload);
  }

  void sendInventoryAlert(int productId, String alertType, String message) {
    final payload = {
      'product_id': productId,
      'alert_type': alertType, // 'low_stock', 'out_of_stock', 'expiring'
      'message': message,
    };

    sendCriticalEvent('inventory_alert', payload);
  }

  void sendSystemMaintenance(
      String maintenanceType, DateTime scheduledTime, Duration duration) {
    final payload = {
      'maintenance_type': maintenanceType,
      'scheduled_time': scheduledTime.toIso8601String(),
      'duration': duration.inMinutes,
    };

    sendCriticalEvent('system_maintenance', payload);
  }

  // Get sync statistics
  Map<String, dynamic> getSyncStatistics() {
    return {
      'is_connected': _stateProvider.isConnected,
      'is_master': _stateProvider.isMaster,
      'current_role': _stateProvider.currentRole,
      'master_device': _stateProvider.masterDeviceId,
      'last_sync': _stateProvider.lastSync?.toIso8601String(),
      'pending_operations': _stateProvider.pendingOperations,
      'total_events': _stateProvider.eventHistory.length,
      'recent_events': _stateProvider.recentEvents.length,
    };
  }

  // Get events by type
  List<SyncEvent> getEventsByType(String eventType) {
    return _stateProvider.getEventsByType(eventType);
  }

  // Clear event history
  void clearEventHistory() {
    _stateProvider.clearEventHistory();
  }

  // Dispose resources
  void dispose() {
    _eventSubscription?.cancel();
    _connectionStatusSubscription?.cancel();
    _errorSubscription?.cancel();
    _webSocketService.dispose();
    print('🧹 Sync service disposed');
  }
}
