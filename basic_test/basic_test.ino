/*
 * ESP32-S3 Basic Test - No WiFi
 * Simple test sketch to verify ESP32 hardware functionality
 * Sends startup info and "Hello World" every minute
 */

#include <WiFi.h>  // Required for MAC address (no WiFi connection needed)

void blinkLedSlow(int blinks, int onTime, int offTime) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(2, HIGH);
    delay(onTime);
    digitalWrite(2, LOW);
    delay(offTime);
    Serial.print("Blink ");
    Serial.println(i + 1);
  }
}

void setup() {
  // Initialize Serial FIRST
  Serial.begin(115200);
  delay(3000);  // Wait for serial to be ready
  
  Serial.println();
  Serial.println("=====================================");
  Serial.println("  ESP32-S3 Basic Test Starting");
  Serial.println("=====================================");
  
  // Print chip information
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
  Serial.println(WiFi.macAddress());  // MAC works even without WiFi connection
  
  Serial.print("Sketch Size: ");
  Serial.print(ESP.getSketchSize() / 1024);
  Serial.println(" KB");
  
  Serial.print("Free Sketch Space: ");
  Serial.print(ESP.getFreeSketchSpace() / 1024);
  Serial.println(" KB");
  
  // Test built-in LED
  pinMode(2, OUTPUT);
  Serial.println("Built-in LED (pin 2) configured");
  
  // Blink LED to indicate successful startup
  Serial.println("Startup indication - slow LED blink sequence...");
  blinkLedSlow(5, 500, 500);  // 5 slow blinks: 500ms on, 500ms off
  
  Serial.println("=====================================");
  Serial.println("  ESP32-S3 Basic Test Complete!");
  Serial.println("  Sending 'Hello World' every minute");
  Serial.println("=====================================");
  
  Serial.println("\n*** HELLO WORLD - STARTUP ***");
  Serial.print("System ready at: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
}

void loop() {
  static unsigned long lastHello = 0;
  static int helloCount = 0;
  
  // Send Hello World every 60 seconds (1 minute)
  if (millis() - lastHello >= 60000) {
    lastHello = millis();
    helloCount++;
    
    Serial.println("\n*** HELLO WORLD ***");
    Serial.print("Message #");
    Serial.print(helloCount);
    Serial.print(" | Uptime: ");
    Serial.print(millis() / 1000);
    Serial.println(" seconds");
    
    Serial.print("Free Heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    
    Serial.print("CPU Temperature: ");
    Serial.print(temperatureRead());
    Serial.println(" °C");
    
    // Toggle LED to show activity
    static bool ledState = false;
    ledState = !ledState;
    digitalWrite(2, ledState ? HIGH : LOW);
    Serial.print("LED Status: ");
    Serial.println(ledState ? "ON" : "OFF");
    
    Serial.println("*** END HELLO WORLD ***\n");
  }
  
  // Brief delay every 10 seconds to show we're still running
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus >= 10000) {
    lastStatus = millis();
    Serial.print(".");
    Serial.flush();  // Ensure output is sent immediately
  }
  
  delay(100);
}
