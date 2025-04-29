#include <ESP8266WiFi.h>

const char* ssid = "Samsung_A53";        // Ganti dengan nama WiFi Anda
const char* password = "zikri.wahyuzi"; // Ganti dengan password WiFi Anda

WiFiServer server(80);  // Port untuk server HTTP

int relayPin = D1; // Relay terhubung ke pin D1 (GPIO 5)

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);  // Awalnya relay mati

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi berhasil tersambung!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String request = client.readStringUntil('\r');
    client.flush();

    if (request.indexOf("/lampOn") != -1) {
      digitalWrite(relayPin, HIGH);  // Hidupkan relay
    }
    if (request.indexOf("/lampOff") != -1) {
      digitalWrite(relayPin, LOW);  // Matikan relay
    }

    // Kirim respon HTTP ke client
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/html");
    client.println();
    client.println("<h1>Relay is Controlled</h1>");
    client.println();
  }
}