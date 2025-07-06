"""
User service for handling user-related business logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import db_manager
from app.core.security import security_manager
from app.models.user import UserCreate, UserLogin, UserUpdate, UserResponse
from app.models.common import Token
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Check if username already exists
            existing_user = await db_manager.get_by_field_single("users", "username", user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            
            # Hash the password
            hashed_password = security_manager.hash_password(user_data.password)
            
            # Create user data
            user_dict = {
                "username": user_data.username,
                "password_hash": hashed_password,
                "is_admin": False,
                "is_approved": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert user into database
            created_user = await db_manager.create("users", user_dict)
            if not created_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            return UserResponse(
                id=created_user["id"],
                username=created_user["username"],
                is_admin=bool(created_user["is_admin"]),
                is_approved=bool(created_user["is_approved"]),
                created_at=created_user["created_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def authenticate_user(login_data: UserLogin) -> Token:
        """Authenticate user and return token."""
        try:
            # Get user from database
            user = await db_manager.get_by_field_single("users", "username", login_data.username)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Verify password
            if not security_manager.verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if user is approved
            if not user["is_approved"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User not approved. Please wait for admin approval."
                )
            
            # Create JWT token
            token_data = {
                "user_id": user["id"],
                "username": user["username"],
                "is_admin": bool(user["is_admin"])
            }
            
            access_token = security_manager.create_access_token(token_data)
            
            user_response = UserResponse(
                id=user["id"],
                username=user["username"],
                is_admin=bool(user["is_admin"]),
                is_approved=bool(user["is_approved"]),
                created_at=user["created_at"]
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=168 * 3600,  # 7 days in seconds
                user=user_response.dict()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            user = await db_manager.get_by_id("users", user_id)
            if not user:
                return None
            
            return UserResponse(
                id=user["id"],
                username=user["username"],
                is_admin=bool(user["is_admin"]),
                is_approved=bool(user["is_approved"]),
                created_at=user["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    @staticmethod
    async def get_all_users() -> List[UserResponse]:
        """Get all users (admin only)."""
        try:
            users = await db_manager.get_all("users", limit=1000)
            return [
                UserResponse(
                    id=user["id"],
                    username=user["username"],
                    is_admin=bool(user["is_admin"]),
                    is_approved=bool(user["is_approved"]),
                    created_at=user["created_at"]
                )
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    @staticmethod
    async def update_user(user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """Update user (admin only)."""
        try:
            # Check if user exists
            existing_user = await db_manager.get_by_id("users", user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prepare update data
            update_data = {}
            if user_update.is_approved is not None:
                update_data["is_approved"] = user_update.is_approved
            if user_update.is_admin is not None:
                update_data["is_admin"] = user_update.is_admin
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )
            
            # Update user
            updated_user = await db_manager.update("users", user_id, update_data)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user"
                )
            
            return UserResponse(
                id=updated_user["id"],
                username=updated_user["username"],
                is_admin=bool(updated_user["is_admin"]),
                is_approved=bool(updated_user["is_approved"]),
                created_at=updated_user["created_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """Delete user (admin only)."""
        try:
            # Check if user exists
            existing_user = await db_manager.get_by_id("users", user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Delete user
            result = await db_manager.delete("users", user_id)
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 