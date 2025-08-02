import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/sync_state_provider.dart';
import '../services/sync_service.dart';
import '../widgets/sync_status_bar.dart';

class SyncTestPage extends StatefulWidget {
  const SyncTestPage({Key? key}) : super(key: key);

  @override
  State<SyncTestPage> createState() => _SyncTestPageState();
}

class _SyncTestPageState extends State<SyncTestPage> {
  SyncService? _syncService;
  final TextEditingController _deviceIdController = TextEditingController();
  final TextEditingController _roleController = TextEditingController();
  final TextEditingController _priorityController = TextEditingController();

  String _selectedRole = 'sales_assistant';
  String _selectedComputerRole = 'client';
  int _selectedPriority = 50;

  @override
  void initState() {
    super.initState();
    _deviceIdController.text =
        'device_${DateTime.now().millisecondsSinceEpoch}';
    _roleController.text = _selectedRole;
    _priorityController.text = _selectedPriority.toString();
  }

  @override
  void dispose() {
    _syncService?.dispose();
    _deviceIdController.dispose();
    _roleController.dispose();
    _priorityController.dispose();
    super.dispose();
  }

  Future<void> _initializeSync() async {
    try {
      final syncState = Provider.of<SyncStateProvider>(context, listen: false);
      _syncService = SyncService(syncState);

             await _syncService!.initialize(
         deviceId: _deviceIdController.text,
         role: _selectedRole,
         computerRole: _selectedComputerRole,
         priority: _selectedPriority,
       );

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Sync service initialized successfully'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Failed to initialize sync: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _disconnectSync() async {
    try {
      await _syncService?.disconnect();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('🔌 Sync service disconnected'),
          backgroundColor: Colors.orange,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error disconnecting: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _sendTestEvent() {
    if (_syncService == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ Please initialize sync service first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    _syncService!.sendCriticalEvent('test_event', {
      'message': 'Hello from Flutter!',
      'timestamp': DateTime.now().toIso8601String(),
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📤 Test event sent'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  void _updateStock() {
    if (_syncService == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ Please initialize sync service first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    _syncService!.updateStock(1, 10, 'add');
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📦 Stock update sent'),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sync Test Page'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
        actions: [
          const SyncStatusBar(),
          const SizedBox(width: 16),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Device Information Panel
              const DeviceInfoPanel(),

              const SizedBox(height: 24),

              // Connection Controls
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Connection Settings',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 16),

                      // Device ID
                      TextField(
                        controller: _deviceIdController,
                        decoration: const InputDecoration(
                          labelText: 'Device ID',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Role Selection
                      DropdownButtonFormField<String>(
                        value: _selectedRole,
                        decoration: const InputDecoration(
                          labelText: 'User Role',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(
                              value: 'admin', child: Text('Administrator')),
                          DropdownMenuItem(
                              value: 'manager', child: Text('Manager')),
                          DropdownMenuItem(
                              value: 'assistant_manager',
                              child: Text('Assistant Manager')),
                          DropdownMenuItem(
                              value: 'inventory_assistant',
                              child: Text('Inventory Assistant')),
                          DropdownMenuItem(
                              value: 'sales_assistant',
                              child: Text('Sales Assistant')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedRole = value!;
                          });
                        },
                      ),
                      const SizedBox(height: 16),

                      // Computer Role Selection
                      DropdownButtonFormField<String>(
                        value: _selectedComputerRole,
                        decoration: const InputDecoration(
                          labelText: 'Computer Role',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(
                              value: 'master', child: Text('Master')),
                          DropdownMenuItem(
                              value: 'client', child: Text('Client')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedComputerRole = value!;
                          });
                        },
                      ),
                      const SizedBox(height: 16),

                      // Priority Selection
                      DropdownButtonFormField<int>(
                        value: _selectedPriority,
                        decoration: const InputDecoration(
                          labelText: 'Priority',
                          border: OutlineInputBorder(),
                        ),
                        items: [
                          for (int i = 0; i <= 100; i += 10)
                            DropdownMenuItem(value: i, child: Text('$i')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedPriority = value!;
                          });
                        },
                      ),
                      const SizedBox(height: 24),

                      // Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _initializeSync,
                              icon: const Icon(Icons.power_settings_new),
                              label: const Text('Connect'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _disconnectSync,
                              icon: const Icon(Icons.power_off),
                              label: const Text('Disconnect'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.red,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Test Actions
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Test Actions',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _sendTestEvent,
                              icon: const Icon(Icons.send),
                              label: const Text('Send Test Event'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _updateStock,
                              icon: const Icon(Icons.inventory),
                              label: const Text('Update Stock'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.orange,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Event History
              SizedBox(
                height: 300, // Fixed height for event history
                child: Consumer<SyncStateProvider>(
                  builder: (context, syncState, child) {
                    return Card(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.history,
                                  color: Theme.of(context).primaryColor,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Event History (${syncState.eventHistory.length})',
                                  style:
                                      Theme.of(context).textTheme.titleMedium,
                                ),
                                const Spacer(),
                                TextButton.icon(
                                  onPressed: syncState.clearEventHistory,
                                  icon: const Icon(Icons.clear),
                                  label: const Text('Clear'),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: syncState.recentEvents.length,
                              itemBuilder: (context, index) {
                                final event = syncState.recentEvents[index];
                                return Card(
                                  margin: const EdgeInsets.only(bottom: 8),
                                  child: ListTile(
                                    leading: Icon(
                                      _getEventIcon(event.eventType),
                                      color: _getEventColor(event.eventType),
                                    ),
                                    title: Text(
                                      event.eventType,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                    ),
                                    subtitle: Text(
                                      '${event.deviceId} - ${_formatDateTime(event.timestamp)}',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    trailing: Text(
                                      '${event.payload.length} fields',
                                      style: const TextStyle(
                                          fontSize: 10, color: Colors.grey),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getEventIcon(String eventType) {
    switch (eventType) {
      case 'device_online':
        return Icons.check_circle;
      case 'device_offline':
        return Icons.cancel;
      case 'master_election':
        return Icons.star;
      case 'critical_event':
        return Icons.warning;
      case 'sync_request':
        return Icons.sync;
      case 'sync_response':
        return Icons.sync_alt;
      case 'role_change':
        return Icons.swap_horiz;
      case 'error':
        return Icons.error;
      default:
        return Icons.info;
    }
  }

  Color _getEventColor(String eventType) {
    switch (eventType) {
      case 'device_online':
        return Colors.green;
      case 'device_offline':
        return Colors.red;
      case 'master_election':
        return Colors.amber;
      case 'critical_event':
        return Colors.orange;
      case 'sync_request':
        return Colors.blue;
      case 'sync_response':
        return Colors.blue;
      case 'role_change':
        return Colors.purple;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}:${dateTime.second.toString().padLeft(2, '0')}';
  }
}
