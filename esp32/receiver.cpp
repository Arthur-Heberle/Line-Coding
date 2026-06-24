#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>

void onDataRecv(const esp_now_recv_info_t *esp_now_info, const uint8_t *incomingData, int len) {
  char buf[250];
  int copy_len = (len < 249) ? len : 249;
  memcpy(buf, incomingData, copy_len);
  buf[copy_len] = '\0';

  int end = copy_len - 1;
  while (end >= 0 && (buf[end] == '\n' || buf[end] == '\r' || buf[end] == ' ')) {
    buf[end--] = '\0';
  }

  if (end >= 0) Serial.println(buf);
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
