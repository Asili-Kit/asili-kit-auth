import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'api_config.dart';

class AuthService {
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse("${ApiConfig.baseUrl}/auth/login"),
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: {"username": email, "password": password},
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data; // access + refresh + expires
    } else {
      throw Exception(data["detail"] ?? "Login failed");
    }
  }

  Future<Map<String, dynamic>> register(String email, String password) async {
    final url = Uri.parse("${ApiConfig.baseUrl}/auth/register");
    debugPrint('[register] POST $url');

    try {
      final response = await http
          .post(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"email": email, "password": password}),
          )
          .timeout(const Duration(seconds: 20));

      final responseText = utf8.decode(response.bodyBytes);
      debugPrint('[register] status=${response.statusCode}');
      debugPrint('[register] body=$responseText');

      if (responseText.isEmpty) {
        throw Exception('Register failed: empty response body');
      }

      final data = jsonDecode(responseText) as Map<String, dynamic>;

      if (response.statusCode == 201 || response.statusCode == 200) {
        return data;
      }

      throw Exception(
        data["detail"] ??
            data["message"] ??
            'Register failed (${response.statusCode})',
      );
    } on TimeoutException {
      debugPrint('[register] timeout while calling $url');
      throw Exception('Register request timed out');
    } catch (e, st) {
      debugPrint('[register] request failed: $e');
      debugPrint('$st');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    final response = await http.post(
      Uri.parse("${ApiConfig.baseUrl}/auth/refresh"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"refresh_token": refreshToken}),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data;
    } else {
      throw Exception("Session expired");
    }
  }

  Future<void> logout({
    required String accessToken,
    String? refreshToken,
    bool allDevices = false,
  }) async {
    await http.post(
      Uri.parse("${ApiConfig.baseUrl}/auth/logout"),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $accessToken",
      },
      body: jsonEncode({
        "refresh_token": refreshToken,
        "all_devices": allDevices,
      }),
    );
  }

  Future<void> requestPasswordReset(String email) async {
    await http.post(
      Uri.parse("${ApiConfig.baseUrl}/auth/request-password-reset"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email}),
    );
  }

  Future<void> resetPassword(String token, String newPassword) async {
    final response = await http.post(
      Uri.parse("${ApiConfig.baseUrl}/auth/reset-password"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"token": token, "new_password": newPassword}),
    );

    if (response.statusCode != 200) {
      throw Exception("Password reset failed");
    }
  }

  Future<Map<String, dynamic>> getMe(String accessToken) async {
    final response = await http.get(
      Uri.parse("${ApiConfig.baseUrl}/users/me"),
      headers: {"Authorization": "Bearer $accessToken"},
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return data;
    } else {
      throw Exception("Failed to fetch user");
    }
  }
}
