import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time

# --- CONFIGURAÇÃO DA PORTA SERIAL DO RECEPTOR ---
# IMPORTANTE: Mude para a porta do seu ESP32 Receptor (no log era COM3)
PORTA_SERIAL = 'COM3' 
BAUD_RATE = 115200

# Variável global para controle da conexão
ser = None

def iniciar_conexao():
    global ser
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        label_status.config(text=f"Conectado à {PORTA_SERIAL} - Aguardando dados...", fg="green")
        # Inicia a thread que fica lendo a porta serial em segundo plano
        threading.Thread(target=ler_serial, daemon=True).start()
    except Exception as e:
        label_status.config(text=f"Erro ao conectar na {PORTA_SERIAL}", fg="red")
        messagebox.showerror("Erro de Conexão", f"Não foi possível abrir a porta {PORTA_SERIAL}.\nVerifique se o Monitor Serial da Arduino IDE está fechado!")

def ler_serial():
    global ser
    while True:
        if ser and ser.in_waiting > 0:
            try:
                # Lê a linha enviada pelo ESP32 e decodifica
                linha = ser.readline().decode('utf-8').strip()
                
                # Só processa se houver conteúdo
                if linha:
                    # Fatiando os dados separados por ";"
                    dados = linha.split(';')
                    
                    # Atualiza a interface gráfica com os dados recebidos
                    if len(dados) == 4:
                        # Usamos o método .after() do Tkinter para atualizar a interface
                        # a partir de uma thread secundária de forma segura
                        root.after(0, atualizar_interface, dados)
            except Exception as e:
                print(f"Erro de leitura: {e}")
        time.sleep(0.01) # Pequeno delay para não sobrecarregar a CPU

def atualizar_interface(dados):
    texto, inteiro, decimal, booleano = dados
    
    # Atualiza os rótulos na tela
    valor_char.config(text=texto)
    valor_int.config(text=inteiro)
    valor_float.config(text=decimal)
    
    # Transforma '1'/'0' de volta para 'Ativado'/'Desativado'
    estado_bool = "Ativado (True)" if booleano == '1' else "Desativado (False)"
    valor_bool.config(text=estado_bool)

# --- CONSTRUÇÃO DA INTERFACE GRÁFICA (GUI) ---
root = tk.Tk()
root.title("Monitor ESP-NOW Receptor")
root.geometry("400x350")
root.configure(padx=20, pady=20)

tk.Label(root, text="Dados Recebidos do ESP-NOW", font=("Arial", 14, "bold")).pack(pady=(0, 20))

# Frames para organizar o layout
frame_dados = tk.Frame(root)
frame_dados.pack(fill="x")

# Linhas de Dados
tk.Label(frame_dados, text="Texto:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="e", pady=5)
valor_char = tk.Label(frame_dados, text="---", font=("Arial", 12), fg="blue")
valor_char.grid(row=0, column=1, sticky="w", padx=10, pady=5)

tk.Label(frame_dados, text="Inteiro:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="e", pady=5)
valor_int = tk.Label(frame_dados, text="---", font=("Arial", 12), fg="blue")
valor_int.grid(row=1, column=1, sticky="w", padx=10, pady=5)

tk.Label(frame_dados, text="Decimal:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="e", pady=5)
valor_float = tk.Label(frame_dados, text="---", font=("Arial", 12), fg="blue")
valor_float.grid(row=2, column=1, sticky="w", padx=10, pady=5)

tk.Label(frame_dados, text="Booleano:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="e", pady=5)
valor_bool = tk.Label(frame_dados, text="---", font=("Arial", 12), fg="blue")
valor_bool.grid(row=3, column=1, sticky="w", padx=10, pady=5)

# Status
label_status = tk.Label(root, text="Inicializando...", fg="gray", font=("Arial", 10))
label_status.pack(side="bottom", pady=20)

# Inicia a conexão serial logo após desenhar a interface
root.after(500, iniciar_conexao)

root.mainloop()