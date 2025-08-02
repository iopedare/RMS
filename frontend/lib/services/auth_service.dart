import 'dart:convert';
import 'package:http/http.dart' as http;
import '../providers/auth_provider.dart';

class AuthService {
  static const String baseUrl = 'http://localhost:5000';

  Future<LoginResult> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success'] == true) {
        final user = User.fromJson(data['user']);
        return LoginResult(
          success: true,
          user: user,
        );
      } else {
        return LoginResult(
          success: false,
          error: data['error'] ?? 'Login failed',
        );
      }
    } catch (e) {
      return LoginResult(
        success: false,
        error: 'Network error: $e',
      );
    }
  }

  Future<bool> logout(String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/logout'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<User?> verifyToken(String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/verify'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return User.fromJson(data['user']);
        }
      }
      return null;
    } catch (e) {
      return null;
    }
  }
} 