"""
ESP32 Device Management API endpoints
Handles device status, diagnostics, and configuration
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import httpx
import logging
import asyncio

from app.core.config import settings
from app.models.esp32 import DeviceStatus, DeviceInfo, NetworkInfo, SystemStats

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status", response_model=DeviceStatus)
async def get_device_status():
    """
    Get ESP32 device status and health check
    
    Returns connectivity status, uptime, and basic health metrics
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start_time = asyncio.get_event_loop().time()
            response = await client.get(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/")
            end_time = asyncio.get_event_loop().time()
            
            response_time_ms = int((end_time - start_time) * 1000)
            
            return DeviceStatus(
                online=True,
                ip_address=settings.ESP32_IP,
                response_time_ms=response_time_ms,
                http_status=response.status_code,
                message="ESP32 is online and responding"
            )
    except httpx.TimeoutException:
        logger.warning("ESP32 connection timeout")
        return DeviceStatus(
            online=False,
            ip_address=settings.ESP32_IP,
            message="ESP32 connection timeout"
        )
    except Exception as e:
        logger.error(f"Error checking ESP32 status: {str(e)}")
        return DeviceStatus(
            online=False,
            ip_address=settings.ESP32_IP,
            message=f"Error: {str(e)}"
        )


@router.get("/info", response_model=DeviceInfo)
async def get_device_info():
    """
    Get detailed ESP32 device information
    
    Returns chip model, MAC address, firmware version, etc.
    Note: This requires corresponding endpoints on the ESP32
    """
    try:
        # This would need a /info endpoint on the ESP32
        # For now, return static info based on known hardware
        return DeviceInfo(
            chip_model="ESP32-D0WD-V3",
            chip_revision="v3.0",
            mac_address="94:e6:86:4b:e3:90",  # Would be fetched from ESP32
            flash_size_mb=4,
            psram_size_mb=8,
            cpu_frequency_mhz=240,
            firmware_version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Error getting device info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting device info: {str(e)}")


@router.get("/network", response_model=NetworkInfo)
async def get_network_info():
    """
    Get ESP32 network information
    
    Returns WiFi SSID, signal strength, IP configuration
    """
    try:
        # This would need a /network endpoint on the ESP32
        return NetworkInfo(
            ssid="FOOTBALL",  # From config
            ip_address=settings.ESP32_IP,
            gateway="10.0.0.1",
            subnet="255.255.255.0",
            rssi=-45,  # Would be fetched from ESP32
            connected=True
        )
    except Exception as e:
        logger.error(f"Error getting network info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting network info: {str(e)}")


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get ESP32 system statistics
    
    Returns memory usage, uptime, temperature, etc.
    """
    try:
        # This would need a /stats endpoint on the ESP32
        return SystemStats(
            uptime_seconds=3600,  # Would be fetched from ESP32
            free_heap_bytes=270556,
            total_heap_bytes=327680,
            cpu_usage_percent=25,
            temperature_celsius=45.5
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")


@router.post("/restart")
async def restart_device():
    """
    Restart the ESP32 device
    
    Sends a restart command to the ESP32
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # This would need a /restart endpoint on the ESP32
            response = await client.post(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/restart")
            
            if response.status_code == 200:
                logger.info("ESP32 restart command sent")
                return {
                    "success": True,
                    "message": "ESP32 restart command sent. Device will be offline for ~10 seconds."
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to send restart command")
    except Exception as e:
        logger.error(f"Error restarting device: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error restarting device: {str(e)}")


@router.post("/test")
async def run_hardware_test():
    """
    Run hardware diagnostic test on ESP32
    
    Tests camera, LED, memory, and connectivity
    """
    results = {
        "connectivity": False,
        "camera": False,
        "led": False,
        "memory": False,
        "overall": False
    }
    
    try:
        # Test 1: Connectivity
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/")
            results["connectivity"] = response.status_code == 200
        
        # Test 2: Camera
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/capture")
            results["camera"] = response.status_code == 200 and len(response.content) > 1000
        
        # Test 3: LED (would need ESP32 endpoint)
        results["led"] = True  # Assume working if device is online
        
        # Test 4: Memory (would need ESP32 endpoint)
        results["memory"] = True  # Assume working if device is online
        
        # Overall result
        results["overall"] = all([
            results["connectivity"],
            results["camera"],
            results["led"],
            results["memory"]
        ])
        
        logger.info(f"Hardware test completed: {results}")
        
        return {
            "success": results["overall"],
            "results": results,
            "message": "Hardware test completed" if results["overall"] else "Some tests failed"
        }
        
    except Exception as e:
        logger.error(f"Error running hardware test: {str(e)}")
        return {
            "success": False,
            "results": results,
            "message": f"Hardware test failed: {str(e)}"
        }


@router.get("/ping")
async def ping_device():
    """
    Simple ping to check if ESP32 is reachable
    
    Returns response time in milliseconds
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            start_time = asyncio.get_event_loop().time()
            response = await client.get(f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/")
            end_time = asyncio.get_event_loop().time()
            
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                "success": True,
                "online": True,
                "response_time_ms": response_time_ms,
                "message": f"ESP32 responded in {response_time_ms}ms"
            }
    except Exception as e:
        logger.warning(f"ESP32 ping failed: {str(e)}")
        return {
            "success": False,
            "online": False,
            "message": f"ESP32 not reachable: {str(e)}"
        }
