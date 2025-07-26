import 'package:flutter/material.dart';

class SyncStatusBar extends StatelessWidget {
  final String status;
  final String deviceId;
  final String role;
  final DateTime? lastSync;
  final int pendingChanges;
  final VoidCallback? onRetry; // Optional retry callback

  const SyncStatusBar({
    required this.status,
    required this.deviceId,
    required this.role,
    this.lastSync,
    this.pendingChanges = 0,
    this.onRetry,
    super.key,
  });

  // Determine color based on status
  Color _statusColor() {
    if (status.contains('Connected') || status.contains('Registered')) {
      return Colors.green;
    } else if (status.contains('Connecting') ||
        status.contains('Registering')) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  // Determine icon based on status
  IconData _statusIcon() {
    if (status.contains('Connected') || status.contains('Registered')) {
      return Icons.check_circle;
    } else if (status.contains('Connecting') ||
        status.contains('Registering')) {
      return Icons.sync;
    } else {
      return Icons.error;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _statusColor(),
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Tooltip(
            message: 'Current sync/connection status',
            child: Row(
              children: [
                Icon(_statusIcon(), color: Colors.white),
                const SizedBox(width: 4),
                Text('Status: $status',
                    style: const TextStyle(color: Colors.white)),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Tooltip(
            message: 'Device ID and role',
            child: Text('Device: $deviceId ($role)',
                style: const TextStyle(color: Colors.white)),
          ),
          const SizedBox(width: 16),
          if (lastSync != null)
            Tooltip(
              message: 'Last successful sync time',
              child: Text('Last Sync: ${lastSync!.toLocal()}',
                  style: const TextStyle(color: Colors.white)),
            ),
          const SizedBox(width: 16),
          Tooltip(
            message: 'Number of pending sync changes/events',
            child: Text('Pending: $pendingChanges',
                style: const TextStyle(color: Colors.white)),
          ),
          // Show retry button if status is error/disconnected/failed and retry callback is provided
          if ((status.toLowerCase().contains('error') ||
                  status.toLowerCase().contains('disconnected') ||
                  status.toLowerCase().contains('failed')) &&
              onRetry != null)
            Padding(
              padding: const EdgeInsets.only(left: 16),
              child: Tooltip(
                message: 'Retry connection/registration',
                child: IconButton(
                  icon: const Icon(Icons.refresh, color: Colors.white),
                  onPressed: onRetry,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
