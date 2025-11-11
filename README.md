# 📷 ESP32-WROVER-DEV Camera Web Server

> **Built by Glenn Mossy** 🚀  
> Turn your ESP32-WROVER-DEV into a powerful IoT camera with web interface, API endpoints, and n8n automation!

[![ESP32](https://img.shields.io/badge/ESP32-WROVER--DEV-blue.svg)](https://www.espressif.com/)
[![Arduino](https://img.shields.io/badge/Arduino-Compatible-green.svg)](https://www.arduino.cc/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## 🎯 What is This?

This is a complete camera system running on the **Freenove ESP32-WROVER-DEV** board with built-in camera module. It's like having a smart security camera that you can control with code, automate with workflows, and integrate with AI services!

Think of it as your personal IoT camera that can:
- �� Capture images on demand or on schedule
- 🤖 Integrate with n8n for automation workflows
- 🧠 Send images to AI services for analysis
- 🏷️ Auto-label images based on content
- 📊 Track motion, visitors, or any visual events
- 🌐 Access from anywhere on your network

### ✨ Features That'll Make You Smile

- 📸 **Live Camera Feed** - See what your ESP32 sees in real-time
- 🌐 **Web Interface** - Beautiful gallery to view, rename, and delete images
- 🤖 **API Endpoints** - Perfect for n8n automation and AI integration
- 💾 **Auto-Save Images** - Captures stored with timestamps
- 🏷️ **Smart Labeling** - Rename images with custom labels
- ⚡ **Low Power Mode** - Optimized for battery operation
- 🔄 **Auto-Refresh** - Live feed updates every 5 seconds
- 🗑️ **Image Management** - Delete unwanted captures with one click
- 📡 **RESTful API** - JSON responses for easy integration

## 🛠️ Hardware You'll Need

- **Freenove ESP32-WROVER-DEV Board** with built-in camera (OV2640)
  - ESP32-D0WD-V3 chip (revision v3.0)
  - Wi-Fi, BT 5 (LE), Dual Core + LP Core, 240MHz
  - 4MB Flash, PSRAM support
  - Built-in OV2640 camera module
- USB cable (for programming and power)
- WiFi network (2.4GHz - ESP32 doesn't support 5GHz)
- Computer with Arduino IDE or arduino-cli

## 🚀 Quick Start (5 Minutes to Camera Bliss!)

### 1. Install ESP32 Board Support

```bash
arduino-cli core install esp32:esp32
```

### 2. Clone This Repository

```bash
git clone https://github.com/gmossy/ESP32-WROVER-DEV.git
cd ESP32-WROVER-DEV
```

### 3. Configure WiFi Credentials

Edit `camera_webserver/camera_webserver.ino`:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 4. Upload the Camera Sketch

```bash
cd camera_webserver
arduino-cli compile --fqbn esp32:esp32:esp32wrover .
arduino-cli upload --fqbn esp32:esp32:esp32wrover --port /dev/cu.usbserial-143130 --upload-property upload.speed=115200 .
```

> **Note:** Replace `/dev/cu.usbserial-143130` with your actual port. Find it with: `arduino-cli board list`

### 5. Start the Image Viewer

```bash
python3 view_captures.py
```

### 6. Open Your Browser

- **Camera Interface:** <http://10.0.0.30>
- **Image Gallery:** <http://127.0.0.1:8080>

**That's it!** You're now running a full-featured camera system! 🎉

## 📸 Using the Camera

### Web Interface

The image gallery at <http://127.0.0.1:8080> provides:

- **Live Feed**: Auto-refreshing camera view
- **Image Gallery**: All captured images with metadata
- **Rename**: Click 🏷️ to add custom labels
- **Delete**: Click 🗑️ to remove images
- **Full Screen**: Click any image to view full-size

### API Endpoints

Perfect for automation and integration:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/capture` | GET | Capture & save new image |
| `/api/images` | GET | List all images with metadata |
| `/api/rename` | POST | Rename/relabel an image |
| `/api/delete/{filename}` | DELETE | Delete specific image |

### Command Line

```bash
# Capture image
curl http://127.0.0.1:8080/api/capture

# List all images
curl http://127.0.0.1:8080/api/images

# Get image directly from ESP32
curl http://10.0.0.30/capture -o image.jpg
```

## 🤖 n8n Automation

This project is designed to work seamlessly with n8n workflows!

### Example Workflows

#### 1. Scheduled Capture Every 5 Minutes

```
Schedule Trigger (*/5 * * * *)
  ↓
HTTP Request (GET /api/capture)
  ↓
Set Node (extract filename)
```

#### 2. AI-Powered Auto-Labeling

```
Webhook Trigger
  ↓
HTTP Request (GET /api/capture)
  ↓
HTTP Request (download image)
  ↓
OpenAI Vision (analyze image)
  ↓
Function (create label)
  ↓
HTTP Request (POST /api/rename)
```

#### 3. Motion Detection Alert

```
Webhook (motion sensor)
  ↓
HTTP Request (GET /api/capture)
  ↓
Send Email/Slack (with image)
```

**See [n8n/N8N_INTEGRATION.md](n8n/N8N_INTEGRATION.md) for complete guide!**

## 📁 Project Structure

```text
ESP32-WROVER-DEV/
├── README.md                    # You are here!
├── CONFIGURATION.md             # WiFi credentials setup guide
├── API_QUICK_REFERENCE.md       # Quick API reference
├── Makefile                     # Build automation
├── camera_webserver/
│   └── camera_webserver.ino    # Main camera sketch
├── low_power_webserver/
│   └── low_power_webserver.ino # Power-optimized version
├── n8n/                        # Docker & n8n automation
│   ├── README.md               # Docker setup guide
│   ├── N8N_INTEGRATION.md      # n8n integration guide
│   ├── docker-compose.yml      # Docker services
│   └── Dockerfile.viewer       # Image viewer container
├── view_captures.py            # Image gallery web server
├── test.py                     # Diagnostic & testing script
├── generate_config.py          # Config generator from .env
└── captures/                   # Saved images folder
```

## 🔧 Configuration

### WiFi Settings

Edit the sketch to match your network:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Static IP (optional)
IPAddress local_IP(10, 0, 0, 30);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);
```

### Camera Settings

Adjust image quality and resolution:

```cpp
config.frame_size = FRAMESIZE_UXGA;  // Resolution
config.jpeg_quality = 10;            // Quality (10=high, 63=low)
config.fb_count = 2;                 // Frame buffers
```

Available resolutions:
- `FRAMESIZE_UXGA` (1600x1200) - Highest quality
- `FRAMESIZE_SVGA` (800x600) - Balanced
- `FRAMESIZE_VGA` (640x480) - Lower bandwidth
- `FRAMESIZE_QVGA` (320x240) - Fastest

### Server Port

Change the Python server port in `view_captures.py`:

```python
PORT = 8080  # Change to your preferred port
```

## 🧪 Testing & Diagnostics

### Run Comprehensive Tests

```bash
python3 test.py
```

This will test:
- ✅ ESP32 port detection
- ✅ Network connectivity (ping)
- ✅ TCP port 80 status
- ✅ HTTP requests
- ✅ Camera image capture
- ✅ Serial monitor output

### Manual Tests

```bash
# Test camera directly
curl http://10.0.0.30/capture -o test.jpg

# Check if image viewer is running
curl http://127.0.0.1:8080/api/images

# Monitor serial output
arduino-cli monitor -p /dev/cu.usbserial-143130 -c baudrate=115200
```

## 🎓 Learning Resources

### Understanding the Code

**Camera Initialization** (`camera_webserver.ino`):
```cpp
void setupCamera() {
  camera_config_t config;
  // Configure camera pins for Freenove WROVER
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  // ... more pin configurations
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
  }
}
```

**Image Capture** (`camera_webserver.ino`):
```cpp
void handleCapture() {
  camera_fb_t * fb = esp_camera_fb_get();  // Get frame buffer
  if(!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  // Send JPEG data
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  esp_camera_fb_return(fb);  // Return buffer
}
```

**API Endpoint** (`view_captures.py`):
```python
def do_GET(self):
    if self.path == '/api/capture':
        # Capture from ESP32
        req = urllib.request.Request('http://10.0.0.30/capture')
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
            # Save with timestamp
            filename = f"capture_{timestamp}_api.jpg"
            with open(filename, 'wb') as f:
                f.write(image_data)
```

### Key Concepts

1. **Frame Buffer**: Temporary memory holding camera image
2. **JPEG Compression**: Reduces image size for transmission
3. **Static IP**: Fixed address for reliable access
4. **RESTful API**: Standard HTTP methods for operations
5. **CORS Headers**: Allow cross-origin requests

## 🐛 Troubleshooting

### Camera Not Initializing

**Error:** `Camera init failed with error 0x...`

**Solutions:**
- Check camera ribbon cable connection
- Verify pin configuration matches your board
- Try different frame size (SVGA instead of UXGA)
- Check if PSRAM is detected: `psramFound()`

### WiFi Not Connecting

**Error:** `WiFi connection failed`

**Solutions:**
- Verify SSID and password are correct
- Ensure using 2.4GHz network (not 5GHz)
- Check WiFi signal strength
- Try without static IP first
- Monitor serial output for details

### Upload Fails

**Error:** `Could not open port` or `chip stopped responding`

**Solutions:**
- Hold BOOT button while uploading
- Use slower baud rate: `--upload-property upload.speed=115200`
- Try different USB cable
- Check port with: `arduino-cli board list`
- Erase flash first: `esptool --port /dev/cu.usbserial-143130 erase_flash`

### Images Not Saving

**Solutions:**
- Check `captures/` folder exists and is writable
- Verify ESP32 is accessible: `ping 10.0.0.30`
- Check Python server is running
- Look for errors in server output

### Browser Can't Connect

**Solutions:**
- Use `http://` not `https://`
- Disable browser HTTPS-only mode
- Try different browser or incognito mode
- Check firewall settings
- Verify server is running: `curl http://127.0.0.1:8080`

## 🔒 Security Notes

- **Local Network Only**: Server runs on localhost by default
- **No Authentication**: Add API keys for production use
- **Plain HTTP**: Use reverse proxy with SSL for public access
- **Firewall**: Restrict access to trusted devices
- **Credentials**: Don't commit WiFi passwords to public repos!

## 🚀 Advanced Usage

### Custom Image Processing

Add image processing in `view_captures.py`:

```python
from PIL import Image
import io

def process_image(image_data):
    img = Image.open(io.BytesIO(image_data))
    # Resize, filter, or analyze
    img = img.resize((640, 480))
    return img
```

### Webhook Integration

Trigger captures from external services:

```bash
curl -X POST http://your-n8n-server:5678/webhook/esp32-capture
```

### Database Storage

Store image metadata in SQLite:

```python
import sqlite3

conn = sqlite3.connect('images.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        filename TEXT,
        timestamp REAL,
        label TEXT,
        size INTEGER
    )
''')
```

## 📊 Performance

- **Image Capture Time**: ~500ms
- **JPEG Compression**: 10-15x reduction
- **Typical Image Size**: 80-120KB
- **Network Latency**: 50-200ms (local network)
- **Power Consumption**: 
  - Active (WiFi + Camera): ~300mA
  - Low Power Mode: ~150mA
  - Deep Sleep: ~10μA

## 🤝 Contributing

Found a bug? Have an idea? Contributions welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Espressif** for the amazing ESP32 platform
- **Freenove** for the WROVER-DEV board
- **Arduino** community for libraries and support
- **n8n** for workflow automation inspiration

## 📧 Contact

**Glenn Mossy**
- GitHub: [@gmossy](https://github.com/gmossy)

## 🌟 Star This Repo!

If you found this project helpful, please give it a star! ⭐

It helps others discover this project and motivates me to create more awesome IoT projects!

---

**Happy Coding!** 🚀📷

*Built with ❤️ by Glenn Mossy*
