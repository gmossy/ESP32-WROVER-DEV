# ESP32 Camera System - FastAPI Backend

Modern REST API backend for ESP32 camera system with n8n integration, AI capabilities, and sensor management.

## 🚀 Features

- **Camera Control** - Capture, stream, and manage images
- **ESP32 Management** - Device status, diagnostics, and configuration
- **n8n Integration** - Workflow triggers and webhook management
- **AI Vision** - Image analysis and chat capabilities (OpenAI integration)
- **Sensor Support** - Motion sensors, LCD displays, and extensible sensor framework
- **RESTful API** - Clean, documented API with automatic OpenAPI/Swagger docs

## 📋 API Endpoints Overview

### Camera API (`/api/v1/camera`)
- `POST /capture` - Capture new image
- `GET /stream` - Live camera stream
- `GET /images` - List all captured images
- `GET /images/{filename}` - Get specific image
- `DELETE /images/{filename}` - Delete image
- `POST /images/{filename}/rename` - Rename image
- `GET /settings` - Get camera settings
- `POST /settings` - Update camera settings

### ESP32 Device API (`/api/v1/esp32`)
- `GET /status` - Device health check
- `GET /info` - Device information (chip, MAC, etc.)
- `GET /network` - Network information
- `GET /stats` - System statistics
- `POST /restart` - Restart device
- `POST /test` - Run hardware diagnostics
- `GET /ping` - Simple connectivity check

### n8n Integration API (`/api/v1/n8n`)
- `GET /status` - n8n server status
- `GET /workflows` - List all workflows
- `GET /workflows/{id}` - Get workflow details
- `POST /workflows/{id}/activate` - Activate workflow
- `POST /workflows/{id}/deactivate` - Deactivate workflow
- `POST /trigger/camera-capture` - Trigger camera workflow
- `POST /trigger/motion-detected` - Trigger motion workflow
- `POST /webhook/{name}` - Send custom webhook
- `GET /executions` - List workflow executions

### Sensors API (`/api/v1/sensors`)
- `GET /status` - All sensors status
- `POST /motion/event` - Record motion event
- `GET /motion/events` - Get motion events
- `DELETE /motion/events` - Clear motion events
- `POST /lcd/display` - Display message on LCD
- `POST /lcd/clear` - Clear LCD screen
- `POST /reading` - Record sensor reading
- `GET /readings/{sensor_id}` - Get sensor readings
- `GET /list` - List all sensors
- `POST /configure` - Configure sensor

### AI/Chat API (`/api/v1/ai`)
- `POST /analyze-image` - Analyze image with AI vision
- `POST /chat` - Chat with AI assistant
- `POST /label-image` - Auto-generate image label
- `POST /detect-objects` - Detect objects in image
- `GET /models` - List available AI models

## 🛠️ Setup

### Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export ESP32_IP=10.0.0.30
export N8N_URL=http://localhost:5678
export OPENAI_API_KEY=your_key_here  # Optional

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build and run with docker-compose
cd n8n
docker-compose up -d backend

# View logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health
```

## 📖 API Documentation

Once running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔧 Configuration

Environment variables:

```bash
# API Settings
ENVIRONMENT=production
API_V1_STR=/api/v1

# ESP32 Configuration
ESP32_IP=10.0.0.30
ESP32_PORT=80
ESP32_TIMEOUT=10

# n8n Configuration
N8N_URL=http://n8n:5678
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=changeme123

# Storage
CAPTURE_DIR=/app/captures

# AI Configuration (Optional)
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-4-vision-preview

# Sensor Configuration
MOTION_SENSOR_ENABLED=false
LCD_SCREEN_ENABLED=false
```

## 📝 Example Usage

### Capture Image

```bash
curl -X POST "http://localhost:8000/api/v1/camera/capture?save=true&label=test" \
  -H "accept: application/json"
```

### Check ESP32 Status

```bash
curl "http://localhost:8000/api/v1/esp32/status"
```

### Trigger n8n Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/n8n/trigger/camera-capture" \
  -H "Content-Type: application/json" \
  -d '{"label": "motion_detected", "metadata": {"confidence": 0.95}}'
```

### Record Motion Event

```bash
curl -X POST "http://localhost:8000/api/v1/sensors/motion/event" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "pir_1", "confidence": 0.9}'
```

### Analyze Image with AI

```bash
curl -X POST "http://localhost:8000/api/v1/ai/analyze-image" \
  -H "Content-Type: application/json" \
  -d '{"filename": "capture_20241112_120000.jpg", "prompt": "What objects are visible?"}'
```

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── logging_config.py  # Logging setup
│   ├── api/
│   │   └── v1/
│   │       ├── api.py         # API router
│   │       └── endpoints/
│   │           ├── camera.py  # Camera endpoints
│   │           ├── esp32.py   # ESP32 endpoints
│   │           ├── n8n.py     # n8n endpoints
│   │           ├── sensors.py # Sensor endpoints
│   │           └── ai_chat.py # AI endpoints
│   └── models/
│       ├── camera.py          # Camera models
│       ├── esp32.py           # ESP32 models
│       ├── n8n.py             # n8n models
│       ├── sensors.py         # Sensor models
│       └── ai.py              # AI models
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔌 Extending with New Sensors

Add new sensor types easily:

```python
# In sensors.py
@router.post("/temperature/reading")
async def record_temperature(
    sensor_id: str,
    temperature_c: float,
    humidity_percent: Optional[float] = None
):
    reading = SensorReading(
        sensor_id=sensor_id,
        sensor_type="temperature",
        value=temperature_c,
        unit="celsius",
        timestamp=datetime.now().isoformat(),
        metadata={"humidity": humidity_percent}
    )
    # Store and process...
    return {"success": True, "reading": reading.dict()}
```

## 🧪 Testing

```bash
# Test ESP32 connectivity
curl http://localhost:8000/api/v1/esp32/ping

# Test camera capture
curl -X POST http://localhost:8000/api/v1/camera/capture

# Test n8n connection
curl http://localhost:8000/api/v1/n8n/status

# Run hardware test
curl -X POST http://localhost:8000/api/v1/esp32/test
```

## 📊 Health Monitoring

The backend includes health checks every 10 seconds:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:8000/health
```

## 🔐 Security Notes

- Use environment variables for sensitive data
- Enable authentication for production deployments
- Use HTTPS in production
- Restrict CORS origins appropriately
- Keep API keys secure (especially OPENAI_API_KEY)

## 🤝 Integration with n8n

The backend is designed to work seamlessly with n8n workflows:

1. **Webhook Triggers** - Send events to n8n workflows
2. **Workflow Management** - Activate/deactivate workflows via API
3. **Execution Monitoring** - Track workflow runs
4. **Custom Webhooks** - Flexible webhook system

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [n8n Documentation](https://docs.n8n.io/)
- [![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

**Built with ❤️ for ESP32 Camera System**
