"""
Sensors API endpoints
Handles motion sensors, LCD display, and other extensible sensors
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.core.config import settings
from app.models.sensors import SensorReading, MotionEvent, LCDMessage, SensorStatus

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for sensor data (use Redis/DB in production)
motion_events: List[MotionEvent] = []
sensor_readings: Dict[str, List[SensorReading]] = {}


@router.get("/status")
async def get_sensors_status():
    """
    Get status of all connected sensors
    """
    return {
        "motion_sensor": {
            "enabled": settings.MOTION_SENSOR_ENABLED,
            "status": "active" if settings.MOTION_SENSOR_ENABLED else "disabled",
            "events_count": len(motion_events)
        },
        "lcd_screen": {
            "enabled": settings.LCD_SCREEN_ENABLED,
            "status": "active" if settings.LCD_SCREEN_ENABLED else "disabled"
        }
    }


@router.post("/motion/event")
async def record_motion_event(
    sensor_id: str = Body(..., description="Sensor identifier"),
    confidence: float = Body(1.0, ge=0.0, le=1.0, description="Detection confidence"),
    metadata: Optional[Dict[str, Any]] = Body(None)
):
    """
    Record a motion detection event
    
    Called when motion sensor detects movement
    """
    if not settings.MOTION_SENSOR_ENABLED:
        raise HTTPException(status_code=403, detail="Motion sensor is not enabled")
    
    event = MotionEvent(
        sensor_id=sensor_id,
        timestamp=datetime.now().isoformat(),
        confidence=confidence,
        metadata=metadata or {}
    )
    
    motion_events.append(event)
    logger.info(f"Motion detected by sensor {sensor_id} (confidence: {confidence})")
    
    # Optionally trigger n8n workflow
    # await trigger_motion_detection_workflow(sensor_id, confidence, metadata)
    
    return {
        "success": True,
        "event": event.dict(),
        "message": "Motion event recorded"
    }


@router.get("/motion/events")
async def get_motion_events(
    limit: int = 50,
    sensor_id: Optional[str] = None
):
    """
    Get recent motion detection events
    
    - **limit**: Maximum number of events to return
    - **sensor_id**: Filter by specific sensor
    """
    filtered_events = motion_events
    
    if sensor_id:
        filtered_events = [e for e in motion_events if e.sensor_id == sensor_id]
    
    # Return most recent events
    return {
        "count": len(filtered_events),
        "events": [e.dict() for e in filtered_events[-limit:]]
    }


@router.delete("/motion/events")
async def clear_motion_events():
    """
    Clear all motion detection events
    """
    global motion_events
    count = len(motion_events)
    motion_events = []
    
    logger.info(f"Cleared {count} motion events")
    return {
        "success": True,
        "cleared_count": count,
        "message": f"Cleared {count} motion events"
    }


@router.post("/lcd/display")
async def display_on_lcd(message: LCDMessage):
    """
    Display message on LCD screen
    
    Sends text to be displayed on the ESP32 LCD screen
    """
    if not settings.LCD_SCREEN_ENABLED:
        raise HTTPException(status_code=403, detail="LCD screen is not enabled")
    
    try:
        # This would send the message to ESP32 LCD endpoint
        # For now, just log it
        logger.info(f"LCD Display: {message.text} (line: {message.line}, duration: {message.duration_seconds}s)")
        
        return {
            "success": True,
            "message": "Text displayed on LCD",
            "displayed_text": message.text,
            "line": message.line
        }
    except Exception as e:
        logger.error(f"Error displaying on LCD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error displaying on LCD: {str(e)}")


@router.post("/lcd/clear")
async def clear_lcd():
    """
    Clear LCD screen
    """
    if not settings.LCD_SCREEN_ENABLED:
        raise HTTPException(status_code=403, detail="LCD screen is not enabled")
    
    try:
        # This would send clear command to ESP32
        logger.info("LCD screen cleared")
        
        return {
            "success": True,
            "message": "LCD screen cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing LCD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing LCD: {str(e)}")


@router.post("/reading")
async def record_sensor_reading(
    sensor_id: str = Body(...),
    sensor_type: str = Body(..., description="Type of sensor (temperature, humidity, etc.)"),
    value: float = Body(...),
    unit: str = Body(..., description="Unit of measurement"),
    metadata: Optional[Dict[str, Any]] = Body(None)
):
    """
    Record a generic sensor reading
    
    Extensible endpoint for any type of sensor data
    """
    reading = SensorReading(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        timestamp=datetime.now().isoformat(),
        metadata=metadata or {}
    )
    
    if sensor_id not in sensor_readings:
        sensor_readings[sensor_id] = []
    
    sensor_readings[sensor_id].append(reading)
    logger.info(f"Sensor reading recorded: {sensor_type} = {value} {unit}")
    
    return {
        "success": True,
        "reading": reading.dict(),
        "message": "Sensor reading recorded"
    }


@router.get("/readings/{sensor_id}")
async def get_sensor_readings(
    sensor_id: str,
    limit: int = 100
):
    """
    Get readings from a specific sensor
    
    - **sensor_id**: Sensor identifier
    - **limit**: Maximum number of readings to return
    """
    if sensor_id not in sensor_readings:
        return {
            "sensor_id": sensor_id,
            "count": 0,
            "readings": []
        }
    
    readings = sensor_readings[sensor_id][-limit:]
    
    return {
        "sensor_id": sensor_id,
        "count": len(readings),
        "readings": [r.dict() for r in readings]
    }


@router.get("/list")
async def list_sensors():
    """
    List all registered sensors
    """
    sensors = []
    
    # Motion sensor
    if settings.MOTION_SENSOR_ENABLED:
        sensors.append({
            "id": "motion_sensor_1",
            "type": "motion",
            "status": "active",
            "events_count": len(motion_events)
        })
    
    # LCD screen
    if settings.LCD_SCREEN_ENABLED:
        sensors.append({
            "id": "lcd_screen_1",
            "type": "display",
            "status": "active"
        })
    
    # Other sensors from readings
    for sensor_id, readings in sensor_readings.items():
        if readings:
            latest = readings[-1]
            sensors.append({
                "id": sensor_id,
                "type": latest.sensor_type,
                "status": "active",
                "readings_count": len(readings),
                "latest_value": f"{latest.value} {latest.unit}"
            })
    
    return {
        "count": len(sensors),
        "sensors": sensors
    }


@router.post("/configure")
async def configure_sensor(
    sensor_id: str = Body(...),
    sensor_type: str = Body(...),
    config: Dict[str, Any] = Body(...)
):
    """
    Configure a sensor
    
    Generic endpoint to update sensor configuration
    """
    try:
        logger.info(f"Configuring sensor {sensor_id} ({sensor_type}): {config}")
        
        # This would send configuration to ESP32
        # For now, just acknowledge
        
        return {
            "success": True,
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "config": config,
            "message": f"Sensor {sensor_id} configured"
        }
    except Exception as e:
        logger.error(f"Error configuring sensor: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error configuring sensor: {str(e)}")
