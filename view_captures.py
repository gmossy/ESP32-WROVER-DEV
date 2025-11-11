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
            
            # Generate HTML
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ESP32 Camera Captures</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f0f0f0;
                    }
                    h1 {
                        color: #333;
                        text-align: center;
                    }
                    .info {
                        text-align: center;
                        margin: 20px 0;
                        padding: 15px;
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 5px;
                    }
                    .controls {
                        text-align: center;
                        margin: 20px 0;
                    }
                    button {
                        padding: 10px 20px;
                        font-size: 16px;
                        margin: 5px;
                        cursor: pointer;
                        background-color: #008CBA;
                        color: white;
                        border: none;
                        border-radius: 4px;
                    }
                    button:hover {
                        background-color: #007399;
                    }
                    .gallery {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 20px;
                        margin-top: 20px;
                    }
                    .image-card {
                        background-color: white;
                        border-radius: 8px;
                        padding: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .image-card img {
                        width: 100%;
                        height: auto;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .image-card img:hover {
                        opacity: 0.8;
                    }
                    .image-info {
                        margin-top: 10px;
                        font-size: 12px;
                        color: #666;
                    }
                    .no-images {
                        text-align: center;
                        padding: 40px;
                        color: #999;
                    }
                    .live-feed {
                        text-align: center;
                        margin: 20px 0;
                        padding: 20px;
                        background-color: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .live-feed img {
                        max-width: 100%;
                        border: 2px solid #333;
                        border-radius: 4px;
                    }
                    .image-actions {
                        margin-top: 10px;
                        display: flex;
                        gap: 5px;
                        flex-wrap: wrap;
                    }
                    .btn-delete {
                        background-color: #f44336;
                        padding: 5px 10px;
                        font-size: 12px;
                    }
                    .btn-delete:hover {
                        background-color: #da190b;
                    }
                    .btn-rename {
                        background-color: #ff9800;
                        padding: 5px 10px;
                        font-size: 12px;
                    }
                    .btn-rename:hover {
                        background-color: #e68900;
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
                </script>
            </head>
            <body>
                <h1>📷 ESP32 Camera Captures</h1>
                
                <div class="info">
                    <strong>Camera Status:</strong> Connected to 10.0.0.30<br>
                    <strong>Total Captures:</strong> """ + str(len(images)) + """ images
                </div>
                
                <div class="live-feed">
                    <h2>Live Camera Feed</h2>
                    <img id="liveImage" src="http://10.0.0.30/capture" alt="Live Camera" onload="this.style.display='block'" onerror="this.style.display='none'">
                    <br><br>
                    <button onclick="captureLive()">📸 Capture New Image</button>
                </div>
                
                <div class="controls">
                    <button onclick="refreshPage()">🔄 Refresh Gallery</button>
                    <button onclick="window.open('http://10.0.0.30', '_blank')">🌐 Open ESP32 Interface</button>
                </div>
                
                <h2 style="text-align: center;">Captured Images</h2>
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
                            <strong>{img_name}</strong><br>
                            Time: {timestamp}<br>
                            Size: {img_size_kb:.1f} KB
                        </div>
                        <div class="image-actions">
                            <button class="btn-rename" onclick="renameImage('{img_name}')">🏷️ Rename</button>
                            <button class="btn-delete" onclick="deleteImage('{img_name}')">🗑️ Delete</button>
                        </div>
                    </div>
                    '''
                html += '</div>'
            else:
                html += '<div class="no-images">No images captured yet. Click "Capture New Image" above to start!</div>'
            
            html += """
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        
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
