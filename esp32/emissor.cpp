#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>

// MAC da recetora MASTER
uint8_t broadcastAddress[] = {0x00, 0x70, 0x07, 0x25, 0x36, 0xa0}; 

// Estrutura simplificada: apenas um grande buffer para a string do Python
typedef struct struct_message {
  char payload[240]; 
} struct_message;

struct_message myData;
esp_now_peer_info_t peerInfo;

void OnDataSent(const wifi_tx_info_t *tx_info, esp_now_send_status_t status) {
  if (status == ESP_NOW_SEND_SUCCESS) {
    Serial.println("ESP_NOW_OK");
  } else {
    Serial.println("ESP_NOW_FAIL");
  }
}
 
void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  esp_wifi_set_ps(WIFI_PS_NONE);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  if (esp_now_init() != ESP_OK) {
    return;
  }

  esp_now_register_send_cb(OnDataSent);
  
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 1;
  peerInfo.encrypt = false;
  
  esp_now_add_peer(&peerInfo);
}
 
void loop() {
  // Verifica se o Python (main.py) enviou algo via Serial
  if (Serial.available() > 0) {
    // Lê a linha até a quebra de linha (\n)
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove espaços vazios ou \r
    
    if (input.length() > 0) {
      // Copia a string recebida para a nossa estrutura, garantindo o limite de 239 chars + nulo
      strncpy(myData.payload, input.c_str(), sizeof(myData.payload) - 1);
      myData.payload[sizeof(myData.payload) - 1] = '\0';
      
      // Envia o pacote via ESP-NOW
      esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
    }
  }
}