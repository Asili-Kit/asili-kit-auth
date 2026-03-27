from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user