# Checklist de testes para o Codex

Use este checklist para validar a implementação sem complicar o projeto.

## 1. Testes do `encode.py`

Criar ou rodar testes manuais em Python:

```python
from encode import (
    encodeMessage,
    decode_message,
    textToBinary,
    binaryToText,
    binaryToTrits,
    tritsToBinary,
)

message = "TESTE"
key = "ABC"

encrypted = encodeMessage(message, key)
binary = textToBinary(encrypted)
trits = binaryToTrits(binary)
recovered_binary = tritsToBinary(trits)
recovered_encrypted = binaryToText(recovered_binary)
recovered_message = decode_message(recovered_encrypted, key)

assert recovered_message == message
print("OK")
```

Também testar com caracteres acentuados:

```python
message = "OLÁ ÇÃO"
key = "SENHA"
```

## 2. Teste sem ESP32

Antes de usar ESP-NOW, testar somente o receptor Python com uma linha simulada:

```text
TRITS:-1,0,1,1,0,-1
```

O receptor deve:

- reconhecer o prefixo `TRITS:`;
- converter para lista `[-1, 0, 1, 1, 0, -1]`;
- rejeitar valores inválidos;
- rejeitar tamanho que não seja múltiplo de 6.

## 3. Teste Serial do ESP32 Slave

Subir o firmware Slave e abrir o Monitor Serial.

Enviar manualmente:

```text
TRITS:-1,0,1,1,0,-1
```

Esperado:

- O ESP32 Slave deve informar que recebeu a linha.
- O ESP32 Slave deve tentar enviar via ESP-NOW.
- Deve aparecer status de envio.

## 4. Teste Serial do ESP32 Master

Subir o firmware Master e abrir o Monitor Serial.

Quando o Slave enviar:

```text
TRITS:-1,0,1,1,0,-1
```

O Master deve imprimir exatamente:

```text
TRITS:-1,0,1,1,0,-1
```

## 5. Teste ponta a ponta

Com tudo conectado:

1. Abrir GUI Master.
2. Conectar na porta serial do ESP32 Master.
3. Abrir GUI Slave.
4. Conectar na porta serial do ESP32 Slave.
5. Digitar mensagem e chave.
6. Enviar.
7. Verificar se a GUI Master exibiu a mensagem original.

## 6. Erros comuns

### Porta serial errada no Ubuntu

Usar:

```text
/dev/ttyACM0
```

ou:

```text
/dev/ttyUSB0
```

Não usar:

```text
tty/ACM0
```

### Permissão negada na Serial

Rodar:

```bash
sudo usermod -aG dialout $USER
```

Depois sair e entrar de novo na sessão.

### Monitor Serial aberto

Fechar o Monitor Serial da Arduino IDE antes de abrir a GUI Python.

### Python com pacote serial faltando

Usar o mesmo Python no qual o `pyserial` foi instalado.

Teste:

```bash
python3 -c "import serial; print(serial.__version__)"
```

## 7. Critério final de aprovação

O teste final passa quando:

```text
mensagem enviada no Slave == mensagem exibida no Master
```

usando a mesma chave nos dois lados.

