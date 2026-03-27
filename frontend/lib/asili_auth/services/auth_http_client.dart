import 'package:http/http.dart' as http;

import 'auth_service.dart';
import 'token_storage.dart';
import 'api_config.dart';

class AuthHttpClient {
  final AuthService authService;

  AuthHttpClient(this.authService);

  Future<http.Response> get(String endpoint) async {
    return _request(() {
      return http.get(
        Uri.parse("${ApiConfig.baseUrl}$endpoint"),
        headers: _headers(),
      );
    });
  }

  Future<http.Response> _request(
    Future<http.Response> Function() request,
  ) async {
    var response = await request();

    if (response.statusCode == 401) {
      final success = await _refreshToken();

      if (success) {
        response = await request(); // retry
      }
    }

    return response;
  }

  Map<String, String> _headers() {
    return {"Authorization": "Bearer ${_accessToken}"};
  }

  String? _accessToken;

  Future<bool> _refreshToken() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final data = await authService.refreshToken(refreshToken);

      _accessToken = data["access_token"];

      await TokenStorage.saveTokens(
        data["access_token"],
        data["refresh_token"],
      );

      return true;
    } catch (_) {
      await TokenStorage.clear();
      return false;
    }
  }
}
