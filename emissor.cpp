#include <esp_now.h>
#include <WiFi.h>

//EMISSOR SLAVE
uint8_t broadcastAddress[] = {0x00, 0x70, 0x07, 0x25, 0x36, 0xa0}; // MAC da recetora MASTER

typedef struct struct_message {
  char a[32];
  int b;
  float c;
  bool d;
} struct_message;

struct_message myData;
esp_now_peer_info_t peerInfo;

void OnDataSent(const wifi_tx_info_t *tx_info, esp_now_send_status_t status) {
  // Retorno opcional para o Python saber se o ESP-NOW entregou com sucesso
  if (status == ESP_NOW_SEND_SUCCESS) {
    Serial.println("ESP_NOW_OK");
  } else {
    Serial.println("ESP_NOW_FAIL");
  }
}
 
void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    return;
  }

  esp_now_register_send_cb(OnDataSent);
  
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  esp_now_add_peer(&peerInfo);
}
 
void loop() {
  // Verifica se o Python enviou algo via Serial
  if (Serial.available() > 0) {
    // Lê a linha enviada pelo Python até o '\n'
    String input = Serial.readStringUntil('\n');
    
    // Converte para array de char para podermos usar o strtok (separador)
    char buf[128];
    input.toCharArray(buf, sizeof(buf));
    
    // Separa os dados usando ";" como delimitador
    char* token = strtok(buf, ";");
    if (token != NULL) strcpy(myData.a, token);   // Texto
    
    token = strtok(NULL, ";");
    if (token != NULL) myData.b = atoi(token);     // Inteiro
    
    token = strtok(NULL, ";");
    if (token != NULL) myData.c = atof(token);     // Float
    
    token = strtok(NULL, ";");
    if (token != NULL) myData.d = (atoi(token) == 1); // Bool (1 ou 0)
    
    // Envia o pacote estruturado via ESP-NOW
    esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
  }
}