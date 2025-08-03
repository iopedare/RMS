import 'package:flutter/foundation.dart';

class User {
  final int id;
  final String username;
  final String role;
  final int roleId;
  final String deviceId;

  User({
    required this.id,
    required this.username,
    required this.role,
    required this.roleId,
    required this.deviceId,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      role: json['role'],
      roleId: json['role_id'],
      deviceId: json['device_id'],
    );
  }
}

class LoginResult {
  final bool success;
  final User? user;
  final String? error;

  LoginResult({
    required this.success,
    this.user,
    this.error,
  });
}

class AuthProvider extends ChangeNotifier {
  User? _currentUser;
  String? _token;
  bool _isAuthenticated = false;

  User? get currentUser => _currentUser;
  String? get token => _token;
  bool get isAuthenticated => _isAuthenticated;

  Future<LoginResult> login({
    required String username,
    required String password,
  }) async {
    try {
      // TODO: Implement actual API call to backend
      // For now, simulate login
      await Future.delayed(const Duration(seconds: 1));

      if (username == 'admin' && password == 'password123') {
        _currentUser = User(
          id: 1,
          username: 'admin',
          role: 'admin',
          roleId: 1,
          deviceId: 'device_001',
        );
        _token = 'dummy_token_${DateTime.now().millisecondsSinceEpoch}';
        _isAuthenticated = true;
        notifyListeners();

        return LoginResult(
          success: true,
          user: _currentUser,
        );
      } else {
        return LoginResult(
          success: false,
          error: 'Invalid credentials',
        );
      }
    } catch (e) {
      return LoginResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  Future<void> logout() async {
    _currentUser = null;
    _token = null;
    _isAuthenticated = false;
    notifyListeners();
  }

  void setUser(User user, String token) {
    _currentUser = user;
    _token = token;
    _isAuthenticated = true;
    notifyListeners();
  }
}
