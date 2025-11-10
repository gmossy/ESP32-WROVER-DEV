/*
 * ESP32-S3 Web Server
 * Creates a simple web server on the ESP32-S3
 * IP Address: 10.0.0.30
 */

#include <WiFi.h>
#include <WebServer.h>

// WiFi credentials - UPDATE THESE
const char* ssid = "FOOTBALL_EXT_5G";
const char* password = "cities3976";

// Static IP configuration
IPAddress local_IP(10, 0, 0, 30);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);

// Create web server on port 80
WebServer server(80);

// LED pin (built-in LED on most ESP32-S3 boards)
const int LED_PIN = 2;
bool ledState = false;

void blinkLedSlow(int blinks, int onTime, int offTime) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(onTime);
    digitalWrite(LED_PIN, LOW);
    delay(offTime);
    Serial.print("Webserver blink ");
    Serial.println(i + 1);
  }
}

// HTML page
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-S3 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .status {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            margin: 10px 5px;
            font-size: 16px;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            color: white;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #45a049;
        }
        .button.off {
            background-color: #f44336;
        }
        .button.off:hover {
            background-color: #da190b;
        }
        .info {
            margin-top: 20px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 ESP32-S3 Web Server</h1>
        <div class="status">
            <strong>Status:</strong> Server is running!<br>
            <strong>LED State:</strong> <span id="ledState">%LED_STATE%</span>
        </div>
        <div style="text-align: center;">
            <a href="/led/on" class="button">Turn LED ON</a>
            <a href="/led/off" class="button off">Turn LED OFF</a>
            <a href="/led/toggle" class="button" style="background-color: #FF9800;">Toggle LED</a>
        </div>
        <div class="info">
            <strong>Device Info:</strong><br>
            Chip: ESP32-S3<br>
            IP Address: 10.0.0.30<br>
            Free Heap: %FREE_HEAP% bytes<br>
            Uptime: %UPTIME% seconds
        </div>
    </div>
</body>
</html>
)rawliteral";

// Handle root page
void handleRoot() {
    String html = String(htmlPage);
    html.replace("%LED_STATE%", ledState ? "ON" : "OFF");
    html.replace("%FREE_HEAP%", String(ESP.getFreeHeap()));
    html.replace("%UPTIME%", String(millis() / 1000));
    
    server.send(200, "text/html", html);
    Serial.println("Root page served");
}

// Handle LED ON
void handleLedOn() {
    ledState = true;
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED turned ON");
    
    server.sendHeader("Location", "/");
    server.send(303);
}

// Handle LED OFF
void handleLedOff() {
    ledState = false;
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED turned OFF");
    
    server.sendHeader("Location", "/");
    server.send(303);
}

// Handle LED Toggle
void handleLedToggle() {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
    Serial.println("LED toggled to: " + String(ledState ? "ON" : "OFF"));
    
    server.sendHeader("Location", "/");
    server.send(303);
}

// Handle 404
void handleNotFound() {
    String message = "404 - Not Found\n\n";
    message += "URI: " + server.uri() + "\n";
    message += "Method: " + String((server.method() == HTTP_GET) ? "GET" : "POST") + "\n";
    
    server.send(404, "text/plain", message);
    Serial.println("404: " + server.uri());
}

void setup() {
    // Initialize Serial
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n\n=== ESP32-S3 Web Server Starting ===");
    
    // Initialize LED pin
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // Configure static IP
    Serial.println("Configuring static IP: 10.0.0.30");
    if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
        Serial.println("Failed to configure static IP");
    }
    
    // Connect to WiFi
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
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
    } else {
        Serial.println("\n✗ WiFi Connection Failed!");
        Serial.println("Please check your WiFi credentials and try again.");
        return;
    }
    
    // Setup web server routes
    server.on("/", HTTP_GET, handleRoot);
    server.on("/led/on", HTTP_GET, handleLedOn);
    server.on("/led/off", HTTP_GET, handleLedOff);
    server.on("/led/toggle", HTTP_GET, handleLedToggle);
    server.onNotFound(handleNotFound);
    
    // Start server
    server.begin();
    Serial.println("✓ Web Server Started!");
    Serial.println("Access the server at: http://10.0.0.30");
    
    // Slow LED blink to indicate server ready
    Serial.println("LED configured - slow blink sequence...");
    blinkLedSlow(6, 700, 700);  // 6 slow blinks: 700ms on, 700ms off
    Serial.println("Main webserver ready!");
    
    Serial.println("=====================================\n");
}

void loop() {
    // Handle client requests
    server.handleClient();
    
    // Optional: Print status every 30 seconds
    static unsigned long lastStatus = 0;
    if (millis() - lastStatus > 30000) {
        lastStatus = millis();
        Serial.print("Server running | Uptime: ");
        Serial.print(millis() / 1000);
        Serial.print("s | Free Heap: ");
        Serial.print(ESP.getFreeHeap());
        Serial.println(" bytes");
    }
}
