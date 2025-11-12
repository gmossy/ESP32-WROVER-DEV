"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    PROJECT_NAME: str = "ESP32 Camera System API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
    ]
    
    # ESP32 Configuration
    ESP32_IP: str = os.getenv("ESP32_IP", "10.0.0.30")
    ESP32_PORT: int = int(os.getenv("ESP32_PORT", "80"))
    ESP32_TIMEOUT: int = int(os.getenv("ESP32_TIMEOUT", "10"))
    
    # n8n Configuration
    N8N_URL: str = os.getenv("N8N_URL", "http://n8n:5678")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")
    N8N_BASIC_AUTH_USER: str = os.getenv("N8N_BASIC_AUTH_USER", "admin")
    N8N_BASIC_AUTH_PASSWORD: str = os.getenv("N8N_BASIC_AUTH_PASSWORD", "changeme123")
    
    # Storage
    CAPTURE_DIR: str = os.getenv("CAPTURE_DIR", "/app/captures")
    MAX_CAPTURE_SIZE_MB: int = 10
    
    # AI/LLM Configuration (for future AI chat integration)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4-vision-preview")
    
    # Sensor Configuration
    MOTION_SENSOR_ENABLED: bool = os.getenv("MOTION_SENSOR_ENABLED", "false").lower() == "true"
    LCD_SCREEN_ENABLED: bool = os.getenv("LCD_SCREEN_ENABLED", "false").lower() == "true"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
