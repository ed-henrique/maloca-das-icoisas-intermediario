/*
Autor: Equipe 4 - Os Suricatos Cibernéticos

Descrição:
Dispositivo médico que DEVE acionar o LED e o BUZZER por 5 segundos,
de forma intermitente, quando uma mensagem for recebida via MQTT no
canal 'pacientes_pos_cirurgicos/monitoramento'
*/

#include <WiFi.h>
#include <PubSubClient.h>  // MQTT library

#define LED    13
#define BUZZER 12

const char* ssid = "Macuxi Digital";
const char* password = "@Macuxi#ufrr35anos";
const char* mqtt_server = "172.22.68.36";

WiFiClient espClient;
PubSubClient client(espClient);

bool alert = false;

void enable() {
  digitalWrite(LED, HIGH);
  digitalWrite(BUZZER, HIGH);
}

void disable() {
  digitalWrite(LED, LOW);
  digitalWrite(BUZZER, LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi");

  // Set MQTT server
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  // Connect to MQTT broker
  while (!client.connected()) {
    Serial.print("Tentando se conectar ao servidor MQTT...");
    if (client.connect("Dispositivo do Paciente")) {
      Serial.println("Conectado ao MQTT");
      // Subscribe to the desired topic
      client.subscribe("pacientes_pos_cirurgicos/monitoramento");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println();
      delay(2000);
    }
  }
}

void loop() {
  // MQTT client loop
  client.loop();

  // Intermittently turn on and off the alert (LED + BUZZER) for 5 seconds
  
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Message received
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  // Trigger the alert if the message is received
  if (String(topic) == "pacientes_pos_cirurgicos/monitoramento") {
    Serial.println(message);
    if (String(message) == "ALERT") {
      for (int i = 0; i < 5; i++) {
        enable();
        delay(500);  // LED and Buzzer on for 500ms
        disable();
        delay(500);  // LED and Buzzer off for 500ms
      }
    }
  }
}
