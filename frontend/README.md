# Asili Auth Flutter Module

## Overview

Asili Auth is a Flutter authentication module designed to integrate with the AsiliKit Auth FastAPI backend.

Core capabilities:

- Login and register flows
- Auth state management with `flutter_bloc`
- Access/refresh token persistence
- Auth wrapper for protected navigation
- Logout and password reset API support

## Requirements

- Flutter SDK 3.10+

## Quickstart

```bash
cd frontend
flutter pub get
```

## Configuration

Configure backend URL per environment with Dart defines:

```bash
flutter run \
	--dart-define=ASILI_ENV=dev \
	--dart-define=ASILI_API_BASE_URL=http://127.0.0.1:8000
```

Example staging:

```bash
flutter run \
	--dart-define=ASILI_ENV=staging \
	--dart-define=ASILI_API_BASE_URL=https://staging-api.example.com
```

Example production:

```bash
flutter run \
	--dart-define=ASILI_ENV=prod \
	--dart-define=ASILI_API_BASE_URL=https://api.example.com
```

Notes:
- No code change is required when switching environments.
- Do not include a trailing slash in `ASILI_API_BASE_URL`.
- On Android emulator, use `http://10.0.2.2:8000` to reach a backend running on host machine.

## Usage

Create and provide `AuthCubit`, then render `AuthWrapper`:

```dart
final authService = AuthService();

BlocProvider(
	create: (_) => AuthCubit(authService)..checkAuth(),
	child: const AuthWrapper(),
)
```

Authentication flow summary:
- Call `checkAuth()` on startup.
- Use `AuthWrapper` to route authenticated vs unauthenticated users.
- Use `logout()` to clear local tokens and revoke server-side session.

## Security notes

- Ensure the backend API is running before testing mobile auth flows.
- For production apps, prefer secure storage for tokens (keystore/keychain-backed).
- Consider environment-specific API URLs for dev/staging/prod.

## Troubleshooting

- Immediate `401` on app start: token may be expired; refresh flow should run before retry.
- Logout appears local only: verify backend URL and Authorization header delivery.
- Login fails with connection error: confirm backend host is reachable from emulator/device.
