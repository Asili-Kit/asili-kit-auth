abstract class AuthState {}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  final dynamic user;

  AuthAuthenticated(this.user);
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;

  AuthError(this.message);
}

// Password reset states
class PasswordResetRequested extends AuthState {
  final String message;

  PasswordResetRequested(this.message);
}

class PasswordResetSuccess extends AuthState {
  final String message;

  PasswordResetSuccess(this.message);
}
