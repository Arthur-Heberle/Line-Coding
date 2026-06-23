import tkinter as tk
from tkinter import messagebox
import serial
import time

# --- CONFIGURAÇÃO DA PORTA SERIAL ---
# IMPORTANTE: Mude para a porta do seu ESP32 Emissor (no seu log era a COM4)
PORTA_SERIAL = 'COM4' 
BAUD_RATE = 115200

try:
    # Inicializa a porta serial
    ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    time.sleep(2) # Aguarda o ESP32 reiniciar após a conexão
    print(f"Conectado com sucesso na porta {PORTA_SERIAL}")
except Exception as e:
    print(f"Erro ao abrir a porta {PORTA_SERIAL}: {e}")
    ser = None

# --- FUNÇÃO DE ENVIO ---
def enviar_dados():
    if not ser:
        messagebox.showerror("Erro", "A porta Serial não está conectada!")
        return
    
    # Coleta os dados da interface gráfica
    texto = entry_char.get()
    
    try:
        inteiro = int(entry_int.get())
        flutuante = float(entry_float.get())
    except ValueError:
        messagebox.showerror("Erro", "Insira valores numéricos válidos para Int e Float!")
        return
        
    booleano = 1 if var_bool.get() else 0
    
    # Formata a string exatamente como o ESP32 espera: Texto;Int;Float;Bool\n
    string_envio = f"{texto};{inteiro};{flutuante};{booleano}\n"
    
    # Envia os dados codificados em UTF-8
    ser.write(string_envio.encode('utf-8'))
    label_status.config(text="Dados enviados para o ESP32 Emissor!", fg="green")

# --- CONSTRUÇÃO DA INTERFACE GRÁFICA (GUI) ---
root = tk.Tk()
root.title("Controle ESP-NOW via Python")
root.geometry("400x300")

# Elementos da Tela
tk.Label(root, text="Enviar dados para o ESP32", font=("Arial", 14, "bold")).pack(pady=10)

# Campo Char (Texto)
tk.Label(root, text="Texto (char a[32]):").pack()
entry_char = tk.Entry(root, width=30)
entry_char.insert(0, "Mensagem do Python")
entry_char.pack(pady=2)

# Campo Int
tk.Label(root, text="Inteiro (int b):").pack()
entry_int = tk.Entry(root, width=30)
entry_int.insert(0, "100")
entry_int.pack(pady=2)

# Campo Float
tk.Label(root, text="Decimal (float c):").pack()
entry_float = tk.Entry(root, width=30)
entry_float.insert(0, "25.4")
entry_float.pack(pady=2)

# Campo Bool
var_bool = tk.BooleanVar()
chk_bool = tk.Checkbutton(root, text="Ativar Booleano (bool d)", variable=var_bool)
chk_bool.pack(pady=5)

# Botão Enviar
btn_enviar = tk.Button(root, text="TRANSMITIR", command=enviar_dados, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
btn_enviar.pack(pady=10)

# Status
label_status = tk.Label(root, text="Aguardando envio...", fg="gray")
label_status.pack()

root.mainloop()