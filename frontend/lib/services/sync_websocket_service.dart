import 'dart:convert';
import 'dart:async';
import 'package:socket_io_client/socket_io_client.dart' as IO;

class SyncWebSocketService {
  IO.Socket? _socket;
  String? _deviceId;
  String? _role;
  String? _computerRole;
  int? _priority;
  bool _isConnected = false;
  bool _isReconnecting = false;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;

  // Controllers for state management
  final StreamController<bool> _connectionStatusController =
      StreamController<bool>.broadcast();
  final StreamController<Map<String, dynamic>> _eventController =
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<String> _errorController =
      StreamController<String>.broadcast();

  // Getters
  Stream<bool> get connectionStatus => _connectionStatusController.stream;
  Stream<Map<String, dynamic>> get events => _eventController.stream;
  Stream<String> get errors => _errorController.stream;
  bool get isConnected => _isConnected;

  Future<void> connect({
    required String deviceId,
    required String role,
    required String computerRole,
    required int priority,
    String serverUrl = 'http://localhost:5000',
  }) async {
    try {
      _deviceId = deviceId;
      _role = role;
      _computerRole = computerRole;
      _priority = priority;

      // Create SocketIO connection
      _socket = IO.io(serverUrl, <String, dynamic>{
        'transports': ['websocket'],
        'autoConnect': true,
        'reconnection': true,
        'reconnectionAttempts': _maxReconnectAttempts,
        'reconnectionDelay': 1000,
      });

      // Set up event listeners
      _socket!.onConnect((_) {
        print('✅ SocketIO connected successfully');
        _isConnected = true;
        _isReconnecting = false;
        _reconnectAttempts = 0;
        _connectionStatusController.add(true);
        _registerDevice();
      });

      _socket!.onDisconnect((_) {
        print('🔌 SocketIO disconnected');
        _isConnected = false;
        _connectionStatusController.add(false);
      });

      _socket!.onError((error) {
        print('❌ SocketIO error: $error');
        _errorController.add(error.toString());
        _isConnected = false;
        _connectionStatusController.add(false);
      });

      // Listen for server events
      _socket!.on('connected', (data) {
        print('📥 Received connected event: $data');
        _eventController.add({'event': 'connected', 'data': data});
      });

      _socket!.on('device_online_ack', (data) {
        print('📥 Received device_online_ack: $data');
        _eventController.add({'event': 'device_online_ack', 'data': data});
      });

      _socket!.on('device_offline_ack', (data) {
        print('📥 Received device_offline_ack: $data');
        _eventController.add({'event': 'device_offline_ack', 'data': data});
      });

      _socket!.on('role_change', (data) {
        print('📥 Received role_change: $data');
        _eventController.add({'event': 'role_change', 'data': data});
      });

      _socket!.on('sync_response', (data) {
        print('📥 Received sync_response: $data');
        _eventController.add({'event': 'sync_response', 'data': data});
      });

      _socket!.on('error', (data) {
        print('📥 Received error: $data');
        _eventController.add({'event': 'error', 'data': data});
      });

      // Connect to server
      _socket!.connect();
    } catch (e) {
      _handleError('Connection failed: $e');
      await _attemptReconnection();
    }
  }

  Future<void> disconnect() async {
    try {
      _socket?.disconnect();
      _isConnected = false;
      _isReconnecting = false;
      _connectionStatusController.add(false);
      print('🔌 SocketIO disconnected');
    } catch (e) {
      print('Error during disconnect: $e');
    }
  }

  void sendEvent(String event, Map<String, dynamic> data) {
    if (!_isConnected) {
      _errorController.add('Cannot send event: not connected');
      return;
    }

    try {
      final message = {
        ...data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      _socket?.emit(event, message);
      print('📤 Sent event: $event');
    } catch (e) {
      _errorController.add('Failed to send event: $e');
    }
  }

  Future<void> _registerDevice() async {
    final registrationData = {
      'device_id': _deviceId,
      'role': _role,
      'computer_role': _computerRole,
      'priority': _priority,
    };

    sendEvent('register_device', registrationData);
  }

  void _handleError(String error) {
    print('❌ SocketIO error: $error');
    _errorController.add(error);
    _isConnected = false;
    _connectionStatusController.add(false);
  }

  Future<void> _attemptReconnection() async {
    if (_isReconnecting || _reconnectAttempts >= _maxReconnectAttempts) {
      return;
    }

    _isReconnecting = true;
    _reconnectAttempts++;

    print(
        '🔄 Attempting reconnection (${_reconnectAttempts}/$_maxReconnectAttempts)');

    await Future.delayed(Duration(seconds: _reconnectAttempts * 2));

    if (_reconnectAttempts < _maxReconnectAttempts) {
      await connect(
        deviceId: _deviceId!,
        role: _role!,
        computerRole: _computerRole!,
        priority: _priority!,
      );
    } else {
      print('❌ Max reconnection attempts reached');
      _isReconnecting = false;
    }
  }

  void dispose() {
    _socket?.disconnect();
    _socket?.dispose();
    _connectionStatusController.close();
    _eventController.close();
    _errorController.close();
  }
}
