#include <dht.h>

dht DHT;

#define DHT11_PIN 7

void setup() {
  Serial.begin(9600);
}

void loop() {
  int chk = DHT.read11(DHT11_PIN);
  
  // Use readTemperature() to get the temperature in Celsius
  float temperatureC = DHT.temperature;
  // Convert the temperature to Fahrenheit
  float temperatureF = temperatureC * 1.8 + 32;

  // Read and print temperature in Celsius
  Serial.print((int)temperatureC);
  Serial.print(", "); // Add comma separator
  
  // Read and print temperature in Fahrenheit
  Serial.print((int)temperatureF);
  Serial.print(", "); // Add comma separator

  // Read and print humidity
  float humidity = DHT.humidity;
  Serial.print((int)humidity);
  Serial.println(""); // New line
  delay(2000);
}
