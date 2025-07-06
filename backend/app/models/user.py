"""
User-related Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr
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