import 'package:flutter/material.dart';
import 'package:retail_management_system_frontend/services/sync_api_service.dart';
import 'package:retail_management_system_frontend/services/sync_socket_service.dart';
import 'package:retail_management_system_frontend/widgets/sync_status_bar.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:async';

bool testMode = false;

void main() {
  runApp(const RetailManagementApp());
}

class RetailManagementApp extends StatelessWidget {
  const RetailManagementApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Retail Management System',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const SyncHomePage(),
    );
  }
}

class SyncHomePage extends StatefulWidget {
  const SyncHomePage({super.key});

  @override
  State<SyncHomePage> createState() => _SyncHomePageState();
}

class _SyncHomePageState extends State<SyncHomePage> {
  final SyncApiService apiService = SyncApiService(
      testMode ? 'http://localhost:5999' : 'http://localhost:5000');
  final SyncSocketService socketService = SyncSocketService();

  String status = 'Disconnected';
  String deviceId = '';
  String role = 'client';
  DateTime? lastSync;
  int pendingChanges = 0;
  StreamSubscription? _statusSub;

  @override
  void initState() {
    super.initState();
    _initDeviceAndConnect();
  }

  Future<void> _initDeviceAndConnect() async {
    // Generate or retrieve device ID
    final prefs = await SharedPreferences.getInstance();
    deviceId = prefs.getString('device_id') ?? UniqueKey().toString();
    await prefs.setString('device_id', deviceId);

    // Register device with backend via REST API before connecting WebSocket
    if (!mounted) return;
    setState(() {
      status = 'Registering...';
      print(status);
    });
    try {
      final resp = await apiService.registerDevice(deviceId, role);
      if (resp.statusCode == 200) {
        setState(() {
          status = 'Registered (REST)';
          print(status);
        });
      } else {
        setState(() {
          status = 'Registration failed (${resp.statusCode})';
          print(status);
        });
        // Optionally, show error and retry UI
        if (testMode) {
          setState(() {
            status = 'Disconnected';
            print(status);
          });
        }
        return;
      }
    } catch (e) {
      setState(() {
        status = 'Registration error';
        print(status);
      });
      // Optionally, show error and retry UI
      if (testMode) {
        setState(() {
          status = 'Disconnected';
          print(status);
        });
      }
      return;
    }

    if (testMode) {
      setState(() {
        status = 'Disconnected';
        print(status);
      });
      return;
    }

    // Only connect WebSocket if not in testMode (simulate disconnect in test)
    if (!testMode) {
      socketService.connect('http://localhost:5000', deviceId, role);
      if (!mounted) return;
      setState(() {
        status = 'Connecting...';
        print(status);
      });
      // Listen for connection and registration events
      socketService.socket?.on('connect', (_) {
        if (!mounted) return;
        setState(() {
          status = 'Connected';
          print(status);
        });
      });
      socketService.socket?.on('registered', (data) {
        if (!mounted) return;
        setState(() {
          status = 'Registered (WebSocket)';
          print(status);
        });
      });
      socketService.socket?.on('disconnect', (_) {
        if (!mounted) return;
        setState(() {
          status = 'Disconnected';
          print(status);
        });
      });
      socketService.socket?.on('critical_event', (data) {
        if (!mounted) return;
        setState(() {
          lastSync = DateTime.now();
          print(status);
        });
        // Optionally show a snackbar or notification
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Received critical event: $data')),
        );
        // Acknowledge event
        socketService.acknowledge(data['event_type'] ?? 'unknown', deviceId);
      });
    }
    // Optionally, poll sync status
    _statusSub = Stream.periodic(const Duration(seconds: 10)).listen((_) async {
      final resp = await apiService.getSyncStatus();
      if (resp.statusCode == 200) {
        final data = resp.body;
        if (!mounted) return;
        setState(() {
          // Parse pending events from response if available
          pendingChanges =
              int.tryParse(RegExp(r'\d+').stringMatch(data) ?? '0') ?? 0;
          print(status);
        });
      }
    });
  }

  @override
  void dispose() {
    _statusSub?.cancel();
    socketService.removeAllListeners();
    socketService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Retail Management System')),
      body: Column(
        children: [
          // Enhanced SyncStatusBar with retry button
          SyncStatusBar(
            status: status,
            deviceId: deviceId,
            role: role,
            lastSync: lastSync,
            pendingChanges: pendingChanges,
            onRetry: (status.toLowerCase().contains('error') ||
                    status.toLowerCase().contains('disconnected') ||
                    status.toLowerCase().contains('failed'))
                ? () {
                    // Retry logic: re-init device registration and connection
                    _initDeviceAndConnect();
                  }
                : null,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () async {
              // Example: Push a test sync event
              final resp = await apiService.pushSyncEvent({
                'event_type': 'test_event',
                'payload': {'message': 'Hello from frontend'},
                'device_id': deviceId,
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Push response:  ${resp.statusCode}')),
              );
            },
            child: const Text('Push Test Sync Event'),
          ),
        ],
      ),
    );
  }
}
