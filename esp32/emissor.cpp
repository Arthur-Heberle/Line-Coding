#include <esp_now.h>
#include <WiFi.h>

uint8_t masterMac[] = {0x00, 0x70, 0x07, 0x25, 0x36, 0xA0};

esp_now_peer_info_t peerInfo = {};

void onDataSent(const wifi_tx_info_t *tx_info, esp_now_send_status_t status) {
  Serial.print("ESP-NOW send: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "ok" : "fail");
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_register_send_cb(onDataSent);

  memcpy(peerInfo.peer_addr, masterMac, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("ESP-NOW peer add failed");
    return;
  }

  Serial.println("ESP32 Slave bridge ready");
}

void loop() {
  if (!Serial.available()) {
    delay(5);
    return;
  }

  String line = Serial.readStringUntil('\n');
  line.trim();

  if (line.length() == 0) {
    return;
  }

  if (line.length() > 240) {
    Serial.println("Serial line too large for simple ESP-NOW mode");
    return;
  }

  esp_err_t result = esp_now_send(masterMac, (const uint8_t *)line.c_str(), line.length());

  Serial.print("Forwarded bytes: ");
  Serial.println(line.length());

  if (result != ESP_OK) {
    Serial.print("esp_now_send error: ");
    Serial.println(result);
  }
}
