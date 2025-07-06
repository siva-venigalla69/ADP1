"""
Design service for handling design-related business logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.database import db_manager
from app.core.storage import storage_manager
from app.models.design import (
    DesignCreate, DesignUpdate, DesignResponse, DesignListResponse, 
    DesignSearchFilters
)
from app.models.common import PaginationParams
from app.core.config import settings
from fastapi import HTTPException, status
import logging
import math

logger = logging.getLogger(__name__)


class DesignService:
    """Service class for design-related operations."""
    
    @staticmethod
    def _format_design_response(design_row: Dict[str, Any]) -> DesignResponse:
        """Format a design database row into a DesignResponse."""
        return DesignResponse(
            id=design_row["id"],
            title=design_row["title"],
            description=design_row.get("description"),
            short_description=design_row.get("short_description"),
            long_description=design_row.get("long_description"),
            image_url=storage_manager.get_public_url(design_row["r2_object_key"]),
            r2_object_key=design_row["r2_object_key"],
            category=design_row["category"],
            style=design_row.get("style"),
            colour=design_row.get("colour"),
            fabric=design_row.get("fabric"),
            occasion=design_row.get("occasion"),
            size_available=design_row.get("size_available"),
            price_range=design_row.get("price_range"),
            tags=design_row.get("tags"),
            featured=bool(design_row.get("featured", False)),
            status=design_row.get("status", "active"),
            view_count=design_row.get("view_count", 0),
            like_count=design_row.get("like_count", 0),
            designer_name=design_row.get("designer_name"),
            collection_name=design_row.get("collection_name"),
            season=design_row.get("season"),
            created_at=design_row["created_at"],
            updated_at=design_row.get("updated_at", design_row["created_at"])
        )
    
    @staticmethod
    async def create_design(design_data: DesignCreate) -> DesignResponse:
        """Create a new design."""
        try:
            # Verify R2 object exists
            if not await storage_manager.file_exists(design_data.r2_object_key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="R2 object key not found"
                )
            
            # Create design data
            design_dict = {
                "title": design_data.title,
                "description": design_data.description,
                "short_description": design_data.short_description,
                "long_description": design_data.long_description,
                "r2_object_key": design_data.r2_object_key,
                "category": design_data.category,
                "style": design_data.style,
                "colour": design_data.colour,
                "fabric": design_data.fabric,
                "occasion": design_data.occasion,
                "size_available": design_data.size_available,
                "price_range": design_data.price_range,
                "tags": design_data.tags,
                "featured": design_data.featured,
                "status": "active",
                "view_count": 0,
                "like_count": 0,
                "designer_name": design_data.designer_name,
                "collection_name": design_data.collection_name,
                "season": design_data.season,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert design into database
            created_design = await db_manager.create("designs", design_dict)
            if not created_design:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create design"
                )
            
            return DesignService._format_design_response(created_design)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def get_design_by_id(design_id: int) -> Optional[DesignResponse]:
        """Get design by ID and increment view count."""
        try:
            # Get design from database
            design = await db_manager.get_by_id("designs", design_id)
            if not design:
                return None
            
            # Increment view count
            await db_manager.update("designs", design_id, {
                "view_count": design.get("view_count", 0) + 1
            })
            
            # Update the design object for response
            design["view_count"] = design.get("view_count", 0) + 1
            
            return DesignService._format_design_response(design)
            
        except Exception as e:
            logger.error(f"Error getting design by ID: {str(e)}")
            return None
    
    @staticmethod
    async def get_designs(
        pagination: PaginationParams,
        filters: DesignSearchFilters
    ) -> DesignListResponse:
        """Get designs with pagination and filters."""
        try:
            # Build query conditions
            conditions = []
            params = []
            
            # Add search query
            if filters.q:
                search_fields = ["title", "description", "short_description", "long_description", "tags"]
                search_conditions = []
                for field in search_fields:
                    search_conditions.append(f"{field} LIKE ?")
                    params.append(f"%{filters.q}%")
                conditions.append(f"({' OR '.join(search_conditions)})")
            
            # Add filters
            filter_mapping = {
                "category": filters.category,
                "style": filters.style,
                "colour": filters.colour,
                "fabric": filters.fabric,
                "occasion": filters.occasion,
                "designer_name": filters.designer_name,
                "collection_name": filters.collection_name,
                "season": filters.season,
            }
            
            for field, value in filter_mapping.items():
                if value:
                    conditions.append(f"{field} = ?")
                    params.append(value)
            
            if filters.featured is not None:
                conditions.append("featured = ?")
                params.append(filters.featured)
            
            # Add status filter (only active designs)
            conditions.append("status = ?")
            params.append("active")
            
            # Build WHERE clause
            where_clause = " AND ".join(conditions)
            
            # Get total count
            total_count = await db_manager.count("designs", where_clause, params)
            
            # Calculate pagination
            total_pages = math.ceil(total_count / pagination.per_page)
            offset = (pagination.page - 1) * pagination.per_page
            
            # Get designs
            query = f"SELECT * FROM designs WHERE {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([pagination.per_page, offset])
            
            result = await db_manager.client.execute_query(query, params)
            design_rows = result.get("results", [])
            
            designs = [DesignService._format_design_response(design) for design in design_rows]
            
            return DesignListResponse(
                designs=designs,
                total=total_count,
                page=pagination.page,
                per_page=pagination.per_page,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting designs: {str(e)}")
            return DesignListResponse(
                designs=[],
                total=0,
                page=pagination.page,
                per_page=pagination.per_page,
                total_pages=0
            )
    
    @staticmethod
    async def get_featured_designs(limit: int = 10) -> List[DesignResponse]:
        """Get featured designs."""
        try:
            query = "SELECT * FROM designs WHERE featured = ? AND status = ? ORDER BY created_at DESC LIMIT ?"
            result = await db_manager.client.execute_query(query, [True, "active", limit])
            design_rows = result.get("results", [])
            
            return [DesignService._format_design_response(design) for design in design_rows]
            
        except Exception as e:
            logger.error(f"Error getting featured designs: {str(e)}")
            return []
    
    @staticmethod
    async def update_design(design_id: int, design_update: DesignUpdate) -> Optional[DesignResponse]:
        """Update design (admin only)."""
        try:
            # Check if design exists
            existing_design = await db_manager.get_by_id("designs", design_id)
            if not existing_design:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Design not found"
                )
            
            # Prepare update data
            update_data = {}
            update_fields = [
                "title", "description", "short_description", "long_description",
                "category", "style", "colour", "fabric", "occasion",
                "size_available", "price_range", "tags", "designer_name",
                "collection_name", "season", "featured", "status"
            ]
            
            for field in update_fields:
                value = getattr(design_update, field, None)
                if value is not None:
                    update_data[field] = value
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update design
            updated_design = await db_manager.update("designs", design_id, update_data)
            if not updated_design:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update design"
                )
            
            return DesignService._format_design_response(updated_design)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def delete_design(design_id: int) -> bool:
        """Delete design (admin only)."""
        try:
            # Check if design exists
            existing_design = await db_manager.get_by_id("designs", design_id)
            if not existing_design:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Design not found"
                )
            
            # Delete from R2 storage
            await storage_manager.delete_file(existing_design["r2_object_key"])
            
            # Delete from database
            result = await db_manager.delete("designs", design_id)
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting design: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    async def add_to_favorites(user_id: int, design_id: int) -> bool:
        """Add design to user favorites."""
        try:
            # Check if design exists
            design = await db_manager.get_by_id("designs", design_id)
            if not design:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Design not found"
                )
            
            # Check if already favorited
            existing_favorite = await db_manager.get_by_field_single(
                "user_favorites", "user_id", user_id
            )
            if existing_favorite:
                for fav in existing_favorite:
                    if fav.get("design_id") == design_id:
                        return True  # Already favorited
            
            # Add to favorites
            favorite_data = {
                "user_id": user_id,
                "design_id": design_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await db_manager.create("user_favorites", favorite_data)
            return result is not None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return False
    
    @staticmethod
    async def remove_from_favorites(user_id: int, design_id: int) -> bool:
        """Remove design from user favorites."""
        try:
            # Find and delete favorite
            query = "DELETE FROM user_favorites WHERE user_id = ? AND design_id = ?"
            result = await db_manager.client.execute_query(query, [user_id, design_id])
            return result.get("meta", {}).get("changes", 0) > 0
            
        except Exception as e:
            logger.error(f"Error removing from favorites: {str(e)}")
            return False
    
    @staticmethod
    async def get_user_favorites(user_id: int) -> List[DesignResponse]:
        """Get user's favorite designs."""
        try:
            query = """
            SELECT d.* FROM designs d
            JOIN user_favorites uf ON d.id = uf.design_id
            WHERE uf.user_id = ? AND d.status = 'active'
            ORDER BY uf.created_at DESC
            """
            
            result = await db_manager.client.execute_query(query, [user_id])
            design_rows = result.get("results", [])
            
            return [DesignService._format_design_response(design) for design in design_rows]
            
        except Exception as e:
            logger.error(f"Error getting user favorites: {str(e)}")
            return [] 