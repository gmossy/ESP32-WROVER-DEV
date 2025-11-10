/*
 * ESP32-S3 Hardware Test - Minimal
 * Tests absolute basic functionality without any libraries
 */

// No includes - pure hardware test

void setup() {
  // Configure LED pin first
  pinMode(2, OUTPUT);
  
  // Immediate LED test - no serial, no delays
  digitalWrite(2, HIGH);  // LED ON immediately
}

void loop() {
  // Blink LED fast to show it's running
  digitalWrite(2, HIGH);
  delay(100);
  digitalWrite(2, LOW);
  delay(100);
}
