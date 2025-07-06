"""
Admin API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from app.services.user_service import UserService
from app.models.user import UserUpdate, UserResponse
from app.models.common import MessageResponse, AnalyticsResponse
from app.core.security import get_admin_user, TokenData
from app.core.database import db_manager

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(admin_user: TokenData = Depends(get_admin_user)):
    """Get all users (admin only)."""
    return await UserService.get_all_users()


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., description="User ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Update user (admin only)."""
    user = await UserService.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int = Path(..., description="User ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    # Prevent admin from deleting themselves
    if user_id == admin_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    success = await UserService.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return MessageResponse(
        message="User deleted successfully",
        success=True
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(admin_user: TokenData = Depends(get_admin_user)):
    """Get analytics data (admin only)."""
    try:
        # Get basic counts
        total_users = await db_manager.count("users")
        total_designs = await db_manager.count("designs")
        pending_users = await db_manager.count("users", "is_approved = ?", [False])
        featured_designs = await db_manager.count("designs", "featured = ?", [True])
        
        # Get total views and likes
        view_query = "SELECT SUM(view_count) as total_views FROM designs"
        view_result = await db_manager.client.execute_query(view_query)
        total_views = view_result.get("results", [{}])[0].get("total_views", 0) or 0
        
        like_query = "SELECT SUM(like_count) as total_likes FROM designs"
        like_result = await db_manager.client.execute_query(like_query)
        total_likes = like_result.get("results", [{}])[0].get("total_likes", 0) or 0
        
        # Get popular categories
        category_query = """
        SELECT category, COUNT(*) as count 
        FROM designs 
        WHERE status = 'active' 
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 5
        """
        category_result = await db_manager.client.execute_query(category_query)
        popular_categories = category_result.get("results", [])
        
        # Get recent activity (recent designs)
        recent_query = """
        SELECT title, created_at, 'design_created' as activity_type 
        FROM designs 
        ORDER BY created_at DESC 
        LIMIT 5
        """
        recent_result = await db_manager.client.execute_query(recent_query)
        recent_activity = recent_result.get("results", [])
        
        return AnalyticsResponse(
            total_users=total_users,
            total_designs=total_designs,
            total_views=total_views,
            total_likes=total_likes,
            active_users=total_users - pending_users,  # Simplified calculation
            featured_designs=featured_designs,
            pending_users=pending_users,
            popular_categories=popular_categories,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(admin_user: TokenData = Depends(get_admin_user)):
    """Get users pending approval (admin only)."""
    try:
        users = await db_manager.get_by_field("users", "is_approved", False)
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
        raise HTTPException(status_code=500, detail=f"Failed to get pending users: {str(e)}")


@router.post("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: int = Path(..., description="User ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Approve a user (admin only)."""
    user_update = UserUpdate(is_approved=True)
    user = await UserService.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return MessageResponse(
        message=f"User {user.username} approved successfully",
        success=True
    )


@router.post("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int = Path(..., description="User ID"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Reject a user (admin only)."""
    user_update = UserUpdate(is_approved=False)
    user = await UserService.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return MessageResponse(
        message=f"User {user.username} rejected successfully",
        success=True
    ) 