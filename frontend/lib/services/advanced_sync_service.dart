import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'sync_api_service.dart';
import 'sync_socket_service.dart';

class AdvancedSyncService {
  final SyncApiService apiService;
  final SyncSocketService socketService;
  
  // State management
  String? _deviceId;
  String _currentRole = 'client';
  String _syncStatus = 'disconnected';
  int _pendingChanges = 0;
  DateTime? _lastSync;
  String? _errorMessage;
  
  // Callbacks for UI updates
  Function(String)? onRoleChanged;
  Function(String)? onSyncStatusChanged;
  Function(int)? onPendingChangesChanged;
  Function(String)? onError;
  Function(String)? onMasterElection;
  
  // Timers for periodic operations
  Timer? _statusCheckTimer;
  Timer? _healthCheckTimer;
  Timer? _syncTimer;
  
  // Configuration
  static const Duration statusCheckInterval = Duration(seconds: 30);
  static const Duration healthCheckInterval = Duration(minutes: 2);
  static const Duration syncInterval = Duration(minutes: 5);
  
  AdvancedSyncService(this.apiService, this.socketService) {
    _setupSocketCallbacks();
  }
  
  // Getters for current state
  String? get deviceId => _deviceId;
  String get currentRole => _currentRole;
  String get syncStatus => _syncStatus;
  int get pendingChanges => _pendingChanges;
  DateTime? get lastSync => _lastSync;
  String? get errorMessage => _errorMessage;
  
  // Initialize the service
  Future<void> initialize() async {
    await _loadDeviceInfo();
    await _startPeriodicTasks();
  }
  
  // Connect to backend
  Future<void> connect(String wsUrl) async {
    if (_deviceId == null) {
      throw Exception('Device ID not initialized');
    }
    
    try {
      // Register device via REST API first
      final response = await apiService.registerDevice(_deviceId!, _currentRole);
      if (!apiService.isSuccessResponse(response)) {
        throw Exception('Failed to register device: ${apiService.getErrorMessage(response)}');
      }
      
      // Connect WebSocket
      socketService.connect(wsUrl, _deviceId!, _currentRole);
      
      // Emit device online event
      socketService.emitDeviceOnline();
      
      _updateSyncStatus('connecting');
      
    } catch (e) {
      _handleError('Connection failed: $e');
      rethrow;
    }
  }
  
  // Disconnect from backend
  Future<void> disconnect() async {
    _stopPeriodicTasks();
    
    // Emit device offline event
    socketService.emitDeviceOffline();
    
    // Disconnect socket
    socketService.disconnect();
    
    _updateSyncStatus('disconnected');
  }
  
  // Handle app shutdown
  Future<void> shutdown() async {
    // Emit device shutdown event
    socketService.emitDeviceShutdown();
    
    await disconnect();
  }
  
  // Manual sync operations
  Future<void> triggerSync({String? targetDevice, String syncType = 'full'}) async {
    if (!socketService.isConnected) {
      throw Exception('Not connected to backend');
    }
    
    try {
      _updateSyncStatus('syncing');
      
      if (targetDevice != null) {
        // Sync with specific device
        socketService.emitSyncRequest(targetDevice, syncType);
      } else {
        // Sync with master device
        final masterResponse = await apiService.getMasterDevice();
        if (apiService.isSuccessResponse(masterResponse)) {
          final masterData = apiService.parseJsonResponse(masterResponse);
          if (masterData != null && masterData['device_id'] != _deviceId) {
            socketService.emitSyncRequest(masterData['device_id'], syncType);
          }
        }
      }
      
    } catch (e) {
      _handleError('Sync failed: $e');
      rethrow;
    }
  }
  
  // Manual master election trigger
  Future<void> triggerMasterElection(String reason) async {
    try {
      final response = await apiService.triggerMasterElection(reason);
      if (!apiService.isSuccessResponse(response)) {
        throw Exception('Failed to trigger master election: ${apiService.getErrorMessage(response)}');
      }
    } catch (e) {
      _handleError('Master election failed: $e');
      rethrow;
    }
  }
  
  // Get system information
  Future<Map<String, dynamic>?> getSystemInfo() async {
    try {
      final healthResponse = await apiService.getSystemHealth();
      final networkResponse = await apiService.getNetworkStatus();
      final activeDevicesResponse = await apiService.getActiveDevices();
      
      return {
        'health': apiService.isSuccessResponse(healthResponse) 
            ? apiService.parseJsonResponse(healthResponse) 
            : null,
        'network': apiService.isSuccessResponse(networkResponse) 
            ? apiService.parseJsonResponse(networkResponse) 
            : null,
        'active_devices': apiService.isSuccessResponse(activeDevicesResponse) 
            ? apiService.parseJsonResponse(activeDevicesResponse) 
            : null,
      };
    } catch (e) {
      _handleError('Failed to get system info: $e');
      return null;
    }
  }
  
  // Get sync audit logs
  Future<List<Map<String, dynamic>>?> getAuditLogs({
    String? eventType,
    int? limit,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final response = await apiService.getSyncAuditLogs(
        deviceId: _deviceId,
        eventType: eventType,
        limit: limit,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (apiService.isSuccessResponse(response)) {
        final data = apiService.parseJsonResponse(response);
        return data?['logs'] as List<Map<String, dynamic>>?;
      }
      
      return null;
    } catch (e) {
      _handleError('Failed to get audit logs: $e');
      return null;
    }
  }
  
  // Get master election logs
  Future<List<Map<String, dynamic>>?> getMasterElectionLogs({int? limit}) async {
    try {
      final response = await apiService.getMasterElectionLogs(limit: limit);
      
      if (apiService.isSuccessResponse(response)) {
        final data = apiService.parseJsonResponse(response);
        return data?['logs'] as List<Map<String, dynamic>>?;
      }
      
      return null;
    } catch (e) {
      _handleError('Failed to get master election logs: $e');
      return null;
    }
  }
  
  // Resolve sync conflicts
  Future<bool> resolveConflict(String conflictId, Map<String, dynamic> resolution) async {
    try {
      final response = await apiService.resolveSyncConflict(_deviceId!, conflictId, resolution);
      return apiService.isSuccessResponse(response);
    } catch (e) {
      _handleError('Failed to resolve conflict: $e');
      return false;
    }
  }
  
  // Report errors
  Future<void> reportError(String errorType, String errorMessage, Map<String, dynamic>? details) async {
    try {
      await apiService.reportError(_deviceId!, errorType, errorMessage, details);
    } catch (e) {
      print('Failed to report error: $e');
    }
  }
  
  // Private methods
  Future<void> _loadDeviceInfo() async {
    final prefs = await SharedPreferences.getInstance();
    _deviceId = prefs.getString('device_id');
    _currentRole = prefs.getString('current_role') ?? 'client';
    
    if (_deviceId == null) {
      _deviceId = DateTime.now().millisecondsSinceEpoch.toString();
      await prefs.setString('device_id', _deviceId!);
    }
  }
  
  void _setupSocketCallbacks() {
    socketService.onRoleChange = _handleRoleChange;
    socketService.onMasterElection = _handleMasterElection;
    socketService.onSyncStatus = _handleSyncStatusUpdate;
    socketService.onSyncConflict = _handleSyncConflict;
    socketService.onSyncError = _handleSyncError;
  }
  
  void _handleRoleChange(String deviceId, String newRole, String reason) {
    if (deviceId == _deviceId) {
      _currentRole = newRole;
      _saveRoleToPrefs();
      
      if (onRoleChanged != null) {
        onRoleChanged!(newRole);
      }
      
      print('Role changed to: $newRole (reason: $reason)');
    }
  }
  
  void _handleMasterElection(String newMasterId, String reason) {
    if (onMasterElection != null) {
      onMasterElection!(newMasterId);
    }
    
    print('Master election: $newMasterId elected (reason: $reason)');
  }
  
  void _handleSyncStatusUpdate(String deviceId, String status, Map<String, dynamic> details) {
    if (deviceId == _deviceId) {
      _syncStatus = status;
      _pendingChanges = details['pendingChanges'] ?? 0;
      _lastSync = details['lastSync'] != null 
          ? DateTime.tryParse(details['lastSync']) 
          : null;
      _errorMessage = details['errorMessage'];
      
      if (onSyncStatusChanged != null) {
        onSyncStatusChanged!(status);
      }
      
      if (onPendingChangesChanged != null) {
        onPendingChangesChanged!(_pendingChanges);
      }
    }
  }
  
  void _handleSyncConflict(String deviceId, Map<String, dynamic> conflictData) {
    if (deviceId == _deviceId) {
      _handleError('Sync conflict detected: ${conflictData['conflict_type']}');
    }
  }
  
  void _handleSyncError(String deviceId, String error, Map<String, dynamic> details) {
    if (deviceId == _deviceId) {
      _handleError('Sync error: $error');
    }
  }
  
  void _updateSyncStatus(String status) {
    _syncStatus = status;
    if (onSyncStatusChanged != null) {
      onSyncStatusChanged!(status);
    }
  }
  
  void _handleError(String error) {
    _errorMessage = error;
    if (onError != null) {
      onError!(error);
    }
    print('AdvancedSyncService Error: $error');
  }
  
  Future<void> _saveRoleToPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('current_role', _currentRole);
  }
  
  Future<void> _startPeriodicTasks() async {
    // Status check timer
    _statusCheckTimer = Timer.periodic(statusCheckInterval, (_) {
      _checkSyncStatus();
    });
    
    // Health check timer
    _healthCheckTimer = Timer.periodic(healthCheckInterval, (_) {
      _checkSystemHealth();
    });
    
    // Sync timer
    _syncTimer = Timer.periodic(syncInterval, (_) {
      if (socketService.isConnected && _currentRole == 'client') {
        triggerSync();
      }
    });
  }
  
  void _stopPeriodicTasks() {
    _statusCheckTimer?.cancel();
    _healthCheckTimer?.cancel();
    _syncTimer?.cancel();
  }
  
  Future<void> _checkSyncStatus() async {
    if (!socketService.isConnected) return;
    
    try {
      final response = await apiService.getSyncState(_deviceId!);
      if (apiService.isSuccessResponse(response)) {
        final data = apiService.parseJsonResponse(response);
        if (data != null) {
          _handleSyncStatusUpdate(_deviceId!, data['sync_status'], data);
        }
      }
    } catch (e) {
      print('Status check failed: $e');
    }
  }
  
  Future<void> _checkSystemHealth() async {
    if (!socketService.isConnected) return;
    
    try {
      final response = await apiService.getSystemHealth();
      if (!apiService.isSuccessResponse(response)) {
        _handleError('System health check failed');
      }
    } catch (e) {
      print('Health check failed: $e');
    }
  }
  
  // Dispose resources
  void dispose() {
    _stopPeriodicTasks();
    socketService.removeAllListeners();
  }
} 