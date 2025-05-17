from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Optional
from models.product import Product, ProductImage
from services.image_service import image_service
from database.repositories.product_repository import product_repository
#from api.dependencies import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/{ean}")
async def upload_image(
    ean: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    #current_user = Depends(get_current_user)
):
    """Upload an image for a specific product by EAN"""
    # Check if product exists
    product = await product_repository.get_by_ean(ean)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Upload image
    try:
        result = await image_service.upload_product_image(ean, file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ean}")
async def get_product_images(
    ean: str,
    #current_user = Depends(get_current_user)
):
    """Get all images for a specific product by EAN"""
    images = await product_repository.get_product_images(ean)
    return images

@router.put("/{ean}/primary/{image_id}")
async def set_primary_image(
    ean: str,
    image_id: int,
   #current_user = Depends(get_current_user)
):
    """Set a specific image as primary for a product"""
    success = await image_service.set_primary_image(ean, image_id)
    
    if success:
        return {"success": True, "message": "Primary image updated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update primary image")

@router.delete("/{ean}/{image_id}")
async def delete_image(
    ean: str,
    image_id: int,
    #current_user = Depends(get_current_user)
):
    """Delete a specific image for a product"""
    success = await image_service.delete_product_image(ean, image_id)
    
    if success:
        return {"success": True, "message": "Image deleted"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete image")