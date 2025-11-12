"""
Camera models
"""
from pydantic import BaseModel, Field
from typing import Optional


class CaptureResponse(BaseModel):
    """Response model for image capture"""
    success: bool
    filename: Optional[str] = None
    filepath: Optional[str] = None
    size_bytes: int
    timestamp: str
    message: str


class CameraSettings(BaseModel):
    """Camera configuration settings"""
    resolution: str = Field(..., description="Image resolution (UXGA, SVGA, VGA, etc.)")
    quality: int = Field(..., ge=0, le=63, description="JPEG quality (0-63, lower is better)")
    brightness: int = Field(0, ge=-2, le=2, description="Brightness adjustment")
    contrast: int = Field(0, ge=-2, le=2, description="Contrast adjustment")
    saturation: int = Field(0, ge=-2, le=2, description="Saturation adjustment")


class ImageMetadata(BaseModel):
    """Image file metadata"""
    filename: str
    filepath: str
    size_bytes: int
    created_at: str
    modified_at: str
