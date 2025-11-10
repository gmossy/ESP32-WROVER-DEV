/*
 * ESP32-WROVER Simple Test
 * Basic test to verify board is working
 * Updated with modern ESP32 practices
 */

#include <WiFi.h>

#define LED_PIN 2  // Built-in LED pin

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  delay(2000);  // Wait for serial to be ready
  
  Serial.println();
  Serial.println("=====================================");
  Serial.println("  ESP32-WROVER Simple Test");
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
  
  // Configure LED pin
  pinMode(LED_PIN, OUTPUT);
  Serial.println("LED configured - starting blink test...");
  
  Serial.println("=====================================");
  Serial.println("  ESP32-WROVER is ready!");
  Serial.println("=====================================");
}

void loop() {
  // Blink LED to show it's running
  digitalWrite(LED_PIN, HIGH);
  Serial.println("LED ON");
  delay(1000);
  
  digitalWrite(LED_PIN, LOW);
  Serial.println("LED OFF");
  delay(1000);
}
