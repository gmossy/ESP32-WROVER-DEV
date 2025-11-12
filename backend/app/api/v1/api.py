"""
API v1 Router - Aggregates all API endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import camera, esp32, n8n, sensors, ai_chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(camera.router, prefix="/camera", tags=["camera"])
api_router.include_router(esp32.router, prefix="/esp32", tags=["esp32"])
api_router.include_router(n8n.router, prefix="/n8n", tags=["n8n"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai"])
