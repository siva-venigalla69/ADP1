"""
Design-related Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DesignBase(BaseModel):
    """Base design model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Design title")
    description: Optional[str] = Field(None, description="Design description")
    short_description: Optional[str] = Field(None, description="Short description")
    long_description: Optional[str] = Field(None, description="Long description")
    category: str = Field(..., description="Design category")
    style: Optional[str] = Field(None, description="Design style")
    colour: Optional[str] = Field(None, description="Design colour")
    fabric: Optional[str] = Field(None, description="Fabric type")
    occasion: Optional[str] = Field(None, description="Occasion")
    size_available: Optional[str] = Field(None, description="Available sizes")
    price_range: Optional[str] = Field(None, description="Price range")
    tags: Optional[str] = Field(None, description="Tags")
    designer_name: Optional[str] = Field(None, description="Designer name")
    collection_name: Optional[str] = Field(None, description="Collection name")
    season: Optional[str] = Field(None, description="Season")


class DesignCreate(DesignBase):
    """Design creation model."""
    r2_object_key: str = Field(..., description="R2 object key for the image")
    featured: Optional[bool] = Field(False, description="Featured status")


class DesignUpdate(BaseModel):
    """Design update model."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = None
    colour: Optional[str] = None
    fabric: Optional[str] = None
    occasion: Optional[str] = None
    size_available: Optional[str] = None
    price_range: Optional[str] = None
    tags: Optional[str] = None
    designer_name: Optional[str] = None
    collection_name: Optional[str] = None
    season: Optional[str] = None
    featured: Optional[bool] = None
    status: Optional[str] = None


class DesignResponse(DesignBase):
    """Design response model."""
    id: int
    image_url: str = Field(..., description="R2 public URL for the image")
    r2_object_key: str
    featured: bool
    status: str
    view_count: int
    like_count: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class DesignListResponse(BaseModel):
    """Design list response with pagination."""
    designs: List[DesignResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class DesignSearchFilters(BaseModel):
    """Design search and filter parameters."""
    q: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    style: Optional[str] = Field(None, description="Filter by style")
    colour: Optional[str] = Field(None, description="Filter by colour")
    fabric: Optional[str] = Field(None, description="Filter by fabric")
    occasion: Optional[str] = Field(None, description="Filter by occasion")
    featured: Optional[bool] = Field(None, description="Filter by featured status")
    designer_name: Optional[str] = Field(None, description="Filter by designer")
    collection_name: Optional[str] = Field(None, description="Filter by collection")
    season: Optional[str] = Field(None, description="Filter by season") 