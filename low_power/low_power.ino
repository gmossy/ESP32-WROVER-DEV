/*
 * ESP32-S3 Ultra Low Power Test
 * Minimal power consumption sketch
 * No WiFi, reduced CPU speed, minimal components
 */

// Remove WiFi.h completely - no WiFi radio initialization
// Use hardware serial instead of USB serial if possible

void blinkLedSlow(int blinks, int onTime, int offTime) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(2, HIGH);
    delay(onTime);
    digitalWrite(2, LOW);
    delay(offTime);
    Serial.print("Slow blink ");
    Serial.println(i + 1);
  }
}

void setup() {
  // Reduce CPU frequency to save power
  setCpuFrequencyMhz(80);  // Reduce from 240MHz to 80MHz
  
  // Initialize Serial at lower baud rate (less power)
  Serial.begin(9600);  // Reduced from 115200 to 9600
  delay(1000);  // Shorter delay
  
  Serial.println();
  Serial.println("=== ESP32-S3 LOW POWER TEST ===");
  
  // Minimal startup info (less processing)
  Serial.print("CPU: ");
  Serial.print(getCpuFrequencyMhz());
  Serial.println("MHz");
  
  Serial.print("Free Heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
  
  // Configure LED for minimal power usage
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW);  // LED off by default
  
  Serial.println("Low power mode active");
  Serial.println("Hello World every 60 seconds");
  Serial.println("================================");
  
  // Initial hello world
  Serial.println("*** HELLO WORLD - STARTUP ***");
}

void loop() {
  static unsigned long lastHello = 0;
  static int helloCount = 0;
  
  // Use delay() instead of millis() for more efficient sleep
  // Check every 10 seconds, send hello every 60 seconds
  static int counter = 0;
  
  delay(10000);  // 10 second delay (allows CPU to sleep)
  counter++;
  
  // Send hello every 6 intervals = 60 seconds
  if (counter >= 6) {
    counter = 0;
    helloCount++;
    
    Serial.println();
    Serial.println("*** HELLO WORLD ***");
    Serial.print("Message #");
    Serial.println(helloCount);
    Serial.print("Uptime: ");
    Serial.print(millis() / 1000);
    Serial.println("s");
    Serial.print("Heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    Serial.println("*** END ***");
    Serial.println();
    
    // Brief LED flash (minimal power)
    blinkLedSlow(1, 200, 200);  // 1 slow blink: 200ms on, 200ms off
  } else {
    // Show we're still alive with minimal power
    Serial.print(".");
  }
}
