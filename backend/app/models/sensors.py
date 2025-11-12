"""
Sensor models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class SensorReading(BaseModel):
    """Generic sensor reading"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    metadata: Dict[str, Any] = {}


class MotionEvent(BaseModel):
    """Motion detection event"""
    sensor_id: str
    timestamp: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}


class LCDMessage(BaseModel):
    """LCD display message"""
    text: str = Field(..., max_length=80)
    line: int = Field(1, ge=1, le=4, description="LCD line number (1-4)")
    duration_seconds: Optional[int] = Field(None, description="Display duration (None = permanent)")


class SensorStatus(BaseModel):
    """Sensor status"""
    sensor_id: str
    sensor_type: str
    status: str
    last_reading: Optional[SensorReading] = None
