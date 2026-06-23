import serial
import time

# Troque para a porta do computador do SEU AMIGO
PORTA = '/dev/ttyACM0' 
VELOCIDADE = 115200

try:
    print(f"Conectando na {PORTA}...")
    esp32 = serial.Serial(PORTA, VELOCIDADE, timeout=1)
    time.sleep(2)
    
    print("\n=== TERMINAL DE RECEPCAO ESP-NOW ===")
    print("Aguardando mensagens vindas do ar...\n")
    
    while True:
        # Verifica se tem alguma coisa chegando pelo cabo USB (vinda do ar)
        if esp32.in_waiting > 0:
            # Lê até encontrar a quebra de linha (\n)
            mensagem_recebida = esp32.readline().decode('utf-8').strip()
            
            # Como a placa pode cuspir mensagens de log, vamos ignorar logs e focar no dado
            if not mensagem_recebida.startswith("[ESP32]") and not mensagem_recebida.startswith("MAC"):
                print(f"🚀 MENSAGEM RECEBIDA DO AMIGO: {mensagem_recebida}")
                
except KeyboardInterrupt:
    esp32.close()
    print("\nReceptor encerrado.")
except Exception as e:
    print(f"Erro: {e}")