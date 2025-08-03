import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/sync_state_provider.dart';

class SyncStatusBar extends StatelessWidget {
  const SyncStatusBar({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<SyncStateProvider>(
      builder: (context, syncState, child) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: _getStatusColor(syncState.status),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildStatusIcon(syncState.status),
              const SizedBox(width: 8),
              _buildStatusText(syncState),
              if (syncState.pendingOperations > 0) ...[
                const SizedBox(width: 8),
                _buildPendingIndicator(syncState.pendingOperations),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatusIcon(SyncStatus status) {
    IconData iconData;
    Color iconColor = Colors.white;

    switch (status) {
      case SyncStatus.connected:
        iconData = Icons.check_circle;
        break;
      case SyncStatus.connecting:
        iconData = Icons.hourglass_empty;
        break;
      case SyncStatus.reconnecting:
        iconData = Icons.refresh;
        break;
      case SyncStatus.disconnected:
        iconData = Icons.cancel;
        break;
      case SyncStatus.error:
        iconData = Icons.error;
        break;
    }

    return Icon(
      iconData,
      color: iconColor,
      size: 16,
    );
  }

  Widget _buildStatusText(SyncStateProvider syncState) {
    String statusText;

    switch (syncState.status) {
      case SyncStatus.connected:
        statusText = 'Connected';
        break;
      case SyncStatus.connecting:
        statusText = 'Connecting...';
        break;
      case SyncStatus.reconnecting:
        statusText = 'Reconnecting...';
        break;
      case SyncStatus.disconnected:
        statusText = 'Disconnected';
        break;
      case SyncStatus.error:
        statusText = 'Error';
        break;
    }

    return Text(
      statusText,
      style: const TextStyle(
        color: Colors.white,
        fontSize: 12,
        fontWeight: FontWeight.w500,
      ),
    );
  }

  Widget _buildPendingIndicator(int pendingCount) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        '$pendingCount',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getStatusColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.connected:
        return const Color(0xFF4CAF50); // Green
      case SyncStatus.connecting:
        return const Color(0xFFFF9800); // Orange
      case SyncStatus.reconnecting:
        return const Color(0xFFFF9800); // Orange
      case SyncStatus.disconnected:
        return const Color(0xFFF44336); // Red
      case SyncStatus.error:
        return const Color(0xFFD32F2F); // Dark Red
    }
  }
}

class DeviceInfoPanel extends StatelessWidget {
  const DeviceInfoPanel({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<SyncStateProvider>(
      builder: (context, syncState, child) {
        return Card(
          margin: const EdgeInsets.all(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.devices,
                      color: Theme.of(context).primaryColor,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Device Information',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildInfoRow('Device ID', syncState.deviceId ?? 'Not set'),
                _buildInfoRow('Role', _formatRole(syncState.currentRole)),
                _buildInfoRow('Status', _formatStatus(syncState.status)),
                if (syncState.masterDeviceId != null) ...[
                  _buildInfoRow('Master Device', syncState.masterDeviceId!),
                ],
                if (syncState.lastSync != null) ...[
                  _buildInfoRow(
                      'Last Sync', _formatDateTime(syncState.lastSync!)),
                ],
                _buildInfoRow(
                    'Pending Operations', '${syncState.pendingOperations}'),
                if (syncState.isMaster) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFD700),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.star, size: 16, color: Colors.black87),
                        SizedBox(width: 4),
                        Text(
                          'MASTER DEVICE',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 12,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatRole(String? role) {
    if (role == null) return 'Unknown';

    switch (role) {
      case 'admin':
        return 'Administrator';
      case 'manager':
        return 'Manager';
      case 'assistant_manager':
        return 'Assistant Manager';
      case 'sales_assistant':
        return 'Sales Assistant';
      case 'master':
        return 'Master';
      case 'client':
        return 'Client';
      default:
        return role;
    }
  }

  String _formatStatus(SyncStatus status) {
    switch (status) {
      case SyncStatus.connected:
        return 'Connected';
      case SyncStatus.connecting:
        return 'Connecting';
      case SyncStatus.reconnecting:
        return 'Reconnecting';
      case SyncStatus.disconnected:
        return 'Disconnected';
      case SyncStatus.error:
        return 'Error';
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}
