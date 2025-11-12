"""
Camera API endpoints
Handles image capture, streaming, and camera configuration
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List
from datetime import datetime
import httpx
import os
import logging

from app.core.config import settings
from app.models.camera import CaptureResponse, CameraSettings, ImageMetadata

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/capture", response_model=CaptureResponse)
async def capture_image(
    save: bool = Query(True, description="Save image to disk"),
    label: Optional[str] = Query(None, description="Custom label for image")
):
    """
    Capture a new image from ESP32 camera
    
    - **save**: Whether to save the image to disk
    - **label**: Optional custom label for the image filename
    """
    try:
        async with httpx.AsyncClient(timeout=settings.ESP32_TIMEOUT) as client:
            response = await client.get(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/capture")
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to capture image from ESP32")
            
            image_data = response.content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if save:
                # Create filename with optional label
                if label:
                    filename = f"capture_{timestamp}_{label}.jpg"
                else:
                    filename = f"capture_{timestamp}.jpg"
                
                filepath = os.path.join(settings.CAPTURE_DIR, filename)
                
                # Ensure capture directory exists
                os.makedirs(settings.CAPTURE_DIR, exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                logger.info(f"Image captured and saved: {filename}")
                
                return CaptureResponse(
                    success=True,
                    filename=filename,
                    filepath=filepath,
                    size_bytes=len(image_data),
                    timestamp=timestamp,
                    message="Image captured successfully"
                )
            else:
                return CaptureResponse(
                    success=True,
                    size_bytes=len(image_data),
                    timestamp=timestamp,
                    message="Image captured (not saved)"
                )
                
    except httpx.TimeoutException:
        logger.error("ESP32 connection timeout")
        raise HTTPException(status_code=504, detail="ESP32 connection timeout")
    except Exception as e:
        logger.error(f"Error capturing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error capturing image: {str(e)}")


@router.get("/stream")
async def stream_camera():
    """
    Get live camera stream from ESP32
    Returns MJPEG stream
    """
    try:
        async def generate():
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream('GET', f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/capture") as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        return StreamingResponse(generate(), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error streaming camera: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error streaming camera: {str(e)}")


@router.get("/images", response_model=List[ImageMetadata])
async def list_images(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of images to return"),
    offset: int = Query(0, ge=0, description="Number of images to skip")
):
    """
    List all captured images with metadata
    
    - **limit**: Maximum number of images to return (1-500)
    - **offset**: Number of images to skip for pagination
    """
    try:
        if not os.path.exists(settings.CAPTURE_DIR):
            return []
        
        images = []
        files = sorted(
            [f for f in os.listdir(settings.CAPTURE_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))],
            reverse=True  # Most recent first
        )
        
        # Apply pagination
        paginated_files = files[offset:offset + limit]
        
        for filename in paginated_files:
            filepath = os.path.join(settings.CAPTURE_DIR, filename)
            stat = os.stat(filepath)
            
            images.append(ImageMetadata(
                filename=filename,
                filepath=filepath,
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
            ))
        
        return images
    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")


@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Retrieve a specific image by filename
    """
    filepath = os.path.join(settings.CAPTURE_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(filepath, media_type="image/jpeg")


@router.delete("/images/{filename}")
async def delete_image(filename: str):
    """
    Delete a specific image
    """
    filepath = os.path.join(settings.CAPTURE_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        os.remove(filepath)
        logger.info(f"Image deleted: {filename}")
        return {"success": True, "message": f"Image {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")


@router.post("/images/{filename}/rename")
async def rename_image(filename: str, new_label: str):
    """
    Rename an image with a new label
    """
    old_filepath = os.path.join(settings.CAPTURE_DIR, filename)
    
    if not os.path.exists(old_filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Extract timestamp from original filename
        parts = filename.split('_')
        if len(parts) >= 3:
            timestamp = f"{parts[1]}_{parts[2].split('.')[0]}"
            new_filename = f"capture_{timestamp}_{new_label}.jpg"
        else:
            new_filename = f"{new_label}.jpg"
        
        new_filepath = os.path.join(settings.CAPTURE_DIR, new_filename)
        os.rename(old_filepath, new_filepath)
        
        logger.info(f"Image renamed: {filename} -> {new_filename}")
        return {
            "success": True,
            "old_filename": filename,
            "new_filename": new_filename,
            "message": "Image renamed successfully"
        }
    except Exception as e:
        logger.error(f"Error renaming image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error renaming image: {str(e)}")


@router.get("/settings", response_model=CameraSettings)
async def get_camera_settings():
    """
    Get current camera settings from ESP32
    """
    # This would need to be implemented on the ESP32 side
    # For now, return default settings
    return CameraSettings(
        resolution="UXGA",
        quality=10,
        brightness=0,
        contrast=0,
        saturation=0
    )


@router.post("/settings", response_model=CameraSettings)
async def update_camera_settings(settings_update: CameraSettings):
    """
    Update camera settings on ESP32
    """
    # This would need to be implemented on the ESP32 side
    # For now, return the settings as-is
    logger.info(f"Camera settings update requested: {settings_update}")
    return settings_update
