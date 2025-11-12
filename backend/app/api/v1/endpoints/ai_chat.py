"""
AI Chat API endpoints
Handles AI vision analysis, chat interactions, and image understanding
"""
from fastapi import APIRouter, HTTPException, Body, File, UploadFile
from typing import Optional, List
import base64
import logging
import os

from app.core.config import settings
from app.models.ai import ChatMessage, ImageAnalysisRequest, ImageAnalysisResponse, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    filename: Optional[str] = Body(None, description="Image filename from captures folder"),
    image_file: Optional[UploadFile] = File(None, description="Upload image directly"),
    prompt: str = Body("What do you see in this image?", description="Analysis prompt")
):
    """
    Analyze an image using AI vision model
    
    Can analyze either:
    - An existing image from the captures folder (by filename)
    - A newly uploaded image file
    
    Requires OPENAI_API_KEY to be configured
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Get image data
        if filename:
            filepath = os.path.join(settings.CAPTURE_DIR, filename)
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Image not found")
            
            with open(filepath, 'rb') as f:
                image_data = f.read()
        elif image_file:
            image_data = await image_file.read()
        else:
            raise HTTPException(status_code=400, detail="Either filename or image_file must be provided")
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Call OpenAI Vision API (placeholder - implement actual API call)
        # This would use the OpenAI Python SDK
        logger.info(f"Analyzing image with prompt: {prompt}")
        
        # Placeholder response
        analysis = {
            "description": "This is a placeholder response. Implement OpenAI Vision API integration.",
            "objects_detected": ["camera", "device"],
            "confidence": 0.85,
            "tags": ["technology", "electronics"]
        }
        
        return ImageAnalysisResponse(
            success=True,
            analysis=analysis,
            prompt=prompt,
            model=settings.AI_MODEL,
            message="Image analyzed successfully (placeholder)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message: str = Body(..., description="User message"),
    context: Optional[List[ChatMessage]] = Body(None, description="Previous conversation context"),
    include_latest_image: bool = Body(False, description="Include latest captured image in context")
):
    """
    Chat with AI assistant
    
    Can optionally include the latest captured image for visual context
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Build conversation context
        messages = []
        
        if context:
            messages.extend([{"role": msg.role, "content": msg.content} for msg in context])
        
        # Add latest image if requested
        if include_latest_image:
            # Get latest image from captures folder
            if os.path.exists(settings.CAPTURE_DIR):
                images = sorted(
                    [f for f in os.listdir(settings.CAPTURE_DIR) if f.endswith(('.jpg', '.jpeg'))],
                    reverse=True
                )
                if images:
                    latest_image = os.path.join(settings.CAPTURE_DIR, images[0])
                    with open(latest_image, 'rb') as f:
                        image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here's the latest image from the camera:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    })
        
        # Add user message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API (placeholder)
        logger.info(f"Chat request: {message}")
        
        # Placeholder response
        response_text = "This is a placeholder AI response. Implement OpenAI Chat API integration to get real responses."
        
        return ChatResponse(
            success=True,
            response=response_text,
            model=settings.AI_MODEL,
            message="Chat response generated (placeholder)"
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


@router.post("/label-image")
async def auto_label_image(
    filename: str = Body(..., description="Image filename to label")
):
    """
    Automatically generate a label for an image using AI
    
    Uses AI vision to analyze the image and suggest a descriptive label
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        filepath = os.path.join(settings.CAPTURE_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Analyze image to generate label
        with open(filepath, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Call OpenAI Vision API with labeling prompt (placeholder)
        logger.info(f"Auto-labeling image: {filename}")
        
        # Placeholder label
        suggested_label = "camera_view"
        
        return {
            "success": True,
            "filename": filename,
            "suggested_label": suggested_label,
            "confidence": 0.85,
            "message": "Label generated successfully (placeholder)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error labeling image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error labeling image: {str(e)}")


@router.post("/detect-objects")
async def detect_objects_in_image(
    filename: str = Body(..., description="Image filename to analyze")
):
    """
    Detect objects in an image using AI vision
    
    Returns list of detected objects with confidence scores
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        filepath = os.path.join(settings.CAPTURE_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Detect objects in image (placeholder)
        logger.info(f"Detecting objects in: {filename}")
        
        # Placeholder detections
        detections = [
            {"object": "camera", "confidence": 0.92, "bbox": [100, 100, 200, 200]},
            {"object": "device", "confidence": 0.87, "bbox": [150, 150, 250, 250]}
        ]
        
        return {
            "success": True,
            "filename": filename,
            "detections": detections,
            "count": len(detections),
            "message": "Objects detected successfully (placeholder)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting objects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error detecting objects: {str(e)}")


@router.get("/models")
async def list_available_models():
    """
    List available AI models
    """
    return {
        "current_model": settings.AI_MODEL,
        "available_models": [
            "gpt-4-vision-preview",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ],
        "configured": bool(settings.OPENAI_API_KEY)
    }
