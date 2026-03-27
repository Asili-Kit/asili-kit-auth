from datetime import timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth import AuthSession, LoginAttemptState, PasswordResetToken, generate_raw_token, hash_token, utcnow


def _normalize_now_for(value):
    now = utcnow()
    if value is None:
        return now
    if getattr(value, "tzinfo", None) is None and getattr(now, "tzinfo", None) is not None:
        return now.replace(tzinfo=None)
    return now


def _is_expired(value) -> bool:
    if value is None:
        return False
    now = _normalize_now_for(value)
    return value <= now


def _is_future(value) -> bool:
    if value is None:
        return False
    now = _normalize_now_for(value)
    return value > now


def generate_session_id() -> str:
    return uuid4().hex


def create_auth_session(db: Session, user_id: int, session_id: str, refresh_token: str, expires_in_days: int) -> AuthSession:
    expires_at = utcnow() + timedelta(days=expires_in_days)
    session = AuthSession(
        id=session_id,
        user_id=user_id,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_auth_session(db: Session, session_id: str) -> AuthSession | None:
    return db.query(AuthSession).filter(AuthSession.id == session_id).first()


def validate_refresh_session(db: Session, session_id: str, refresh_token: str) -> AuthSession | None:
    session = get_auth_session(db, session_id)
    if session is None:
        return None

    if session.is_revoked or _is_expired(session.expires_at):
        return None

    if session.refresh_token_hash != hash_token(refresh_token):
        # Token reuse/tampering attempt: revoke all sessions for that user.
        revoke_all_auth_sessions(db, session.user_id)
        return None

    return session


def revoke_auth_session(db: Session, session_id: str, replaced_by_session_id: str | None = None) -> bool:
    session = get_auth_session(db, session_id)
    if session is None:
        return False

    session.is_revoked = True
    session.revoked_at = utcnow()
    if replaced_by_session_id:
        session.replaced_by_session_id = replaced_by_session_id
    db.commit()
    return True


def revoke_all_auth_sessions(db: Session, user_id: int) -> int:
    sessions = db.query(AuthSession).filter(
        AuthSession.user_id == user_id,
        AuthSession.is_revoked.is_(False),
    ).all()
    now = utcnow()
    for session in sessions:
        session.is_revoked = True
        session.revoked_at = now
    db.commit()
    return len(sessions)


def rotate_refresh_session(
    db: Session,
    current_session: AuthSession,
    new_session_id: str,
    new_refresh_token: str,
) -> AuthSession:
    current_session.is_revoked = True
    current_session.revoked_at = utcnow()
    current_session.replaced_by_session_id = new_session_id

    new_session = AuthSession(
        id=new_session_id,
        user_id=current_session.user_id,
        refresh_token_hash=hash_token(new_refresh_token),
        expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def get_or_create_login_state(db: Session, user_id: int) -> LoginAttemptState:
    state = db.query(LoginAttemptState).filter(LoginAttemptState.user_id == user_id).first()
    if state is None:
        state = LoginAttemptState(user_id=user_id, failed_attempts=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def is_user_login_locked(db: Session, user_id: int) -> bool:
    state = get_or_create_login_state(db, user_id)
    return _is_future(state.locked_until)


def register_failed_login(db: Session, user_id: int) -> LoginAttemptState:
    state = get_or_create_login_state(db, user_id)
    if _is_future(state.locked_until):
        return state

    state.failed_attempts += 1
    if state.failed_attempts >= settings.LOGIN_MAX_ATTEMPTS:
        state.failed_attempts = 0
        state.locked_until = utcnow() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)

    db.commit()
    db.refresh(state)
    return state


def reset_failed_logins(db: Session, user_id: int) -> LoginAttemptState:
    state = get_or_create_login_state(db, user_id)
    state.failed_attempts = 0
    state.locked_until = None
    db.commit()
    db.refresh(state)
    return state


def create_password_reset_token(db: Session, user_id: int) -> str:
    raw_token = generate_raw_token()
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(token)
    db.commit()
    return raw_token


def consume_password_reset_token(db: Session, raw_token: str) -> PasswordResetToken | None:
    hashed = hash_token(raw_token)
    token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == hashed,
        PasswordResetToken.used_at.is_(None),
    ).first()

    if token is None:
        return None

    if _is_expired(token.expires_at):
        return None

    token.used_at = utcnow()
    db.commit()
    db.refresh(token)
    return token
