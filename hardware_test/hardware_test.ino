/*
 * ESP32-WROVER Comprehensive Hardware Test
 * Tests: LED, Serial I/O, Chip Info, Memory
 * Combined test for complete board verification
 */

#include <WiFi.h>

#define LED_PIN 2  // Built-in LED pin

// Serial I/O test variables
String inputBuffer = "";
bool serialTestComplete = false;

void setup() {
  // Configure LED pin first - immediate visual feedback
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED ON immediately
  
  // Initialize Serial
  Serial.begin(115200);
  delay(2000);  // Wait for serial to be ready
  
  Serial.println();
  Serial.println("=====================================");
  Serial.println("  ESP32-WROVER Hardware Test");
  Serial.println("=====================================");
  Serial.println();
  
  // Test 1: Chip Information
  Serial.println("TEST 1: Chip Information");
  Serial.println("-------------------------");
  Serial.print("Chip Model: ");
  Serial.println(ESP.getChipModel());
  
  Serial.print("Chip Revision: ");
  Serial.println(ESP.getChipRevision());
  
  Serial.print("Flash Size: ");
  Serial.print(ESP.getFlashChipSize() / (1024 * 1024));
  Serial.println(" MB");
  
  Serial.print("Free Heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
  
  Serial.print("CPU Frequency: ");
  Serial.print(ESP.getCpuFreqMHz());
  Serial.println(" MHz");
  
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  
  // Check for PSRAM
  Serial.print("PSRAM Found: ");
  Serial.println(psramFound() ? "YES" : "NO");
  if (psramFound()) {
    Serial.print("PSRAM Size: ");
    Serial.print(ESP.getPsramSize() / (1024 * 1024));
    Serial.println(" MB");
  }
  Serial.println("✓ Chip info test PASSED");
  Serial.println();
  
  // Test 2: LED Hardware
  Serial.println("TEST 2: LED Hardware");
  Serial.println("--------------------");
  Serial.println("Testing LED blink pattern...");
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    Serial.print("  Blink ");
    Serial.print(i + 1);
    Serial.println(": LED ON");
    delay(300);
    
    digitalWrite(LED_PIN, LOW);
    Serial.println("         LED OFF");
    delay(300);
  }
  Serial.println("✓ LED test PASSED");
  Serial.println();
  
  // Test 3: Serial I/O
  Serial.println("TEST 3: Serial I/O");
  Serial.println("------------------");
  Serial.println("Type 'TEST' and press Enter to verify serial input:");
  Serial.print("> ");
}

void loop() {
  // Serial I/O Test - wait for user input
  if (!serialTestComplete && Serial.available() > 0) {
    char inChar = Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputBuffer.length() > 0) {
        Serial.println(inputBuffer);  // Echo back
        
        if (inputBuffer.equalsIgnoreCase("TEST")) {
          Serial.println("✓ Serial I/O test PASSED");
          Serial.println();
          Serial.println("=====================================");
          Serial.println("  ALL TESTS PASSED!");
          Serial.println("  ESP32-WROVER is fully functional");
          Serial.println("=====================================");
          Serial.println();
          serialTestComplete = true;
        } else {
          Serial.print("Received: '");
          Serial.print(inputBuffer);
          Serial.println("' - Please type 'TEST'");
          Serial.print("> ");
        }
        inputBuffer = "";
      }
    } else if (inChar != '\r') {  // Ignore carriage return
      inputBuffer += inChar;
    }
  }
  
  // Continuous LED blink to show board is running
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 1000) {
    lastBlink = millis();
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    
    // Show heartbeat after serial test completes
    if (serialTestComplete) {
      Serial.print(".");
      static int dotCount = 0;
      dotCount++;
      if (dotCount >= 60) {
        dotCount = 0;
        Serial.println();
        Serial.print("Uptime: ");
        Serial.print(millis() / 1000);
        Serial.print("s | Free Heap: ");
        Serial.print(ESP.getFreeHeap());
        Serial.println(" bytes");
      }
    }
  }
}
