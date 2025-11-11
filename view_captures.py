#!/usr/bin/env python3
"""
Simple web server to view captured images from ESP32 camera
Supports image deletion, relabeling, and API endpoints for n8n integration
"""

import http.server
import socketserver
import os
import json
import urllib.parse
import shutil
from pathlib import Path
from datetime import datetime

PORT = int(os.getenv('PORT', 8080))
CAPTURE_DIR = os.getenv('CAPTURE_DIR', 'captures')
ESP32_IP = os.getenv('ESP32_IP', '10.0.0.30')

class CaptureHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get list of captured images
            capture_path = Path(CAPTURE_DIR)
            if capture_path.exists():
                images = sorted(capture_path.glob('*.jpg'), reverse=True)
            else:
                images = []
            
            # Generate HTML with Arduino branding
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ESP32 Camera Gallery - Arduino</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #00979D 0%, #00878C 100%);
                        min-height: 100vh;
                        display: flex;
                    }
                    
                    /* Arduino Sidebar */
                    .sidebar {
                        width: 280px;
                        background: #00979D;
                        color: white;
                        padding: 20px;
                        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
                        display: flex;
                        flex-direction: column;
                        position: fixed;
                        height: 100vh;
                        overflow-y: auto;
                    }
                    
                    .logo {
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 2px solid rgba(255,255,255,0.2);
                    }
                    
                    .logo h1 {
                        color: white;
                        font-size: 24px;
                        margin-bottom: 5px;
                    }
                    
                    .logo p {
                        color: rgba(255,255,255,0.8);
                        font-size: 12px;
                    }
                    
                    .nav-section {
                        margin-bottom: 25px;
                    }
                    
                    .nav-section h3 {
                        color: rgba(255,255,255,0.7);
                        font-size: 12px;
                        text-transform: uppercase;
                        margin-bottom: 10px;
                        letter-spacing: 1px;
                    }
                    
                    .nav-button {
                        width: 100%;
                        padding: 12px 15px;
                        margin: 5px 0;
                        background: rgba(255,255,255,0.1);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.3s;
                        text-align: left;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    
                    .nav-button:hover {
                        background: rgba(255,255,255,0.2);
                        transform: translateX(5px);
                    }
                    
                    .nav-button.primary {
                        background: #E47128;
                    }
                    
                    .nav-button.primary:hover {
                        background: #D35F1E;
                    }
                    
                    .stats {
                        background: rgba(255,255,255,0.1);
                        padding: 15px;
                        border-radius: 8px;
                        margin-top: auto;
                    }
                    
                    .stat-item {
                        display: flex;
                        justify-content: space-between;
                        margin: 8px 0;
                        font-size: 13px;
                    }
                    
                    .stat-label {
                        color: rgba(255,255,255,0.7);
                    }
                    
                    .stat-value {
                        color: white;
                        font-weight: bold;
                    }
                    
                    /* Main Content */
                    .main-content {
                        margin-left: 280px;
                        flex: 1;
                        padding: 30px;
                        overflow-y: auto;
                    }
                    
                    .header {
                        background: white;
                        padding: 20px 30px;
                        border-radius: 12px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        margin-bottom: 30px;
                    }
                    
                    .header h2 {
                        color: #00979D;
                        margin-bottom: 10px;
                    }
                    
                    .header p {
                        color: #666;
                    }
                    
                    .live-feed {
                        background: white;
                        padding: 25px;
                        border-radius: 12px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        margin-bottom: 30px;
                    }
                    
                    .live-feed h3 {
                        color: #00979D;
                        margin-bottom: 15px;
                    }
                    
                    .live-feed img {
                        width: 100%;
                        max-width: 800px;
                        border: 3px solid #00979D;
                        border-radius: 8px;
                        display: block;
                        margin: 0 auto;
                    }
                    
                    .gallery {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                        gap: 20px;
                    }
                    
                    .image-card {
                        background: white;
                        border-radius: 12px;
                        padding: 15px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        transition: transform 0.3s, box-shadow 0.3s;
                    }
                    
                    .image-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                    }
                    
                    .image-card img {
                        width: 100%;
                        height: 200px;
                        object-fit: cover;
                        border-radius: 8px;
                        cursor: pointer;
                        border: 2px solid #e0e0e0;
                    }
                    
                    .image-info {
                        margin-top: 12px;
                        font-size: 12px;
                        color: #666;
                    }
                    
                    .image-info strong {
                        color: #00979D;
                        display: block;
                        margin-bottom: 5px;
                    }
                    
                    .image-actions {
                        margin-top: 12px;
                        display: flex;
                        gap: 8px;
                    }
                    
                    .btn-rename {
                        flex: 1;
                        background: #E47128;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                        transition: background 0.3s;
                    }
                    
                    .btn-rename:hover {
                        background: #D35F1E;
                    }
                    
                    .btn-delete {
                        flex: 1;
                        background: #DC3545;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                        transition: background 0.3s;
                    }
                    
                    .btn-delete:hover {
                        background: #C82333;
                    }
                    
                    .btn-chat {
                        flex: 1;
                        background: #00979D;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 12px;
                        transition: background 0.3s;
                    }
                    
                    .btn-chat:hover {
                        background: #00878C;
                    }
                    
                    .no-images {
                        text-align: center;
                        padding: 60px 20px;
                        color: #999;
                        background: white;
                        border-radius: 12px;
                    }
                    
                    .system-check {
                        background: rgba(255,255,255,0.1);
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                    }
                    
                    .check-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin: 8px 0;
                        font-size: 13px;
                    }
                    
                    .check-label {
                        color: rgba(255,255,255,0.9);
                    }
                    
                    .status-indicator {
                        width: 10px;
                        height: 10px;
                        border-radius: 50%;
                        display: inline-block;
                        margin-right: 5px;
                    }
                    
                    .status-online {
                        background: #4CAF50;
                        box-shadow: 0 0 5px #4CAF50;
                    }
                    
                    .status-offline {
                        background: #f44336;
                        box-shadow: 0 0 5px #f44336;
                    }
                    
                    .status-checking {
                        background: #ff9800;
                        animation: pulse 1.5s infinite;
                    }
                    
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.5; }
                    }
                    
                    /* Responsive */
                    @media (max-width: 768px) {
                        .sidebar {
                            width: 100%;
                            position: relative;
                            height: auto;
                        }
                        .main-content {
                            margin-left: 0;
                        }
                        body {
                            flex-direction: column;
                        }
                    }
                </style>
                <script>
                    function refreshPage() {
                        location.reload();
                    }
                    
                    function captureLive() {
                        fetch('http://10.0.0.30/capture')
                            .then(response => response.blob())
                            .then(blob => {
                                const url = URL.createObjectURL(blob);
                                document.getElementById('liveImage').src = url;
                            })
                            .catch(error => console.error('Error:', error));
                    }
                    
                    function captureAndSave() {
                        // Show loading state
                        const btn = event.target;
                        const originalText = btn.textContent;
                        btn.textContent = 'Capturing...';
                        btn.disabled = true;
                        
                        // Call API to capture and save image
                        fetch('/api/capture')
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Update live feed
                                    captureLive();
                                    // Show success message
                                    btn.textContent = 'Captured!';
                                    // Reload page after 1 second to show new image in gallery
                                    setTimeout(() => {
                                        location.reload();
                                    }, 1000);
                                } else {
                                    alert('Capture failed: ' + (data.error || 'Unknown error'));
                                    btn.textContent = originalText;
                                    btn.disabled = false;
                                }
                            })
                            .catch(error => {
                                alert('Error capturing image: ' + error);
                                btn.textContent = originalText;
                                btn.disabled = false;
                            });
                    }
                    
                    function openImage(src) {
                        window.open(src, '_blank');
                    }
                    
                    function deleteImage(filename) {
                        if (confirm('Are you sure you want to delete ' + filename + '?')) {
                            fetch('/api/delete/' + encodeURIComponent(filename), {
                                method: 'DELETE'
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    alert('Image deleted successfully');
                                    location.reload();
                                } else {
                                    alert('Error deleting image: ' + data.error);
                                }
                            })
                            .catch(error => {
                                alert('Error: ' + error);
                            });
                        }
                    }
                    
                    function renameImage(filename) {
                        const newLabel = prompt('Enter new label for ' + filename + ':', '');
                        if (newLabel && newLabel.trim()) {
                            fetch('/api/rename', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    old_name: filename,
                                    new_label: newLabel.trim()
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    alert('Image renamed to: ' + data.new_name);
                                    location.reload();
                                } else {
                                    alert('Error renaming image: ' + data.error);
                                }
                            })
                            .catch(error => {
                                alert('Error: ' + error);
                            });
                        }
                    }
                    
                    // Auto-refresh live feed every 5 seconds
                    setInterval(captureLive, 5000);
                    function chatWithImage(filename) {
                        alert('Chat feature coming soon! You can integrate with AI services like OpenAI Vision to analyze: ' + filename);
                        // TODO: Implement chat/AI analysis feature
                    }
                    
                    // System status checks
                    function checkESP32Status() {
                        const indicator = document.getElementById('esp32-status');
                        const text = document.getElementById('esp32-text');
                        
                        fetch('/api/status/esp32')
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'online') {
                                    indicator.className = 'status-indicator status-online';
                                    text.textContent = 'Online';
                                } else {
                                    indicator.className = 'status-indicator status-offline';
                                    text.textContent = 'Offline';
                                }
                            })
                            .catch(() => {
                                indicator.className = 'status-indicator status-offline';
                                text.textContent = 'Error';
                            });
                    }
                    
                    function checkN8NStatus() {
                        const indicator = document.getElementById('n8n-status');
                        const text = document.getElementById('n8n-text');
                        
                        fetch('/api/status/n8n')
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'running') {
                                    indicator.className = 'status-indicator status-online';
                                    text.textContent = 'Running';
                                } else {
                                    indicator.className = 'status-indicator status-offline';
                                    text.textContent = 'Stopped';
                                }
                            })
                            .catch(() => {
                                indicator.className = 'status-indicator status-offline';
                                text.textContent = 'Error';
                            });
                    }
                    
                    // Run checks on page load
                    window.onload = function() {
                        checkESP32Status();
                        checkN8NStatus();
                        // Recheck every 10 seconds
                        setInterval(checkESP32Status, 10000);
                        setInterval(checkN8NStatus, 10000);
                    };
                    
                    // Auto-refresh live feed every 5 seconds
                    setInterval(captureLive, 5000);
                </script>
            </head>
            <body>
                <!-- Arduino-styled Sidebar -->
                <div class="sidebar">
                    <div class="logo">
                        <h1>ESP32 CAM</h1>
                        <p>Arduino Camera Gallery</p>
                    </div>
                    
                    <div class="system-check">
                        <h3 style="color: rgba(255,255,255,0.7); font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">System Status</h3>
                        <div class="check-item">
                            <span class="check-label">ESP32 Camera</span>
                            <span><span id="esp32-status" class="status-indicator status-checking"></span><span id="esp32-text">Checking...</span></span>
                        </div>
                        <div class="check-item">
                            <span class="check-label">n8n Docker</span>
                            <span><span id="n8n-status" class="status-indicator status-checking"></span><span id="n8n-text">Checking...</span></span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <h3>Actions</h3>
                        <button class="nav-button primary" onclick="captureAndSave()">
                            Capture New Image
                        </button>
                        <button class="nav-button" onclick="refreshPage()">
                            Refresh Gallery
                        </button>
                        <button class="nav-button" onclick="window.open('http://10.0.0.30', '_blank')">
                            ESP32 Interface
                        </button>
                    </div>
                    
                    <div class="nav-section">
                        <h3>Automation</h3>
                        <button class="nav-button" onclick="window.open('http://localhost:5678', '_blank')">
                            n8n Automation
                        </button>
                        <button class="nav-button" onclick="window.open('/api/images', '_blank')">
                            API Endpoint
                        </button>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-label">Total Images:</span>
                            <span class="stat-value">""" + str(len(images)) + """</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Camera IP:</span>
                            <span class="stat-value">10.0.0.30</span>
                        </div>
                    </div>
                </div>
                
                <!-- Main Content Area -->
                <div class="main-content">
                    <div class="header">
                        <h2>Camera Gallery</h2>
                        <p>Real-time ESP32 camera monitoring and image management</p>
                    </div>
                    
                    <div class="live-feed">
                        <h3>Live Camera Feed</h3>
                        <img id="liveImage" src="http://10.0.0.30/capture" alt="Live Camera" onload="this.style.display='block'" onerror="this.style.display='none'">
                    </div>
                    
                    <h3 style="color: #00979D; margin-bottom: 20px;">Captured Images</h3>
            """
            
            if images:
                html += '<div class="gallery">'
                for img in images:
                    img_name = img.name
                    img_size = img.stat().st_size
                    img_size_kb = img_size / 1024
                    
                    # Parse timestamp from filename
                    try:
                        parts = img_name.split('_')
                        date = parts[1]
                        time = parts[2]
                        timestamp = f"{date[:4]}-{date[4:6]}-{date[6:8]} {time[:2]}:{time[2:4]}:{time[4:6]}"
                    except:
                        timestamp = "Unknown"
                    
                    html += f'''
                    <div class="image-card">
                        <img src="{CAPTURE_DIR}/{img_name}" alt="{img_name}" onclick="openImage('{CAPTURE_DIR}/{img_name}')">
                        <div class="image-info">
                            <strong>{img_name}</strong>
                            Time: {timestamp}<br>
                            Size: {img_size_kb:.1f} KB
                        </div>
                        <div class="image-actions">
                            <button class="btn-chat" onclick="chatWithImage('{img_name}')">Chat</button>
                            <button class="btn-rename" onclick="renameImage('{img_name}')">Rename</button>
                            <button class="btn-delete" onclick="deleteImage('{img_name}')">Delete</button>
                        </div>
                    </div>
                    '''
                html += '</div>'
            else:
                html += '<div class="no-images">No images captured yet. Click "Capture New Image" in the sidebar to start!</div>'
            
            html += """
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        
        elif self.path == '/api/status/esp32':
            # API endpoint to check ESP32 status
            import socket
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # Try to connect to ESP32
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ESP32_IP, 80))
                sock.close()
                
                if result == 0:
                    self.wfile.write(json.dumps({'status': 'online'}).encode())
                else:
                    self.wfile.write(json.dumps({'status': 'offline'}).encode())
            except:
                self.wfile.write(json.dumps({'status': 'offline'}).encode())
        
        elif self.path == '/api/status/n8n':
            # API endpoint to check n8n status
            import socket
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # Try to connect to n8n
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', 5678))
                sock.close()
                
                if result == 0:
                    self.wfile.write(json.dumps({'status': 'running'}).encode())
                else:
                    self.wfile.write(json.dumps({'status': 'stopped'}).encode())
            except:
                self.wfile.write(json.dumps({'status': 'stopped'}).encode())
        
        elif self.path == '/api/images':
            # API endpoint to list all images (for n8n)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            capture_path = Path(CAPTURE_DIR)
            if capture_path.exists():
                images = []
                for img in sorted(capture_path.glob('*.jpg'), reverse=True):
                    images.append({
                        'filename': img.name,
                        'path': f"{CAPTURE_DIR}/{img.name}",
                        'size': img.stat().st_size,
                        'modified': img.stat().st_mtime
                    })
                self.wfile.write(json.dumps({'images': images}).encode())
            else:
                self.wfile.write(json.dumps({'images': []}).encode())
        
        elif self.path == '/api/capture':
            # API endpoint to trigger camera capture (for n8n)
            import urllib.request
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Capture image from ESP32
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{CAPTURE_DIR}/capture_{timestamp}_api.jpg"
                
                req = urllib.request.Request(f'http://{ESP32_IP}/capture', method='GET')
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        image_data = response.read()
                        with open(filename, 'wb') as f:
                            f.write(image_data)
                        
                        result = {
                            'success': True,
                            'filename': filename,
                            'size': len(image_data),
                            'url': f"http://127.0.0.1:{PORT}/{filename}"
                        }
                        self.wfile.write(json.dumps(result).encode())
                    else:
                        self.wfile.write(json.dumps({'success': False, 'error': 'Camera returned non-200 status'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        
        else:
            # Serve files normally
            super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/rename':
            # Rename/relabel image
            try:
                data = json.loads(post_data.decode('utf-8'))
                old_name = data.get('old_name')
                new_label = data.get('new_label')
                
                if old_name and new_label:
                    old_path = Path(CAPTURE_DIR) / old_name
                    # Create new filename with label
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = f"capture_{timestamp}_{new_label}.jpg"
                    new_path = Path(CAPTURE_DIR) / new_name
                    
                    if old_path.exists():
                        shutil.move(str(old_path), str(new_path))
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True, 'new_name': new_name}).encode())
                    else:
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': False, 'error': 'File not found'}).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': 'Missing parameters'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_DELETE(self):
        # Delete image
        if self.path.startswith('/api/delete/'):
            filename = self.path.replace('/api/delete/', '')
            filename = urllib.parse.unquote(filename)
            
            try:
                file_path = Path(CAPTURE_DIR) / filename
                if file_path.exists() and file_path.parent == Path(CAPTURE_DIR):
                    file_path.unlink()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': 'File not found'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Bind to 0.0.0.0 for Docker, 127.0.0.1 for local
    host = "0.0.0.0" if os.getenv('DOCKER', 'false').lower() == 'true' else "127.0.0.1"
    with socketserver.TCPServer((host, PORT), CaptureHandler) as httpd:
        print(f"✓ Image viewer server running at http://{host}:{PORT}/")
        print(f"✓ ESP32 Camera IP: {ESP32_IP}")
        print(f"✓ Serving images from: {os.path.abspath(CAPTURE_DIR)}/")
        print(f"✓ Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")
