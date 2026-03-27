from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.security import hash_password, validate_password_strength, verify_password
from app.dependencies import get_current_active_user
from app.schemas.auth import (
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    consume_password_reset_token,
    create_auth_session,
    create_password_reset_token,
    generate_session_id,
    is_user_login_locked,
    register_failed_login,
    reset_failed_logins,
    revoke_all_auth_sessions,
    revoke_auth_session,
    rotate_refresh_session,
    validate_refresh_session,
)
from app.services.user_service import create_user, get_user_by_email, get_user_by_id

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        validate_password_strength(user.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return create_user(db, user)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)

    if user and is_user_login_locked(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to too many failed login attempts",
        )

    if not user or not verify_password(form_data.password, user.password):
        if user:
            register_failed_login(db, user.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    reset_failed_logins(db, user.id)

    access_token = create_access_token(data={"sub": str(user.id)})
    session_id = generate_session_id()
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "sid": session_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    create_auth_session(
        db=db,
        user_id=user.id,
        session_id=session_id,
        refresh_token=refresh_token,
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_refresh_token(payload.refresh_token)
        user_id = int(decoded.get("sub"))
        session_id = decoded.get("sid")
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    session = validate_refresh_session(db, session_id=session_id, refresh_token=payload.refresh_token)
    if session is None or session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_session_id = generate_session_id()
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "sid": new_session_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    rotate_refresh_session(
        db=db,
        current_session=session,
        new_session_id=new_session_id,
        new_refresh_token=new_refresh_token,
    )

    new_access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    payload: LogoutRequest,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if payload.all_devices:
        count = revoke_all_auth_sessions(db, current_user.id)
        return MessageResponse(message=f"Logged out from {count} active session(s)")

    if payload.refresh_token:
        try:
            decoded = decode_refresh_token(payload.refresh_token)
            user_id = int(decoded.get("sub"))
            session_id = decoded.get("sid")
        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        if user_id != current_user.id or not session_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        revoke_auth_session(db, session_id)
        return MessageResponse(message="Logged out from current session")

    revoke_all_auth_sessions(db, current_user.id)
    return MessageResponse(message="Logged out from all sessions")


@router.post("/request-password-reset", response_model=MessageResponse)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    debug_token = None

    if user and user.is_active:
        token = create_password_reset_token(db, user.id)
        if settings.DEBUG:
            debug_token = token

    return MessageResponse(
        message="If this account exists, a reset link has been sent",
        debug_token=debug_token,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    try:
        validate_password_strength(payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    token = consume_password_reset_token(db, payload.token)
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user = get_user_by_id(db, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user")

    user.password = hash_password(payload.new_password)
    db.commit()

    revoke_all_auth_sessions(db, user.id)

    return MessageResponse(message="Password updated successfully")
