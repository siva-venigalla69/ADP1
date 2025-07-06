"""
Design API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional
from app.services.design_service import DesignService
from app.models.design import (
    DesignCreate, DesignUpdate, DesignResponse, DesignListResponse,
    DesignSearchFilters
)
from app.models.common import PaginationParams, MessageResponse
from app.core.security import get_current_active_user, get_admin_user, TokenData

router = APIRouter(prefix="/designs", tags=["Designs"])


@router.get("", response_model=DesignListResponse)
async def get_designs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    style: Optional[str] = Query(None, description="Filter by style"),
    colour: Optional[str] = Query(None, description="Filter by colour"),
    fabric: Optional[str] = Query(None, description="Filter by fabric"),
    occasion: Optional[str] = Query(None, description="Filter by occasion"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    designer_name: Optional[str] = Query(None, description="Filter by designer"),
    collection_name: Optional[str] = Query(None, description="Filter by collection"),
    season: Optional[str] = Query(None, description="Filter by season"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get designs with pagination and filters."""
    pagination = PaginationParams(page=page, per_page=per_page)
    filters = DesignSearchFilters(
        q=q, category=category, style=style, colour=colour,
        fabric=fabric, occasion=occasion, featured=featured,
        designer_name=designer_name, collection_name=collection_name,
        season=season
    )
    
    return await DesignService.get_designs(pagination, filters)


@router.get("/featured", response_model=list[DesignResponse])
async def get_featured_designs(
    limit: int = Query(10, ge=1, le=50, description="Number of featured designs"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get featured designs."""
    return await DesignService.get_featured_designs(limit)


@router.get("/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: int = Path(..., description="Design ID"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get a specific design by ID."""
    design = await DesignService.get_design_by_id(design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@router.post("", response_model=DesignResponse)
async def create_design(
    design_data: DesignCreate,
    admin_user: TokenData = Depends(get_admin_user)
):
    """Create a new design (admin only)."""
    return await DesignService.create_design(design_data)


@router.put("/{design_id}", response_model=DesignResponse)
async def update_design(
    design_update: DesignUpdate,
    design_id: int = Path(..., description="Design ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Update a design (admin only)."""
    design = await DesignService.update_design(design_id, design_update)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@router.delete("/{design_id}", response_model=MessageResponse)
async def delete_design(
    design_id: int = Path(..., description="Design ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Delete a design (admin only)."""
    success = await DesignService.delete_design(design_id)
    if not success:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return MessageResponse(
        message="Design deleted successfully",
        success=True
    )


@router.post("/{design_id}/favorite", response_model=MessageResponse)
async def add_to_favorites(
    design_id: int = Path(..., description="Design ID"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """Add design to user favorites."""
    success = await DesignService.add_to_favorites(current_user.user_id, design_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add to favorites")
    
    return MessageResponse(
        message="Design added to favorites",
        success=True
    )


@router.delete("/{design_id}/favorite", response_model=MessageResponse)
async def remove_from_favorites(
    design_id: int = Path(..., description="Design ID"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """Remove design from user favorites."""
    success = await DesignService.remove_from_favorites(current_user.user_id, design_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove from favorites")
    
    return MessageResponse(
        message="Design removed from favorites",
        success=True
    )


@router.get("/user/favorites", response_model=list[DesignResponse])
async def get_user_favorites(
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get user's favorite designs."""
    return await DesignService.get_user_favorites(current_user.user_id) 