#include <esp_now.h>
#include <WiFi.h>

// A estrutura deve ser idêntica à do emissor
typedef struct struct_message {
    char a[32];
    int b;
    float c;
    bool d;
} struct_message;

struct_message myData;

// CORRIGIDO: Nova assinatura de função para o receptor
void OnDataRecv(const esp_now_recv_info_t *esp_now_info, const uint8_t *incomingData, int len) {
  memcpy(&myData, incomingData, sizeof(myData));
  
  Serial.print("Bytes received: ");
  Serial.println(len);
  Serial.print("Char: ");
  Serial.println(myData.a);
  Serial.print("Int: ");
  Serial.println(myData.b);
  Serial.print("Float: ");
  Serial.println(myData.c);
  Serial.print("Bool: ");
  Serial.println(myData.d);
  Serial.println();
}
 
void setup() {
  Serial.begin(115200);
  
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  
  // Registra o callback diretamente, sem a necessidade de typecast forçado
  esp_now_register_recv_cb(OnDataRecv);
}
 
void loop() {
  // O receptor fica apenas aguardando o callback ser acionado
}