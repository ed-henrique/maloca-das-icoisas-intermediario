/*
Autor: Equipe 4 - Os Suricatos Cibernéticos

Descrição:
Dispositivo médico que DEVE enviar dados de temperatura, batimento
cardíaco e movimento ao servidor web regularmente.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "RoboCore_MMA8452Q.h"

#define LED           16       // LED connected to pin 16
#define BEATRATE      A0       // Potentiometer connected to pin 33 (Analog input)
#define DHT_PIN       12       // DHT11 sensor data pin
#define DHT_TYPE      DHT11    // Specify DHT11 sensor

const char* ssid = "Macuxi Digital";
const char* password = "@Macuxi#ufrr35anos";
const char* mqtt_server = "172.22.68.36";  // Replace with your MQTT broker's address

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHT_PIN, DHT_TYPE);
MMA8452Q acel;

void setup() {
  // Start the Serial Monitor
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize Accelerometer
  acel.init();
  
  // Set up the LED pin as output (PWM capable pin for brightness control)
  pinMode(LED, OUTPUT);
  
  // Set up the potentiometer pin as input
  pinMode(BEATRATE, INPUT);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Set up MQTT client
  client.setServer(mqtt_server, 1883);  // Port 1883 is the default MQTT port
}

void reconnect() {
  // Loop until we're reconnected to the MQTT broker
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      // Subscribe to topics if needed (not necessary for publishing)
      // client.subscribe("your_topic");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  
  client.loop();  // Keep the MQTT connection alive
  
  // Read the beatrate value
  float heartrate_raw = analogRead(BEATRATE);
  int heartrate = map(heartrate_raw, 0, 4095, 0, 215);

  // Read temperature and humidity from the DHT11 sensor
  float temperature = dht.readTemperature(); // Temperature in Celsius
  float humidity = dht.readHumidity();      // Humidity in %

  // Read accelerometer data
  acel.read();

  // Format the sensor data into a message
  String message = "Temperature: " + String(temperature) + "°C, ";
  message += "Humidity: " + String(humidity) + "%, ";
  message += "Heart Rate: " + String(heartrate) + " bpm, ";
  message += "Accel X: " + String(acel.x) + ", ";
  message += "Accel Y: " + String(acel.y) + ", ";
  message += "Accel Z: " + String(acel.z);

  // Publish data to the MQTT topic
  client.publish("pacientes_pos_cirurgicos/monitoramento", message.c_str());

  // Print data to Serial Monitor
  Serial.println(message);

  // Delay before next loop
  delay(5000);  // Send data every 10 seconds
}
