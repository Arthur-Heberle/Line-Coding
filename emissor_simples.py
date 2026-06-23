import serial
import time

# Troque para a porta do SEU computador
PORTA = 'COM4' 
VELOCIDADE = 115200

try:
    print(f"Conectando na {PORTA}...")
    esp32 = serial.Serial(PORTA, VELOCIDADE, timeout=1)
    time.sleep(2) # Dá um tempo para a placa reiniciar
    
    print("\n=== TERMINAL DE ENVIO ESP-NOW ===")
    print("Digite 'sair' para encerrar.")
    
    while True:
        mensagem = input("\nO que você quer enviar? > ")
        
        if mensagem.lower() == 'sair':
            break
            
        # O '\n' no final é OBRIGATÓRIO! É ele que avisa a placa que a frase acabou.
        comando = mensagem + '\n' 
        
        # Envia pelo cabo USB
        esp32.write(comando.encode('utf-8'))
        print("Mensagem injetada no cabo USB! Aguardando confirmacao da placa...")
        
        # Espera meio segundo para dar tempo da ESP32 mandar pro ar e responder o status
        time.sleep(0.5)
        
        # Lê a resposta da placa (sucesso ou falha)
        while esp32.in_waiting > 0:
            resposta = esp32.readline().decode('utf-8').strip()
            if resposta:
                print(resposta)

    esp32.close()
    
except Exception as e:
    print(f"Erro: {e}")
    print("Lembre-se de fechar o Monitor Serial do Arduino!")