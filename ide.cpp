#include <WiFi.h>
#include <esp_now.h>

// =========================================================
// COLOQUE AQUI O MAC DA OUTRA PLACA!
uint8_t PEER_MAC[6] = { 0x00, 0x70, 0x07, 0x26, 0x7d, 0xbc }; 
// =========================================================

// Função de RECEBIMENTO (Padrão Core 3.x)
void onRecv(const esp_now_recv_info_t *recv_info, const uint8_t *data, int len) {
  // Tudo que chega pelo ar (ESP-NOW), ele joga no cabo USB (Serial)
  Serial.write(data, len);
}

// Função de ENVIO (Padrão Core 3.x corrigido!)
void onSent(const esp_now_send_info_t *info, esp_now_send_status_t status) {
  if (status == ESP_NOW_SEND_SUCCESS) {
     Serial.println("\n[ESP32] Pacote entregue com sucesso no ar!");
  } else {
     Serial.println("\n[ESP32] Falha na entrega (A outra placa esta muito longe ou desligada?)");
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);

  Serial.print("\nMAC DESTA PLACA (Anote para por na outra): ");
  Serial.println(WiFi.macAddress());

  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro ao iniciar ESP-NOW");
    return;
  }

  // Agora ambas as funções estão com as assinaturas corretas
  esp_now_register_recv_cb(onRecv);
  esp_now_register_send_cb(onSent);

  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, PEER_MAC, 6);
  peer.channel = 0;  
  peer.encrypt = false;

  if (esp_now_add_peer(&peer) != ESP_OK) {
    Serial.println("[ERRO] Falha ao registrar o Par ESP-NOW.");
  } else {
    Serial.println("[OK] Par registrado. Pronto! Aguardando dados...");
  }
}

void loop() {
  static String buf;

  // Ouve o cabo USB. O que chegar do Python, ele envia pro ar
  while (Serial.available()) {
    char c = (char)Serial.read();
    buf += c;

    // Se o Python mandou um 'Enter' (\n), ele dispara a mensagem
    if (c == '\n') {
      if (buf.length() <= 250) {
        esp_now_send(PEER_MAC, (const uint8_t*)buf.c_str(), buf.length());
      } else {
        Serial.println("[AVISO] Frame maior que 250 bytes ignorado.");
      }
      buf = "";
    }
  }
}