# AsiliKit Auth API

## Overview

AsiliKit Auth API is a FastAPI authentication backend designed for fast integration into new or existing projects.

Core capabilities:
- registration and login
- access token + refresh token with rotation
- logout for current session or all sessions
- password reset with one-time token
- temporary lockout after multiple failed login attempts

## Prerequisites

- Python 3.10+

## Quickstart

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Configuration

1. Copy `.env.example` to `.env`
2. Adjust values:

```env
SECRET_KEY=YOUR_LONG_RANDOM_SECRET
DEBUG=False
DATABASE_URL=sqlite:///./asili.db
AUTO_CREATE_TABLES=False
```

Notes:
- In production (`DEBUG=False`), `SECRET_KEY` must be a strong value (the API fails fast if it is unsafe).
- `AUTO_CREATE_TABLES=True` is useful for local quickstart only.
- For production, set `AUTO_CREATE_TABLES=False` and apply Alembic migrations before startup.

## Usage

Base URL: `http://127.0.0.1:8000`

Interactive docs:
- Swagger: `http://127.0.0.1:8000/docs`

Main endpoints:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/request-password-reset`
- `POST /auth/reset-password`
- `GET /users/me`

## API error contract

Error responses follow FastAPI default shape:

```json
{
	"detail": "Human-readable message"
}
```

Primary auth-related errors:

| Endpoint | Status | Typical detail | Integrator action |
| --- | --- | --- | --- |
| `POST /auth/login` | `401` | `Invalid email or password` | Show invalid credentials message and allow retry. |
| `POST /auth/login` | `423` | `Account temporarily locked due to too many failed login attempts` | Show lockout message and block new attempts until lock window passes. |
| `POST /auth/refresh` | `401` | `Invalid refresh token` | Clear local tokens and force full login. |
| `POST /auth/logout` | `400` | `Invalid refresh token` | Clear local tokens; optional warning toast; do not block local logout. |
| `POST /auth/logout` | `401` | `Invalid authentication` | Access token missing/expired; clear local state and navigate to login. |
| `GET /users/me` | `401` | `Invalid authentication` or `User not found` | Trigger refresh flow once; if still failing, force login. |
| `POST /auth/reset-password` | `400` | `Invalid or expired reset token` | Ask user to request a new reset link/token. |
| `POST /auth/register` | `400` | password policy message or `Email already registered` | Show exact validation message to user. |

Recommended client behavior:
- On `401` from protected endpoints: try refresh once, then clear tokens and go to login.
- On `423`: do not spam retries; communicate wait period clearly.
- On validation `400`: surface backend message directly when safe for UX.

## Operations

Start server:

```bash
uvicorn app.main:app --reload
```

Database migrations:

Use Alembic as the source of truth in production.

New auth tables can be created automatically at startup via SQLAlchemy:
- `auth_sessions`
- `login_attempt_states`
- `password_reset_tokens`

This behavior depends on `AUTO_CREATE_TABLES`.

Alembic is initialized and an initial migration is available in `alembic/versions`.

Useful commands:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe_change"
```

In production, run `alembic upgrade head` before starting the API.

## Security notes

`/auth/request-password-reset` returns `debug_token` only when `DEBUG=True`.
In production (`DEBUG=False`), connect email delivery using this token in your mail service.

## Tests

```bash
pytest -q
```

## Troubleshooting

- `401 Invalid authentication`: check access token format and expiration.
- `401 Invalid refresh token`: verify refresh token rotation and session state.
- `423 Locked`: user hit failed login threshold; wait for lock window or adjust settings.
