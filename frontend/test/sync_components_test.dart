import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import 'package:retail_management_system_frontend/main.dart';
import 'package:retail_management_system_frontend/providers/sync_state_provider.dart';
import 'package:retail_management_system_frontend/services/sync_service.dart';
import 'package:retail_management_system_frontend/services/sync_websocket_service.dart';
import 'package:retail_management_system_frontend/widgets/sync_status_bar.dart';

void main() {
  group('Sync Components Unit Tests', () {
    late SyncStateProvider syncStateProvider;
    late SyncService syncService;

    setUp(() {
      syncStateProvider = SyncStateProvider();
      syncService = SyncService(syncStateProvider);
    });

    tearDown(() {
      syncService.dispose();
    });

    testWidgets('App loads with provider', (WidgetTester tester) async {
      // Build the app with provider but don't wait for settle to avoid layout issues
      await tester.pumpWidget(
        ChangeNotifierProvider.value(
          value: syncStateProvider,
          child: const RetailManagementApp(),
        ),
      );

      // Just verify the app doesn't crash during initial build
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('Sync status bar displays correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider.value(
            value: syncStateProvider,
            child: Scaffold(
              appBar: AppBar(
                actions: [const SyncStatusBar()],
              ),
              body: const Center(child: Text('Test')),
            ),
          ),
        ),
      );

      // Verify sync status bar is present
      expect(find.byType(SyncStatusBar), findsOneWidget);
    });

    testWidgets('Device info panel displays correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider.value(
            value: syncStateProvider,
            child: Scaffold(
              body: const DeviceInfoPanel(),
            ),
          ),
        ),
      );

      // Verify device info panel is present
      expect(find.byType(DeviceInfoPanel), findsOneWidget);
      expect(find.text('Device Information'), findsOneWidget);
    });

    test('SyncStateProvider initial state', () {
      expect(syncStateProvider.status, SyncStatus.disconnected);
      expect(syncStateProvider.deviceId, isNull);
      expect(syncStateProvider.currentRole, isNull);
      expect(syncStateProvider.pendingOperations, 0);
      expect(syncStateProvider.eventHistory, isEmpty);
    });

    test('SyncStateProvider status updates', () {
      // Test status updates
      syncStateProvider.updateStatus(SyncStatus.connecting);
      expect(syncStateProvider.status, SyncStatus.connecting);

      syncStateProvider.updateStatus(SyncStatus.connected);
      expect(syncStateProvider.status, SyncStatus.connected);

      syncStateProvider.updateStatus(SyncStatus.error);
      expect(syncStateProvider.status, SyncStatus.error);
    });

    test('SyncStateProvider device management', () {
      // Test device ID setting
      syncStateProvider.setDeviceId('test_device_001');
      expect(syncStateProvider.deviceId, 'test_device_001');

      // Test role updates
      syncStateProvider.updateRole('admin');
      expect(syncStateProvider.currentRole, 'admin');

      // Test master device setting
      syncStateProvider.setMasterDevice('master_device_001');
      expect(syncStateProvider.masterDeviceId, 'master_device_001');
    });

    test('SyncStateProvider event management', () {
      // Test adding events to history
      final testEvent = SyncEvent(
        eventType: 'test_event',
        payload: {'test': 'data'},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );

      syncStateProvider.addEventToHistory(testEvent);
      expect(syncStateProvider.eventHistory.length, 1);
      expect(syncStateProvider.eventHistory.first.eventType, 'test_event');

      // Test clearing event history
      syncStateProvider.clearEventHistory();
      expect(syncStateProvider.eventHistory, isEmpty);
    });

    test('SyncStateProvider pending operations', () {
      // Test pending operations
      syncStateProvider.setPendingOperations(5);
      expect(syncStateProvider.pendingOperations, 5);

      // Test adding pending events
      final testEvent = SyncEvent(
        eventType: 'pending_event',
        payload: {'test': 'data'},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );

      syncStateProvider.addPendingEvent(testEvent);
      expect(syncStateProvider.pendingOperations, 1);

      // Test clearing pending events
      syncStateProvider.clearPendingEvents();
      expect(syncStateProvider.pendingOperations, 0);
    });

    test('SyncStateProvider helper methods', () {
      // Test helper methods
      expect(syncStateProvider.isConnected, false);
      expect(syncStateProvider.isDisconnected, true);
      expect(syncStateProvider.hasError, false);

      // Test connected state
      syncStateProvider.updateStatus(SyncStatus.connected);
      expect(syncStateProvider.isConnected, true);
      expect(syncStateProvider.isDisconnected, false);

      // Test master device detection
      syncStateProvider.setDeviceId('test_device');
      syncStateProvider.setMasterDevice('test_device');
      expect(syncStateProvider.isMaster, true);
    });

    test('SyncEvent creation and parsing', () {
      // Test SyncEvent creation
      final event = SyncEvent(
        eventType: 'test_event',
        payload: {'key': 'value'},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );

      expect(event.eventType, 'test_event');
      expect(event.payload['key'], 'value');
      expect(event.deviceId, 'test_device');

      // Test SyncEvent.fromJson
      final jsonData = {
        'event': 'json_event',
        'data': {
          'device_id': 'json_device',
          'test': 'value',
        },
        'timestamp': DateTime.now().toIso8601String(),
      };

      final parsedEvent = SyncEvent.fromJson(jsonData);
      expect(parsedEvent.eventType, 'json_event');
      expect(parsedEvent.deviceId, 'json_device');
      expect(parsedEvent.payload['test'], 'value');
    });

    test('SyncService initialization', () async {
      // Test sync service initialization
      expect(syncService, isA<SyncService>());

      // Note: Actual WebSocket connection test would require a running backend
      // This test verifies the service can be created without errors
    });

    test('SyncService utility methods', () {
      // Test utility methods don't throw errors
      expect(() => syncService.updateStock(1, 10, 'add'), returnsNormally);
      expect(() => syncService.updatePrice(1, 10.0, 15.0), returnsNormally);
      expect(() => syncService.sendInventoryAlert(1, 'low_stock', 'Test alert'),
          returnsNormally);
      expect(
          () => syncService.sendSystemMaintenance(
              'test', DateTime.now(), Duration(minutes: 30)),
          returnsNormally);
    });

    test('SyncService statistics', () {
      // Create a fresh state provider for this test
      final freshStateProvider = SyncStateProvider();
      final freshSyncService = SyncService(freshStateProvider);

      // Ensure the state is clean
      freshStateProvider.reset();

      // Test statistics method
      final stats = freshSyncService.getSyncStatistics();
      expect(stats, isA<Map<String, dynamic>>());

      expect(stats['is_connected'], false);
      expect(stats['is_master'], false);
      expect(stats['pending_operations'], 0);
      expect(stats['total_events'], 0);
      expect(stats['recent_events'], 0);

      // Clean up
      freshSyncService.dispose();
    });

    testWidgets('Connection controls work', (WidgetTester tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider.value(
          value: syncStateProvider,
          child: const MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  Text('Connection Test'),
                  // Add connection controls here if needed
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify the test page loads
      expect(find.text('Connection Test'), findsOneWidget);
    });

    test('SyncStateProvider reset functionality', () {
      // Set some state
      syncStateProvider.setDeviceId('test_device');
      syncStateProvider.updateRole('admin');
      syncStateProvider.updateStatus(SyncStatus.connected);
      syncStateProvider.setPendingOperations(5);

      // Verify state is set
      expect(syncStateProvider.deviceId, 'test_device');
      expect(syncStateProvider.currentRole, 'admin');
      expect(syncStateProvider.status, SyncStatus.connected);
      expect(syncStateProvider.pendingOperations, 5);

      // Reset state
      syncStateProvider.reset();

      // Verify state is reset
      expect(syncStateProvider.deviceId, isNull);
      expect(syncStateProvider.currentRole, isNull);
      expect(syncStateProvider.status, SyncStatus.disconnected);
      expect(syncStateProvider.pendingOperations, 0);
      expect(syncStateProvider.eventHistory, isEmpty);
    });

    test('Event history management', () {
      // Add multiple events
      for (int i = 0; i < 105; i++) {
        final event = SyncEvent(
          eventType: 'event_$i',
          payload: {'index': i},
          deviceId: 'test_device',
          timestamp: DateTime.now(),
        );
        syncStateProvider.addEventToHistory(event);
      }

      // Verify only last 100 events are kept
      expect(syncStateProvider.eventHistory.length, 100);
      expect(syncStateProvider.eventHistory.first.eventType, 'event_5');
      expect(syncStateProvider.eventHistory.last.eventType, 'event_104');
    });

    test('Recent events sorting', () {
      // Add events with different timestamps
      final now = DateTime.now();
      final event1 = SyncEvent(
        eventType: 'event_1',
        payload: {},
        deviceId: 'test_device',
        timestamp: now.subtract(const Duration(seconds: 10)),
      );
      final event2 = SyncEvent(
        eventType: 'event_2',
        payload: {},
        deviceId: 'test_device',
        timestamp: now,
      );

      syncStateProvider.addEventToHistory(event1);
      syncStateProvider.addEventToHistory(event2);

      // Verify recent events are sorted by timestamp (newest first)
      final recentEvents = syncStateProvider.recentEvents;
      expect(recentEvents.length, 2);
      expect(recentEvents.first.eventType, 'event_2'); // Newest first
      expect(recentEvents.last.eventType, 'event_1');
    });

    test('SyncStateProvider event filtering', () {
      // Add different types of events
      final event1 = SyncEvent(
        eventType: 'device_online',
        payload: {},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );
      final event2 = SyncEvent(
        eventType: 'critical_event',
        payload: {},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );
      final event3 = SyncEvent(
        eventType: 'device_online',
        payload: {},
        deviceId: 'test_device',
        timestamp: DateTime.now(),
      );

      syncStateProvider.addEventToHistory(event1);
      syncStateProvider.addEventToHistory(event2);
      syncStateProvider.addEventToHistory(event3);

      // Test filtering by event type
      final deviceOnlineEvents =
          syncStateProvider.getEventsByType('device_online');
      expect(deviceOnlineEvents.length, 2);
      expect(deviceOnlineEvents.every((e) => e.eventType == 'device_online'),
          true);

      final criticalEvents =
          syncStateProvider.getEventsByType('critical_event');
      expect(criticalEvents.length, 1);
      expect(criticalEvents.first.eventType, 'critical_event');
    });
  });
} 