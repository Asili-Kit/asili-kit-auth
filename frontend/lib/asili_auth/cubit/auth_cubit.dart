import 'package:asili_auth/asili_auth/services/token_storage.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/auth_service.dart';
import 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  final AuthService authService;

  AuthCubit(this.authService) : super(AuthInitial());

  // 🔐 LOGIN
  Future<void> login(String email, String password) async {
    emit(AuthLoading());

    try {
      final data = await authService.login(email, password);

      final accessToken = data["access_token"];
      final refreshToken = data["refresh_token"];

      await TokenStorage.saveTokens(accessToken, refreshToken);

      final user = await authService.getMe(accessToken);

      emit(AuthAuthenticated(user));
    } catch (e) {
      emit(AuthError(e.toString()));
      emit(AuthUnauthenticated());
    }
  }

  // 📝 REGISTER
  Future<void> register(String email, String password) async {
    emit(AuthLoading());

    try {
      await authService.register(email, password);
      await login(email, password); // auto login
    } catch (e) {
      emit(AuthError(e.toString()));
      emit(AuthUnauthenticated());
    }
  }

  // 🔄 AUTO LOGIN
  Future<void> checkAuth() async {
    emit(AuthLoading());

    final accessToken = await TokenStorage.getAccessToken();

    if (accessToken == null) {
      emit(AuthUnauthenticated());
      return;
    }

    try {
      final user = await authService.getMe(accessToken);
      emit(AuthAuthenticated(user));
    } catch (_) {
      emit(AuthUnauthenticated());
    }
  }

  // 🚪 LOGOUT
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    final refreshToken = prefs.getString("refresh_token");
    final accessToken = prefs.getString("access_token");

    try {
      if (accessToken != null) {
        await authService.logout(
          accessToken: accessToken,
          refreshToken: refreshToken,
        );
      }
    } catch (_) {}

    await TokenStorage.clear();
    emit(AuthUnauthenticated());
  }
}
