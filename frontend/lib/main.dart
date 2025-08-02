import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/sync_state_provider.dart';
import 'providers/auth_provider.dart';
import 'pages/login_page.dart';
import 'pages/sync_test_page.dart';

void main() {
  runApp(const RetailManagementApp());
}

class RetailManagementApp extends StatelessWidget {
  const RetailManagementApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => SyncStateProvider()),
        ChangeNotifierProvider(create: (context) => AuthProvider()),
      ],
      child: MaterialApp(
        title: 'Retail Management System',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const LoginPage(),
        routes: {
          '/dashboard': (context) => const SyncTestPage(),
        },
      ),
    );
  }
}
