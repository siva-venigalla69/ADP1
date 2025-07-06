"""
Common Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MessageResponse(BaseModel):
    """Standard message response model."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    success: bool = False


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class ImageUploadResponse(BaseModel):
    """Image upload response model."""
    object_key: str
    upload_url: Optional[str] = None
    public_url: str


class PaginationParams(BaseModel):
    """Pagination parameters model."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class CategoryResponse(BaseModel):
    """Category response model."""
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    sort_order: int
    is_active: bool


class AppSettingsResponse(BaseModel):
    """App settings response model."""
    id: int
    allow_screenshots: bool
    allow_downloads: bool
    watermark_enabled: bool
    max_upload_size: int
    supported_formats: str
    gallery_per_page: int
    featured_designs_count: int
    maintenance_mode: bool
    app_version: str
    updated_at: str


class AppSettingsUpdate(BaseModel):
    """App settings update model."""
    allow_screenshots: Optional[bool] = None
    allow_downloads: Optional[bool] = None
    watermark_enabled: Optional[bool] = None
    max_upload_size: Optional[int] = None
    supported_formats: Optional[str] = None
    gallery_per_page: Optional[int] = None
    featured_designs_count: Optional[int] = None
    maintenance_mode: Optional[bool] = None
    app_version: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    total_users: int
    total_designs: int
    total_views: int
    total_likes: int
    active_users: int
    featured_designs: int
    pending_users: int
    popular_categories: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]] 