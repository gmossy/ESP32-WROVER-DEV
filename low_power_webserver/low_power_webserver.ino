/*
 * ESP32-S3 Low Power Web Server
 * Reduced power consumption version
 */

#include <WiFi.h>
#include <WebServer.h>
#include <esp_wifi.h>

// WiFi credentials
const char* ssid = "FOOTBALL";
const char* password = "cities3976";

// Static IP configuration
IPAddress local_IP(10, 0, 0, 30);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);

// Create web server
WebServer server(80);

void blinkLedSlow(int blinks, int onTime, int offTime) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(2, HIGH);
    delay(onTime);
    digitalWrite(2, LOW);
    delay(offTime);
    Serial.print("Server blink ");
    Serial.println(i + 1);
  }
}

void handleRoot() {
  // Minimal HTML to reduce memory and processing
  String html = "<html><body><h1>ESP32 Low Power</h1><p>Uptime: ";
  html += String(millis() / 1000);
  html += "s</p><p>Heap: ";
  html += String(ESP.getFreeHeap());
  html += " bytes</p></body></html>";
  
  server.send(200, "text/html", html);
  Serial.println("Request served");
}

void setup() {
  // Reduce CPU frequency
  setCpuFrequencyMhz(160);  // Moderate reduction (240->160MHz)
  
  // Lower serial baud rate
  Serial.begin(115200);  // Standard baud rate for compatibility
  delay(2000);
  
  Serial.println();
  Serial.println("=== ESP32-S3 LOW POWER WEB SERVER ===");
  
  // Configure static IP
  if (!WiFi.config(local_IP, gateway, subnet, IPAddress(8, 8, 8, 8), IPAddress(8, 8, 4, 4))) {
    Serial.println("Static IP config failed");
  }
  
  // Connect to WiFi with power management
  Serial.print("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  
  // Set WiFi power saving mode (modern approach)
  esp_wifi_set_ps(WIFI_PS_MAX_MODEM);  // Enable maximum power saving
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {  // Fewer attempts
    delay(2000);  // Longer delay between attempts
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    // Setup minimal web server
    server.on("/", handleRoot);
    server.begin();
    Serial.println("Web server started");
    
  } else {
    Serial.println("\nWiFi connection failed");
  }
  
  Serial.println("Setup complete");
  
  // Configure LED and blink to indicate server ready
  pinMode(2, OUTPUT);
  Serial.println("LED configured - slow blink sequence...");
  blinkLedSlow(3, 800, 800);  // 3 slow blinks: 800ms on, 800ms off
  Serial.println("Server ready!");
}

void loop() {
  // Handle client requests
  server.handleClient();
  
  // Minimal status reporting (less frequent)
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 30000) {  // Every 30 seconds instead of 10
    lastStatus = millis();
    Serial.print("Status: ");
    Serial.print(WiFi.status());
    Serial.print(" | Heap: ");
    Serial.println(ESP.getFreeHeap());
  }
  
  delay(200);  // Slightly longer delay for power saving
}
