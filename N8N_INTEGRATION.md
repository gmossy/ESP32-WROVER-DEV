# n8n Integration Guide for ESP32 Camera

This guide explains how to integrate your ESP32 camera with n8n for automated image capture and processing.

## API Endpoints

The `view_captures.py` server provides the following API endpoints for n8n integration:

### 1. Capture Image from ESP32
**Endpoint:** `GET http://127.0.0.1:8080/api/capture`

**Description:** Triggers the ESP32 camera to capture a new image and saves it to the captures folder.

**Response:**
```json
{
  "success": true,
  "filename": "captures/capture_20251110_184500_api.jpg",
  "size": 102400,
  "url": "http://127.0.0.1:8080/captures/capture_20251110_184500_api.jpg"
}
```

**n8n HTTP Request Node Configuration:**
- **Method:** GET
- **URL:** `http://127.0.0.1:8080/api/capture`
- **Response Format:** JSON

---

### 2. List All Captured Images
**Endpoint:** `GET http://127.0.0.1:8080/api/images`

**Description:** Returns a list of all captured images with metadata.

**Response:**
```json
{
  "images": [
    {
      "filename": "capture_20251110_184500_api.jpg",
      "path": "captures/capture_20251110_184500_api.jpg",
      "size": 102400,
      "modified": 1699651500.123456
    }
  ]
}
```

**n8n HTTP Request Node Configuration:**
- **Method:** GET
- **URL:** `http://127.0.0.1:8080/api/images`
- **Response Format:** JSON

---

### 3. Rename/Relabel Image
**Endpoint:** `POST http://127.0.0.1:8080/api/rename`

**Description:** Renames an image with a custom label.

**Request Body:**
```json
{
  "old_name": "capture_20251110_184500_api.jpg",
  "new_label": "front_door_visitor"
}
```

**Response:**
```json
{
  "success": true,
  "new_name": "capture_20251110_184600_front_door_visitor.jpg"
}
```

**n8n HTTP Request Node Configuration:**
- **Method:** POST
- **URL:** `http://127.0.0.1:8080/api/rename`
- **Body Content Type:** JSON
- **Body:** Use expression to pass old_name and new_label

---

### 4. Delete Image
**Endpoint:** `DELETE http://127.0.0.1:8080/api/delete/{filename}`

**Description:** Deletes a specific image.

**Example:** `DELETE http://127.0.0.1:8080/api/delete/capture_20251110_184500_api.jpg`

**Response:**
```json
{
  "success": true
}
```

**n8n HTTP Request Node Configuration:**
- **Method:** DELETE
- **URL:** `http://127.0.0.1:8080/api/delete/{{ $json.filename }}`
- **Response Format:** JSON

---

## n8n Workflow Examples

### Example 1: Scheduled Image Capture
**Use Case:** Capture an image every 5 minutes

**Workflow:**
1. **Schedule Trigger** (Cron: `*/5 * * * *`)
2. **HTTP Request** → GET `http://127.0.0.1:8080/api/capture`
3. **Set Node** → Extract filename from response
4. **Send Email/Notification** (optional)

### Example 2: Motion Detection Workflow
**Use Case:** Capture image when motion is detected, analyze with AI, and label

**Workflow:**
1. **Webhook Trigger** → Receives motion detection event
2. **HTTP Request** → GET `http://127.0.0.1:8080/api/capture`
3. **HTTP Request** → Download image from URL in response
4. **OpenAI Vision Node** → Analyze image content
5. **HTTP Request** → POST to `/api/rename` with AI-generated label
6. **Send Notification** → Alert with image analysis

### Example 3: Periodic Cleanup
**Use Case:** Delete images older than 7 days

**Workflow:**
1. **Schedule Trigger** (Daily at midnight)
2. **HTTP Request** → GET `http://127.0.0.1:8080/api/images`
3. **Function Node** → Filter images older than 7 days
4. **Split In Batches** → Process images one by one
5. **HTTP Request** → DELETE each old image

---

## Direct ESP32 Integration (Alternative)

If you want n8n to directly communicate with the ESP32 without the Python server:

### Capture Image Directly from ESP32
**Endpoint:** `GET http://10.0.0.30/capture`

**Description:** Returns JPEG image data directly from ESP32 camera.

**n8n HTTP Request Node Configuration:**
- **Method:** GET
- **URL:** `http://10.0.0.30/capture`
- **Response Format:** File (Binary)
- **Download Binary File:** Yes
- **Binary Property:** `data`

**Save Image to Disk:**
Add a **Write Binary File** node after the HTTP Request:
- **File Name:** `{{ $now.format('YYYYMMDDHHmmss') }}_capture.jpg`
- **Binary Property:** `data`

---

## Example n8n Workflow JSON

### Simple Capture Workflow

```json
{
  "name": "ESP32 Camera Capture",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "minutes",
              "minutesInterval": 5
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://127.0.0.1:8080/api/capture",
        "options": {}
      },
      "name": "Capture Image",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "filename",
              "value": "={{ $json.filename }}"
            },
            {
              "name": "image_url",
              "value": "={{ $json.url }}"
            }
          ]
        }
      },
      "name": "Extract Data",
      "type": "n8n-nodes-base.set",
      "position": [650, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Capture Image",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Capture Image": {
      "main": [
        [
          {
            "node": "Extract Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Advanced: AI-Powered Image Labeling

### Workflow with OpenAI Vision

1. **HTTP Request** → Capture image
2. **HTTP Request** → Download image as binary
3. **OpenAI Vision Node:**
   - **Model:** gpt-4-vision-preview
   - **Prompt:** "Describe what you see in this image in 3-5 words"
   - **Image:** Use binary data from previous step
4. **Function Node** → Clean up AI response to create label
5. **HTTP Request** → POST to `/api/rename` with AI label

**Function Node Code:**
```javascript
// Clean up AI response to create a valid filename label
const aiDescription = $input.first().json.response;
const label = aiDescription
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .substring(0, 50);

return [{
  json: {
    old_name: $('Capture Image').first().json.filename.split('/').pop(),
    new_label: label
  }
}];
```

---

## Webhook Integration

To trigger image capture from external services:

### Setup Webhook in n8n
1. Add **Webhook** node
2. Set **HTTP Method:** GET or POST
3. Set **Path:** `/capture-esp32`
4. Connect to **HTTP Request** node (capture endpoint)

**Webhook URL:** `http://your-n8n-server:5678/webhook/capture-esp32`

**Usage:**
```bash
curl http://your-n8n-server:5678/webhook/capture-esp32
```

---

## Testing API Endpoints

### Using curl

**Capture Image:**
```bash
curl http://127.0.0.1:8080/api/capture
```

**List Images:**
```bash
curl http://127.0.0.1:8080/api/images
```

**Rename Image:**
```bash
curl -X POST http://127.0.0.1:8080/api/rename \
  -H "Content-Type: application/json" \
  -d '{"old_name": "capture_20251110_184500_api.jpg", "new_label": "test_label"}'
```

**Delete Image:**
```bash
curl -X DELETE http://127.0.0.1:8080/api/delete/capture_20251110_184500_api.jpg
```

---

## Security Considerations

1. **Local Network Only:** The server runs on `127.0.0.1` (localhost) by default
2. **Expose to Network:** To allow n8n on another machine to access:
   - Change `PORT` binding in `view_captures.py` from `127.0.0.1` to `0.0.0.0`
   - Use firewall rules to restrict access
3. **Authentication:** Consider adding API key authentication for production use
4. **HTTPS:** Use reverse proxy (nginx) with SSL for secure connections

---

## Troubleshooting

### n8n Can't Connect
- Ensure `view_captures.py` is running
- Check firewall settings
- Verify IP address and port
- Test with curl first

### Images Not Saving
- Check `captures/` directory permissions
- Verify ESP32 is accessible at `10.0.0.30`
- Check ESP32 serial output for errors

### Binary Data Issues
- Use "Download Binary File" option in HTTP Request node
- Set correct binary property name
- Use Write Binary File node to save

---

## Support

For issues or questions:
1. Check ESP32 serial monitor: `arduino-cli monitor -p /dev/cu.usbserial-143130 -c baudrate=115200`
2. Check Python server logs
3. Test API endpoints with curl
4. Verify ESP32 camera is accessible: `curl http://10.0.0.30/capture -o test.jpg`
