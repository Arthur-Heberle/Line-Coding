#include <esp_now.h>
#include <WiFi.h>

// RECEPTOR MASTER
typedef struct struct_message {
    char a[32];
    int b;
    float c;
    bool d;
} struct_message;

struct_message myData;

void OnDataRecv(const esp_now_recv_info_t *esp_now_info, const uint8_t *incomingData, int len) {
  memcpy(&myData, incomingData, sizeof(myData));
  
  // Imprime os dados em formato "CSV" (separados por ponto e vírgula)
  // Exemplo de saída no Serial: Mensagem;100;25.40;1
  Serial.print(myData.a);
  Serial.print(";");
  Serial.print(myData.b);
  Serial.print(";");
  Serial.print(myData.c);
  Serial.print(";");
  Serial.println(myData.d); // println no último para gerar a quebra de linha (\n)
}
 
void setup() {
  // A mesma velocidade que usaremos no Python
  Serial.begin(115200);
  
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    // Evitamos printar textos de erro longos para não confundir o leitor do Python
    return;
  }
  
  esp_now_register_recv_cb(OnDataRecv);
}
 
void loop() {
  // O receptor fica apenas aguardando o callback
}
