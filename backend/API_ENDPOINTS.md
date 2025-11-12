# FastAPI Backend - Complete API Endpoints Reference

Base URL: `http://localhost:8000`  
API Version: `/api/v1`

## 📸 Camera Endpoints

### POST `/api/v1/camera/capture`
**Capture new image from ESP32 camera**

**Query Parameters:**
- `save` (boolean): Save image to disk (default: true)
- `label` (string, optional): Custom label for filename

**Response:**
```json
{
  "success": true,
  "filename": "capture_20241112_120000_motion.jpg",
  "filepath": "/app/captures/capture_20241112_120000_motion.jpg",
  "size_bytes": 75432,
  "timestamp": "20241112_120000",
  "message": "Image captured successfully"
}
```

### GET `/api/v1/camera/stream`
**Live camera stream (MJPEG)**

Returns continuous JPEG stream from camera.

### GET `/api/v1/camera/images`
**List all captured images**

**Query Parameters:**
- `limit` (int): Max images to return (1-500, default: 50)
- `offset` (int): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "filename": "capture_20241112_120000.jpg",
    "filepath": "/app/captures/capture_20241112_120000.jpg",
    "size_bytes": 75432,
    "created_at": "2024-11-12T12:00:00",
    "modified_at": "2024-11-12T12:00:00"
  }
]
```

### GET `/api/v1/camera/images/{filename}`
**Get specific image file**

Returns the image file (JPEG).

### DELETE `/api/v1/camera/images/{filename}`
**Delete an image**

**Response:**
```json
{
  "success": true,
  "message": "Image capture_20241112_120000.jpg deleted successfully"
}
```

### POST `/api/v1/camera/images/{filename}/rename`
**Rename/relabel an image**

**Body:**
```json
{
  "new_label": "front_door_visitor"
}
```

---

## 🔧 ESP32 Device Endpoints

### GET `/api/v1/esp32/status`
**Get device status and health**

**Response:**
```json
{
  "online": true,
  "ip_address": "10.0.0.30",
  "response_time_ms": 45,
  "http_status": 200,
  "message": "ESP32 is online and responding"
}
```

### GET `/api/v1/esp32/info`
**Get device information**

**Response:**
```json
{
  "chip_model": "ESP32-D0WD-V3",
  "chip_revision": "v3.0",
  "mac_address": "94:e6:86:4b:e3:90",
  "flash_size_mb": 4,
  "psram_size_mb": 8,
  "cpu_frequency_mhz": 240,
  "firmware_version": "1.0.0"
}
```

### GET `/api/v1/esp32/network`
**Get network information**

**Response:**
```json
{
  "ssid": "FOOTBALL",
  "ip_address": "10.0.0.30",
  "gateway": "10.0.0.1",
  "subnet": "255.255.255.0",
  "rssi": -45,
  "connected": true
}
```

### GET `/api/v1/esp32/stats`
**Get system statistics**

**Response:**
```json
{
  "uptime_seconds": 3600,
  "free_heap_bytes": 270556,
  "total_heap_bytes": 327680,
  "cpu_usage_percent": 25,
  "temperature_celsius": 45.5
}
```

### POST `/api/v1/esp32/restart`
**Restart the ESP32 device**

**Response:**
```json
{
  "success": true,
  "message": "ESP32 restart command sent. Device will be offline for ~10 seconds."
}
```

### POST `/api/v1/esp32/test`
**Run comprehensive hardware test**

**Response:**
```json
{
  "success": true,
  "results": {
    "connectivity": true,
    "camera": true,
    "led": true,
    "memory": true,
    "overall": true
  },
  "message": "Hardware test completed"
}
```

### GET `/api/v1/esp32/ping`
**Simple ping test**

**Response:**
```json
{
  "success": true,
  "online": true,
  "response_time_ms": 23,
  "message": "ESP32 responded in 23ms"
}
```

---

## 🤖 n8n Integration Endpoints

### GET `/api/v1/n8n/status`
**Check n8n server status**

**Response:**
```json
{
  "online": true,
  "url": "http://n8n:5678",
  "status_code": 200,
  "message": "n8n is online and responding"
}
```

### GET `/api/v1/n8n/workflows`
**List all workflows**

**Response:**
```json
{
  "success": true,
  "count": 5,
  "workflows": [...]
}
```

### POST `/api/v1/n8n/workflows/{workflow_id}/activate`
**Activate a workflow**

### POST `/api/v1/n8n/workflows/{workflow_id}/deactivate`
**Deactivate a workflow**

### POST `/api/v1/n8n/trigger/camera-capture`
**Trigger camera capture workflow**

**Body:**
```json
{
  "label": "motion_detected",
  "metadata": {
    "sensor_id": "pir_1",
    "confidence": 0.95
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Camera capture workflow triggered",
  "payload": {...}
}
```

### POST `/api/v1/n8n/trigger/motion-detected`
**Trigger motion detection workflow**

**Body:**
```json
{
  "sensor_id": "pir_1",
  "confidence": 0.9,
  "metadata": {}
}
```

### POST `/api/v1/n8n/webhook/{webhook_name}`
**Send custom webhook to n8n**

**Body:** Any JSON payload

---

## 🔬 Sensors Endpoints

### GET `/api/v1/sensors/status`
**Get status of all sensors**

**Response:**
```json
{
  "motion_sensor": {
    "enabled": true,
    "status": "active",
    "events_count": 42
  },
  "lcd_screen": {
    "enabled": true,
    "status": "active"
  }
}
```

### POST `/api/v1/sensors/motion/event`
**Record motion detection event**

**Body:**
```json
{
  "sensor_id": "pir_1",
  "confidence": 0.95,
  "metadata": {
    "location": "front_door"
  }
}
```

**Response:**
```json
{
  "success": true,
  "event": {...},
  "message": "Motion event recorded"
}
```

### GET `/api/v1/sensors/motion/events`
**Get motion events**

**Query Parameters:**
- `limit` (int): Max events (default: 50)
- `sensor_id` (string, optional): Filter by sensor

**Response:**
```json
{
  "count": 42,
  "events": [...]
}
```

### DELETE `/api/v1/sensors/motion/events`
**Clear all motion events**

### POST `/api/v1/sensors/lcd/display`
**Display message on LCD screen**

**Body:**
```json
{
  "text": "Motion Detected!",
  "line": 1,
  "duration_seconds": 5
}
```

### POST `/api/v1/sensors/lcd/clear`
**Clear LCD screen**

### POST `/api/v1/sensors/reading`
**Record generic sensor reading**

**Body:**
```json
{
  "sensor_id": "temp_1",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "metadata": {
    "humidity": 65.2
  }
}
```

### GET `/api/v1/sensors/readings/{sensor_id}`
**Get readings from specific sensor**

**Query Parameters:**
- `limit` (int): Max readings (default: 100)

### GET `/api/v1/sensors/list`
**List all registered sensors**

**Response:**
```json
{
  "count": 3,
  "sensors": [
    {
      "id": "motion_sensor_1",
      "type": "motion",
      "status": "active",
      "events_count": 42
    },
    {
      "id": "temp_1",
      "type": "temperature",
      "status": "active",
      "readings_count": 150,
      "latest_value": "23.5 celsius"
    }
  ]
}
```

### POST `/api/v1/sensors/configure`
**Configure a sensor**

**Body:**
```json
{
  "sensor_id": "pir_1",
  "sensor_type": "motion",
  "config": {
    "sensitivity": 0.8,
    "cooldown_seconds": 10
  }
}
```

---

## 🧠 AI/Chat Endpoints

### POST `/api/v1/ai/analyze-image`
**Analyze image with AI vision**

**Body:**
```json
{
  "filename": "capture_20241112_120000.jpg",
  "prompt": "What objects are visible in this image?"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "description": "The image shows a camera device...",
    "objects_detected": ["camera", "device"],
    "confidence": 0.85,
    "tags": ["technology", "electronics"]
  },
  "prompt": "What objects are visible?",
  "model": "gpt-4-vision-preview",
  "message": "Image analyzed successfully"
}
```

### POST `/api/v1/ai/chat`
**Chat with AI assistant**

**Body:**
```json
{
  "message": "What was captured in the last image?",
  "include_latest_image": true,
  "context": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on the latest image, I can see...",
  "model": "gpt-4-vision-preview",
  "message": "Chat response generated"
}
```

### POST `/api/v1/ai/label-image`
**Auto-generate label for image**

**Body:**
```json
{
  "filename": "capture_20241112_120000.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "filename": "capture_20241112_120000.jpg",
  "suggested_label": "front_door_visitor",
  "confidence": 0.85,
  "message": "Label generated successfully"
}
```

### POST `/api/v1/ai/detect-objects`
**Detect objects in image**

**Body:**
```json
{
  "filename": "capture_20241112_120000.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "filename": "capture_20241112_120000.jpg",
  "detections": [
    {
      "object": "person",
      "confidence": 0.92,
      "bbox": [100, 100, 200, 300]
    }
  ],
  "count": 1,
  "message": "Objects detected successfully"
}
```

### GET `/api/v1/ai/models`
**List available AI models**

**Response:**
```json
{
  "current_model": "gpt-4-vision-preview",
  "available_models": [
    "gpt-4-vision-preview",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo"
  ],
  "configured": true
}
```

---

## 🏥 System Endpoints

### GET `/health`
**Health check endpoint**

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### GET `/`
**Root endpoint**

**Response:**
```json
{
  "message": "ESP32 Camera System API",
  "version": "1.0.0",
  "docs": "/docs",
  "api": "/api/v1"
}
```

---

## 📚 Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentication

Currently, the API does not require authentication. For production:

1. Add API key authentication
2. Implement JWT tokens
3. Use OAuth2 for user authentication
4. Enable HTTPS

---

## 🚀 Quick Start Examples

### Capture and Analyze
```bash
# 1. Capture image
curl -X POST "http://localhost:8000/api/v1/camera/capture?label=test"

# 2. Analyze with AI
curl -X POST "http://localhost:8000/api/v1/ai/analyze-image" \
  -H "Content-Type: application/json" \
  -d '{"filename": "capture_20241112_120000_test.jpg"}'
```

### Motion Detection Workflow
```bash
# 1. Record motion event
curl -X POST "http://localhost:8000/api/v1/sensors/motion/event" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "pir_1", "confidence": 0.9}'

# 2. Trigger n8n workflow
curl -X POST "http://localhost:8000/api/v1/n8n/trigger/motion-detected" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "pir_1", "confidence": 0.9}'

# 3. Capture image
curl -X POST "http://localhost:8000/api/v1/camera/capture?label=motion"
```

---

**For complete documentation, visit: http://localhost:8000/docs**
