"""
n8n Integration API endpoints
Handles workflow triggers, webhook management, and n8n communication
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
import httpx
import base64
import logging

from app.core.config import settings
from app.models.n8n import WorkflowTrigger, WorkflowStatus, WebhookPayload

router = APIRouter()
logger = logging.getLogger(__name__)


def get_n8n_auth():
    """Get basic auth for n8n"""
    credentials = f"{settings.N8N_BASIC_AUTH_USER}:{settings.N8N_BASIC_AUTH_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


@router.get("/status")
async def get_n8n_status():
    """
    Check n8n server status and connectivity
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.N8N_URL}/healthz",
                headers={"Authorization": get_n8n_auth()}
            )
            
            return {
                "online": response.status_code == 200,
                "url": settings.N8N_URL,
                "status_code": response.status_code,
                "message": "n8n is online and responding"
            }
    except Exception as e:
        logger.error(f"Error checking n8n status: {str(e)}")
        return {
            "online": False,
            "url": settings.N8N_URL,
            "message": f"n8n not reachable: {str(e)}"
        }


@router.get("/workflows")
async def list_workflows():
    """
    List all n8n workflows
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.N8N_URL}/api/v1/workflows",
                headers={"Authorization": get_n8n_auth()}
            )
            
            if response.status_code == 200:
                workflows = response.json()
                return {
                    "success": True,
                    "count": len(workflows.get("data", [])),
                    "workflows": workflows.get("data", [])
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch workflows")
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Get details of a specific workflow
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.N8N_URL}/api/v1/workflows/{workflow_id}",
                headers={"Authorization": get_n8n_auth()}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow: {str(e)}")


@router.post("/workflows/{workflow_id}/activate")
async def activate_workflow(workflow_id: str):
    """
    Activate a workflow
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{settings.N8N_URL}/api/v1/workflows/{workflow_id}",
                headers={"Authorization": get_n8n_auth()},
                json={"active": True}
            )
            
            if response.status_code == 200:
                logger.info(f"Workflow {workflow_id} activated")
                return {"success": True, "message": f"Workflow {workflow_id} activated"}
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to activate workflow")
    except Exception as e:
        logger.error(f"Error activating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error activating workflow: {str(e)}")


@router.post("/workflows/{workflow_id}/deactivate")
async def deactivate_workflow(workflow_id: str):
    """
    Deactivate a workflow
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{settings.N8N_URL}/api/v1/workflows/{workflow_id}",
                headers={"Authorization": get_n8n_auth()},
                json={"active": False}
            )
            
            if response.status_code == 200:
                logger.info(f"Workflow {workflow_id} deactivated")
                return {"success": True, "message": f"Workflow {workflow_id} deactivated"}
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to deactivate workflow")
    except Exception as e:
        logger.error(f"Error deactivating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deactivating workflow: {str(e)}")


@router.post("/trigger/camera-capture")
async def trigger_camera_capture_workflow(
    label: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Trigger n8n workflow for camera capture
    
    This sends a webhook to n8n to start a camera capture workflow
    """
    try:
        payload = {
            "event": "camera_capture",
            "timestamp": datetime.now().isoformat(),
            "label": label,
            "metadata": metadata or {}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # This assumes you have a webhook set up in n8n
            response = await client.post(
                f"{settings.N8N_URL}/webhook/camera-capture",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info("Camera capture workflow triggered")
                return {
                    "success": True,
                    "message": "Camera capture workflow triggered",
                    "payload": payload
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to trigger workflow")
    except Exception as e:
        logger.error(f"Error triggering workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering workflow: {str(e)}")


@router.post("/trigger/motion-detected")
async def trigger_motion_detection_workflow(
    sensor_id: str,
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Trigger n8n workflow for motion detection
    
    Sends motion detection event to n8n for processing
    """
    try:
        from datetime import datetime
        
        payload = {
            "event": "motion_detected",
            "timestamp": datetime.now().isoformat(),
            "sensor_id": sensor_id,
            "confidence": confidence,
            "metadata": metadata or {}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.N8N_URL}/webhook/motion-detected",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Motion detection workflow triggered for sensor {sensor_id}")
                return {
                    "success": True,
                    "message": "Motion detection workflow triggered",
                    "payload": payload
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to trigger workflow")
    except Exception as e:
        logger.error(f"Error triggering motion workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering motion workflow: {str(e)}")


@router.post("/webhook/{webhook_name}")
async def send_webhook(
    webhook_name: str,
    payload: Dict[str, Any] = Body(...)
):
    """
    Send custom webhook to n8n
    
    Generic endpoint to trigger any n8n webhook
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.N8N_URL}/webhook/{webhook_name}",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Webhook {webhook_name} triggered")
                return {
                    "success": True,
                    "message": f"Webhook {webhook_name} triggered",
                    "response": response.json() if response.content else None
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to send webhook")
    except Exception as e:
        logger.error(f"Error sending webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending webhook: {str(e)}")


@router.get("/executions")
async def list_executions(limit: int = 20):
    """
    List recent workflow executions
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.N8N_URL}/api/v1/executions",
                headers={"Authorization": get_n8n_auth()},
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                executions = response.json()
                return {
                    "success": True,
                    "count": len(executions.get("data", [])),
                    "executions": executions.get("data", [])
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch executions")
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing executions: {str(e)}")
