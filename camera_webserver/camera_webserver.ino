/*
 * ESP32-WROVER Camera Web Server
 * Captures and serves images from ESP32 camera module
 * 
 * IMPORTANT: Run 'python3 generate_config.py' to create config.h from .env
 * Created by: Glenn Mossy
 * Date: 2025-11-12
 */

#include <WiFi.h>
#include <WebServer.h>
#include "esp_camera.h"
#include "config.h"  // WiFi credentials and network config from .env

// Create web server
WebServer server(80);

// Camera pins for Freenove ESP32-WROVER-CAM Board
// Try configuration 1 (most common for Freenove WROVER)
#define PWDN_GPIO_NUM     -1  // Not used
#define RESET_GPIO_NUM    -1  // Not used
#define XCLK_GPIO_NUM     21
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       19
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM        5
#define Y2_GPIO_NUM        4
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Init with high specs to pre-allocate larger buffers
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }
  
  Serial.println("Camera initialized successfully");
}

void handleRoot() {
  String html = "<html><head><style>";
  html += "body { font-family: Arial; text-align: center; margin: 20px; }";
  html += "img { max-width: 100%; height: auto; border: 2px solid #333; }";
  html += "button { padding: 10px 20px; font-size: 16px; margin: 10px; }";
  html += "</style></head><body>";
  html += "<h1>ESP32 Camera Server</h1>";
  html += "<p>Uptime: " + String(millis() / 1000) + "s</p>";
  html += "<p>Free Heap: " + String(ESP.getFreeHeap()) + " bytes</p>";
  html += "<img id='camera' src='/capture' />";
  html += "<br><button onclick='location.reload()'>Refresh</button>";
  html += "<button onclick='document.getElementById(\"camera\").src=\"/capture?t=\"+Date.now()'>Capture New</button>";
  html += "<script>setInterval(function(){document.getElementById('camera').src='/capture?t='+Date.now()},5000);</script>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
  Serial.println("Root page served");
}

void handleCapture() {
  camera_fb_t * fb = NULL;
  
  // Take Picture with Camera
  fb = esp_camera_fb_get();  
  if(!fb) {
    Serial.println("Camera capture failed");
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  
  Serial.printf("Image captured: %d bytes\n", fb->len);
  
  // Send image
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  // Return the frame buffer back to the driver for reuse
  esp_camera_fb_return(fb);
  Serial.println("Image served");
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println();
  Serial.println("=== ESP32-WROVER CAMERA WEB SERVER ===");
  
  // Initialize camera
  setupCamera();
  
  // Configure static IP
  if (!WiFi.config(local_IP, gateway, subnet, IPAddress(8, 8, 8, 8), IPAddress(8, 8, 4, 4))) {
    Serial.println("Static IP config failed");
  }
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC: ");
    Serial.println(WiFi.macAddress());
    
    // Setup web server routes
    server.on("/", handleRoot);
    server.on("/capture", handleCapture);
    server.begin();
    Serial.println("Web server started");
    Serial.println("Camera stream available at http://10.0.0.30/capture");
    
  } else {
    Serial.println("\nWiFi connection failed");
  }
  
  Serial.println("Setup complete");
}

void loop() {
  server.handleClient();
  delay(10);
}
