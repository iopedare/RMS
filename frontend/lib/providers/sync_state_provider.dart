import 'dart:async';
import 'package:flutter/foundation.dart';

enum SyncStatus {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
}

class SyncEvent {
  final String eventType;
  final Map<String, dynamic> payload;
  final String deviceId;
  final String? userId;
  final DateTime timestamp;

  SyncEvent({
    required this.eventType,
    required this.payload,
    required this.deviceId,
    this.userId,
    required this.timestamp,
  });

  factory SyncEvent.fromJson(Map<String, dynamic> json) {
    return SyncEvent(
      eventType: json['event'] ?? '',
      payload: json['data'] ?? {},
      deviceId: json['data']?['device_id'] ?? '',
      userId: json['data']?['user_id'],
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class SyncStateProvider extends ChangeNotifier {
  SyncStatus _status = SyncStatus.disconnected;
  String? _masterDeviceId;
  String? _currentRole;
  String? _deviceId;
  DateTime? _lastSync;
  int _pendingOperations = 0;
  List<SyncEvent> _pendingEvents = [];
  List<SyncEvent> _eventHistory = [];

  // Getters
  SyncStatus get status => _status;
  String? get masterDeviceId => _masterDeviceId;
  String? get currentRole => _currentRole;
  String? get deviceId => _deviceId;
  DateTime? get lastSync => _lastSync;
  int get pendingOperations => _pendingOperations;
  List<SyncEvent> get pendingEvents => List.unmodifiable(_pendingEvents);
  List<SyncEvent> get eventHistory => List.unmodifiable(_eventHistory);

  // Methods
  void updateStatus(SyncStatus status) {
    if (_status != status) {
      _status = status;
      notifyListeners();
      print('🔄 Sync status updated: $status');
    }
  }

  void setMasterDevice(String deviceId) {
    if (_masterDeviceId != deviceId) {
      _masterDeviceId = deviceId;
      notifyListeners();
      print('👑 Master device set: $deviceId');
    }
  }

  void updateRole(String role) {
    if (_currentRole != role) {
      _currentRole = role;
      notifyListeners();
      print('🎭 Role updated: $role');
    }
  }

  void setDeviceId(String deviceId) {
    _deviceId = deviceId;
    notifyListeners();
  }

  void updateLastSync(DateTime timestamp) {
    _lastSync = timestamp;
    notifyListeners();
  }

  void setPendingOperations(int count) {
    if (_pendingOperations != count) {
      _pendingOperations = count;
      notifyListeners();
    }
  }

  void addPendingEvent(SyncEvent event) {
    _pendingEvents.add(event);
    _pendingOperations = _pendingEvents.length;
    notifyListeners();
    print('📋 Added pending event: ${event.eventType}');
  }

  void removePendingEvent(SyncEvent event) {
    _pendingEvents.removeWhere((e) =>
        e.eventType == event.eventType && e.timestamp == event.timestamp);
    _pendingOperations = _pendingEvents.length;
    notifyListeners();
  }

  void clearPendingEvents() {
    _pendingEvents.clear();
    _pendingOperations = 0;
    notifyListeners();
    print('🧹 Cleared pending events');
  }

  void addEventToHistory(SyncEvent event) {
    _eventHistory.add(event);
    // Keep only last 100 events
    if (_eventHistory.length > 100) {
      _eventHistory.removeAt(0);
    }
    notifyListeners();
  }

  void clearEventHistory() {
    _eventHistory.clear();
    notifyListeners();
  }

  // Helper methods
  bool get isConnected => _status == SyncStatus.connected;
  bool get isConnecting => _status == SyncStatus.connecting;
  bool get isReconnecting => _status == SyncStatus.reconnecting;
  bool get isDisconnected => _status == SyncStatus.disconnected;
  bool get hasError => _status == SyncStatus.error;
  bool get isMaster =>
      _masterDeviceId != null &&
      _deviceId != null &&
      _masterDeviceId == _deviceId;

  // Get events by type
  List<SyncEvent> getEventsByType(String eventType) {
    return _eventHistory
        .where((event) => event.eventType == eventType)
        .toList();
  }

  // Get recent events (last 10)
  List<SyncEvent> get recentEvents {
    final recent = _eventHistory.take(10).toList();
    recent.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return recent;
  }

  // Reset state
  void reset() {
    _status = SyncStatus.disconnected;
    _masterDeviceId = null;
    _currentRole = null;
    _deviceId = null;
    _lastSync = null;
    _pendingOperations = 0;
    _pendingEvents.clear();
    _eventHistory.clear();
    notifyListeners();
    print('🔄 Sync state reset');
  }
}
