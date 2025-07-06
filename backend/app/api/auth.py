"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.services.user_service import UserService
from app.models.user import UserCreate, UserLogin, UserResponse
from app.models.common import Token, MessageResponse
from app.core.security import get_current_active_user, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        await UserService.create_user(user_data)
        return MessageResponse(
            message="Registration successful! Please wait for admin approval.",
            success=True
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Authenticate user and return access token."""
    return await UserService.authenticate_user(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_active_user)):
    """Get current user information."""
    user = await UserService.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: TokenData = Depends(get_current_active_user)):
    """Logout user (client should discard token)."""
    return MessageResponse(
        message="Logout successful. Please discard your access token.",
        success=True
    ) 