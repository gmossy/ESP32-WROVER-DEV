"""
n8n integration models
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional


class WorkflowTrigger(BaseModel):
    """Workflow trigger request"""
    workflow_id: str
    payload: Dict[str, Any]


class WorkflowStatus(BaseModel):
    """Workflow status"""
    workflow_id: str
    active: bool
    name: str


class WebhookPayload(BaseModel):
    """Generic webhook payload"""
    event: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
