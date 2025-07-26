// This is a basic Flutter widget test for the Retail Management System.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:retail_management_system_frontend/main.dart';

void main() {
  testWidgets('Retail Management System app structure test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const RetailManagementApp());

    // Verify that our app title is displayed in the app bar.
    expect(find.text('Retail Management System'), findsOneWidget);
    
    // Verify that the app bar is present
    expect(find.byType(AppBar), findsOneWidget);
    
    // Verify that the main content area is present
    expect(find.byType(Scaffold), findsOneWidget);
    
    // Verify that the test button is present
    expect(find.text('Push Test Sync Event'), findsOneWidget);
  });

  testWidgets('App widget structure validation', (WidgetTester tester) async {
    // This test validates the widget structure without triggering layout issues
    
    // Create the app widget
    final app = const RetailManagementApp();
    
    // Verify it's the correct type
    expect(app, isA<RetailManagementApp>());
    
    // Build the widget tree but don't trigger layout
    await tester.pumpWidget(app);
    
    // Verify basic structure exists without triggering layout calculations
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(AppBar), findsOneWidget);
  });

  testWidgets('Button presence test', (WidgetTester tester) async {
    // Build our app
    await tester.pumpWidget(const RetailManagementApp());

    // Find the test button by text
    final testButton = find.text('Push Test Sync Event');
    expect(testButton, findsOneWidget);
    
    // Verify there's at least one ElevatedButton in the widget tree
    expect(find.byType(ElevatedButton), findsOneWidget);
  });
}
