import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:retail_management_system_frontend/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Integration Tests - Sync Test Page', () {
    testWidgets('App loads and displays sync test page',
        (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify the app loads and shows sync test page
      expect(find.text('Sync Test Page'), findsOneWidget);
      expect(find.text('Device ID'), findsOneWidget);
      expect(find.text('Role'), findsOneWidget);
      expect(find.text('Priority'), findsOneWidget);
    });

    testWidgets('Connection controls are present',
        (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify connection controls are present
      expect(find.text('Connect'), findsOneWidget);
      expect(find.text('Disconnect'), findsOneWidget);
      expect(find.text('Send Test Event'), findsOneWidget);
      expect(find.text('Update Stock'), findsOneWidget);
    });

    testWidgets('Device information panel displays',
        (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify device information panel is present
      expect(find.text('Device Information'), findsOneWidget);
      expect(find.text('Device ID:'), findsOneWidget);
      expect(find.text('Role:'), findsOneWidget);
      expect(find.text('Status:'), findsOneWidget);
    });

    testWidgets('Event history section is present',
        (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify event history section is present
      expect(find.text('Event History'), findsOneWidget);
      expect(find.text('Clear History'), findsOneWidget);
    });

    testWidgets('Sync status bar is visible',
        (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify sync status bar is present in the app bar
      expect(find.byType(AppBar), findsOneWidget);
    });
  });
} 