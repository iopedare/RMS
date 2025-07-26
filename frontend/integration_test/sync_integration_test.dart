import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:retail_management_system_frontend/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Device Registration & Sync Status Integration', () {
    testWidgets('Successful device registration and sync status',
        (WidgetTester tester) async {
      app.testMode = false; // Normal operation
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 8));
      expect(find.textContaining('Registered'), findsWidgets);
      expect(find.textContaining('Device'), findsWidgets);
      expect(find.textContaining('Pending'), findsWidgets);
    });

    testWidgets('Device registration failure shows error status',
        (WidgetTester tester) async {
      app.testMode = true; // Simulate registration failure
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 8));
      expect(find.textContaining('Disconnected'), findsWidgets);
      expect(
          find.byIcon(Icons.refresh), findsOneWidget); // Check for retry button
    });

    testWidgets('WebSocket disconnection and reconnection',
        (WidgetTester tester) async {
      app.testMode = true; // Simulate WebSocket disconnection
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 8));
      expect(find.textContaining('Disconnected'), findsWidgets);
      // Optionally, set app.testMode = false and re-init to simulate reconnection
    });
  });
}
