# Asili Kit Auth

Complete authentication starter kit for developers who want to ship faster without rebuilding auth from scratch.

This repository includes:
- A FastAPI backend authentication API
- A Flutter authentication module ready to plug into mobile apps

## What You Get

- Register and login
- JWT access token and refresh token rotation
- Session revoke (current session or all sessions)
- Password reset with one-time token
- Login lockout after repeated failed attempts
- Flutter auth state handling with flutter_bloc

## Repository Structure

- `backend/`: FastAPI auth API
- `frontend/`: Flutter auth module
- `INTEGRATION_ROADMAP.md`: phased integration and hardening plan

## 15-Minute Integration Quickstart

### Step 1 - Start Backend API

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Backend available at:
- API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Step 2 - Configure Flutter Module

```bash
cd frontend
flutter pub get
```

Run with environment variables:

```bash
flutter run \
  --dart-define=ASILI_ENV=dev \
  --dart-define=ASILI_API_BASE_URL=http://127.0.0.1:8000
```

For Android emulator host networking, use:

```bash
flutter run \
  --dart-define=ASILI_ENV=dev \
  --dart-define=ASILI_API_BASE_URL=http://10.0.2.2:8000
```

### Step 3 - Plug Into App Startup

Create and provide the auth cubit, then render the auth wrapper:

```dart
final authService = AuthService();

BlocProvider(
  create: (_) => AuthCubit(authService)..checkAuth(),
  child: const AuthWrapper(),
)
```

### Step 4 - Verify End-to-End Flow

- Register a user
- Login and access protected user profile
- Restart app and verify persisted auth state
- Logout and verify session is revoked

## Production Checklist

- Set a strong `SECRET_KEY` in backend environment
- Use `AUTO_CREATE_TABLES=False` in production
- Run Alembic migrations before API startup
- Use secure token storage on mobile (keystore/keychain-backed)
- Use per-environment backend URLs (dev/staging/prod)

## Documentation

- Backend guide: `backend/README.md`
- API error contract: `backend/README.md#api-error-contract`
- Frontend guide: `frontend/README.md`
- Integration plan: `INTEGRATION_ROADMAP.md`

## Versioning

- **Backend**: Follow semantic versioning. Breaking changes require migration guide.
- **Frontend**: Pin to compatible backend version in `pubspec.yaml` or docs.
- **Migrations**: Always run `alembic upgrade head` before API startup.

## Current Status

✅ **Phase 1 — Safe Defaults**: Complete
- Secure config validation ✓
- Production/dev separation ✓  
- Mobile-backend contract ✓

✅ **Phase 2 — Integration**: Complete
- 15-min quickstart ✓
- API error contract ✓
- Environment strategy ✓

🔄 **Phase 3 — Production Hardening**: Planned
- Safe defaults added
- Backend and frontend docs now in English
- Logout backend contract aligned with mobile module

Next focus:
- Environment-specific frontend configuration
- Integration sample app improvements
