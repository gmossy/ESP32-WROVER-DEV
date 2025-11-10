/*
 * Simple ESP32-S3 Web Server
 * Minimal web server for troubleshooting
 */

#include <WiFi.h>
#include <WebServer.h>

// WiFi credentials
const char* ssid = "FOOTBALL_EXT_5G";
const char* password = "cities3976";

// Static IP configuration
IPAddress local_IP(10, 0, 0, 30);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);

// Create web server on port 80
WebServer server(80);

void blinkLedSlow(int blinks, int onTime, int offTime) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(2, HIGH);
    delay(onTime);
    digitalWrite(2, LOW);
    delay(offTime);
    Serial.print("Simple blink ");
    Serial.println(i + 1);
  }
}

void handleRoot() {
  String html = "<html><body>";
  html += "<h1>ESP32-S3 Simple Web Server</h1>";
  html += "<p>Server is working!</p>";
  html += "<p>Uptime: " + String(millis() / 1000) + " seconds</p>";
  html += "<p>Free Heap: " + String(ESP.getFreeHeap()) + " bytes</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
  Serial.println("Root page served");
}

void setup() {
  // Initialize Serial FIRST
  Serial.begin(115200);
  delay(3000);  // Extra delay for serial to be ready
  
  Serial.println("\n\n=== ESP32-S3 Simple Web Server Starting ===");
  
  // Configure static IP
  Serial.println("Configuring static IP: 10.0.0.30");
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("Failed to configure static IP");
  } else {
    Serial.println("Static IP configured successfully");
  }
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
    
    // Print status during connection attempts
    if (attempts % 5 == 0) {
      Serial.print("\nStatus: ");
      Serial.print(WiFi.status());
      Serial.print(" Attempt ");
      Serial.print(attempts);
      Serial.println("/20");
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
    Serial.print("Signal Strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    
    // Setup web server routes
    server.on("/", HTTP_GET, handleRoot);
    
    // Start server
    server.begin();
    Serial.println("✓ Web Server Started!");
    Serial.println("Access the server at: http://10.0.0.30");
    Serial.println("=====================================\n");
    
    // Configure LED and blink to indicate server ready
    pinMode(2, OUTPUT);
    Serial.println("LED configured - slow blink sequence...");
    blinkLedSlow(4, 600, 600);  // 4 slow blinks: 600ms on, 600ms off
    Serial.println("Simple server ready!");
    
  } else {
    Serial.println("\n✗ WiFi Connection Failed!");
    Serial.print("Final status: ");
    Serial.println(WiFi.status());
    Serial.println("Possible issues:");
    Serial.println("- Wrong WiFi credentials");
    Serial.println("- WiFi network not reachable");
    Serial.println("- Static IP conflict");
    Serial.println("=====================================\n");
  }
}

void loop() {
  // Handle client requests
  server.handleClient();
  
  // Print status every 10 seconds
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 10000) {
    lastStatus = millis();
    Serial.print("Status check | Uptime: ");
    Serial.print(millis() / 1000);
    Serial.print("s | WiFi Status: ");
    Serial.print(WiFi.status());
    Serial.print(" | IP: ");
    Serial.println(WiFi.localIP());
  }
  
  delay(100);
}
