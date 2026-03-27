from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.jwt import decode_access_token
from app.services.user_service import get_user_by_id
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        user_id_int = int(user_id)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = get_user_by_id(db, user_id_int)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user