# ESP32 Camera API Quick Reference

## 🚀 Quick Start for n8n

### Capture Image (Recommended for n8n)
```
GET http://127.0.0.1:8080/api/capture
```
Returns: `{ "success": true, "filename": "...", "size": 102400, "url": "..." }`

### List All Images
```
GET http://127.0.0.1:8080/api/images
```
Returns: `{ "images": [{ "filename": "...", "path": "...", "size": 102400, "modified": 1699651500 }] }`

### Rename Image
```
POST http://127.0.0.1:8080/api/rename
Content-Type: application/json

{ "old_name": "capture_20251110_184500_api.jpg", "new_label": "front_door" }
```
Returns: `{ "success": true, "new_name": "capture_20251110_184600_front_door.jpg" }`

### Delete Image
```
DELETE http://127.0.0.1:8080/api/delete/capture_20251110_184500_api.jpg
```
Returns: `{ "success": true }`

---

## 📸 Direct ESP32 Access

### Get Image Directly from Camera
```
GET http://10.0.0.30/capture
```
Returns: Binary JPEG image data

### View ESP32 Web Interface
```
GET http://10.0.0.30/
```
Returns: HTML page with live camera feed

---

## 🔧 n8n HTTP Request Node Settings

### For `/api/capture` endpoint:
- **Method:** GET
- **URL:** `http://127.0.0.1:8080/api/capture`
- **Response Format:** JSON
- **Authentication:** None

### For direct ESP32 image:
- **Method:** GET
- **URL:** `http://10.0.0.30/capture`
- **Response Format:** File
- **Download Binary File:** ✅ Yes
- **Binary Property:** `data`

---

## 💡 Common n8n Workflows

### 1. Scheduled Capture Every 5 Minutes
```
Schedule Trigger (*/5 * * * *) 
  → HTTP Request (GET /api/capture)
  → Set Node (extract filename)
```

### 2. Capture + AI Analysis + Auto-Label
```
Webhook Trigger
  → HTTP Request (GET /api/capture)
  → HTTP Request (download image)
  → OpenAI Vision (analyze image)
  → Function (create label from AI response)
  → HTTP Request (POST /api/rename)
```

### 3. Motion Detection Alert
```
Webhook (motion detected)
  → HTTP Request (GET /api/capture)
  → Send Email/Slack (with image URL)
```

---

## 🧪 Test Commands

```bash
# Capture new image
curl http://127.0.0.1:8080/api/capture

# List all images
curl http://127.0.0.1:8080/api/images

# Rename image
curl -X POST http://127.0.0.1:8080/api/rename \
  -H "Content-Type: application/json" \
  -d '{"old_name": "capture_20251110_184500_api.jpg", "new_label": "test"}'

# Delete image
curl -X DELETE http://127.0.0.1:8080/api/delete/capture_20251110_184500_api.jpg

# Get image directly from ESP32
curl http://10.0.0.30/capture -o test.jpg
```

---

## 🌐 URLs

- **Image Viewer:** http://127.0.0.1:8080
- **ESP32 Camera:** http://10.0.0.30
- **API Base:** http://127.0.0.1:8080/api

---

## 📝 Notes

- Server must be running: `python3 view_captures.py`
- Images saved to: `captures/` folder
- All API endpoints support CORS for cross-origin requests
- Binary image data available at: `http://127.0.0.1:8080/captures/{filename}`
