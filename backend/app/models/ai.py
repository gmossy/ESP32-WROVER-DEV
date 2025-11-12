"""
AI/Chat models
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional


class ChatMessage(BaseModel):
    """Chat message"""
    role: str  # 'user' or 'assistant'
    content: str


class ImageAnalysisRequest(BaseModel):
    """Image analysis request"""
    filename: Optional[str] = None
    prompt: str = "What do you see in this image?"


class ImageAnalysisResponse(BaseModel):
    """Image analysis response"""
    success: bool
    analysis: Dict[str, Any]
    prompt: str
    model: str
    message: str


class ChatResponse(BaseModel):
    """Chat response"""
    success: bool
    response: str
    model: str
    message: str
