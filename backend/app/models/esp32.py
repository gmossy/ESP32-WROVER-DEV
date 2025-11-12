"""
ESP32 device models
"""
from pydantic import BaseModel
from typing import Optional


class DeviceStatus(BaseModel):
    """ESP32 device status"""
    online: bool
    ip_address: str
    response_time_ms: Optional[int] = None
    http_status: Optional[int] = None
    message: str


class DeviceInfo(BaseModel):
    """ESP32 device information"""
    chip_model: str
    chip_revision: str
    mac_address: str
    flash_size_mb: int
    psram_size_mb: int
    cpu_frequency_mhz: int
    firmware_version: str


class NetworkInfo(BaseModel):
    """ESP32 network information"""
    ssid: str
    ip_address: str
    gateway: str
    subnet: str
    rssi: int
    connected: bool


class SystemStats(BaseModel):
    """ESP32 system statistics"""
    uptime_seconds: int
    free_heap_bytes: int
    total_heap_bytes: int
    cpu_usage_percent: int
    temperature_celsius: float
