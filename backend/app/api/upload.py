"""
Upload API routes for file management.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from app.core.storage import storage_manager
from app.core.security import get_admin_user, TokenData
from app.models.common import ImageUploadResponse
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    category: str = Query("general", description="Image category"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Upload an image to R2 storage (admin only)."""
    # Validate file type
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
        )
    
    try:
        # Generate object key
        object_key = storage_manager.generate_object_key(file.filename or "image.jpg", category)
        
        # Upload to R2
        success = await storage_manager.upload_file(
            file_content, 
            object_key, 
            file.content_type,
            metadata={
                "original_filename": file.filename or "",
                "uploaded_by": admin_user.username,
                "category": category
            }
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload image")
        
        # Get public URL
        public_url = storage_manager.get_public_url(object_key)
        
        return ImageUploadResponse(
            object_key=object_key,
            public_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/presigned-url", response_model=dict)
async def get_presigned_upload_url(
    filename: str = Query(..., description="Original filename"),
    category: str = Query("general", description="Image category"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """Get a presigned URL for direct upload to R2 (admin only)."""
    try:
        # Generate object key
        object_key = storage_manager.generate_object_key(filename, category)
        
        # Generate presigned URL
        presigned_url = await storage_manager.generate_presigned_url(object_key)
        
        if not presigned_url:
            raise HTTPException(status_code=500, detail="Failed to generate presigned URL")
        
        return {
            "object_key": object_key,
            "upload_url": presigned_url,
            "public_url": storage_manager.get_public_url(object_key)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")


@router.delete("/image/{object_key:path}")
async def delete_image(
    object_key: str,
    admin_user: TokenData = Depends(get_admin_user)
):
    """Delete an image from R2 storage (admin only)."""
    try:
        success = await storage_manager.delete_file(object_key)
        
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return {"message": "Image deleted successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")


@router.get("/images")
async def list_images(
    prefix: str = Query("", description="Prefix to filter images"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of images"),
    admin_user: TokenData = Depends(get_admin_user)
):
    """List images in R2 storage (admin only)."""
    try:
        images = await storage_manager.list_files(prefix, limit)
        return {"images": images, "count": len(images)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}") 