/*
 * ESP32-S3 Serial Test
 * Basic test to verify ESP32 is working and can output to serial
 * Updated with modern ESP32 practices
 */

#include <WiFi.h>

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  delay(2000);  // Wait for serial to be ready
  
  Serial.println();
  Serial.println("=====================================");
  Serial.println("  ESP32-S3 Serial Test Starting");
  Serial.println("=====================================");
  
  // Print chip info using modern functions
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
  
  // Print MAC address
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  
  // Test built-in LED
  pinMode(2, OUTPUT);
  Serial.println("Testing built-in LED (pin 2)...");
  
  Serial.println("=====================================");
  Serial.println("  ESP32-S3 is working properly!");
  Serial.println("=====================================");
}

void loop() {
  // Blink LED to show it's running
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  
  if (millis() - lastBlink > 1000) {
    lastBlink = millis();
    ledState = !ledState;
    digitalWrite(2, ledState ? HIGH : LOW);
    
    Serial.print("LED Status: ");
    Serial.println(ledState ? "ON" : "OFF");
    Serial.print("Uptime: ");
    Serial.print(millis() / 1000);
    Serial.println(" seconds");
    Serial.print("Free Heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    Serial.println("---");
  }
  
  delay(100);
}
