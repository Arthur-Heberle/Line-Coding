#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>

void onDataRecv(const esp_now_recv_info_t *esp_now_info, const uint8_t *incomingData, int len) {
  String line = "";
  line.reserve(len);

  for (int i = 0; i < len; i++) {
    line += (char)incomingData[i];
  }

  line.trim();

  if (line.length() > 0) {
    Serial.println(line);
  }
}

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  Serial.print("Receiver MAC: ");
  Serial.println(WiFi.macAddress());
  
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_register_recv_cb(onDataRecv);
}

void loop() {
}
