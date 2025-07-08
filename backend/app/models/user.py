"""
User-related Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6, description="Password for registration")


class UserLogin(BaseModel):
    """User login model."""
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")


class UserUpdate(BaseModel):
    """User update model for admin operations."""
    is_approved: Optional[bool] = Field(None, description="User approval status")
    is_admin: Optional[bool] = Field(None, description="Admin status")


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that new password and confirmation match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New password and confirmation password do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validate new password requirements."""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters long')
        
        return v


class UserResponse(UserBase):
    """User response model."""
    id: int
    is_admin: bool
    is_approved: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UserProfile(UserBase):
    """User profile model with additional information."""
    id: int
    is_admin: bool
    is_approved: bool
    created_at: str
    total_favorites: Optional[int] = 0
    
    class Config:
        from_attributes = True 