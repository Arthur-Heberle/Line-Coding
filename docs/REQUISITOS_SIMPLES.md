# Requisitos simples do projeto

Este arquivo resume apenas o necessário para implementar o sistema de forma funcional.

## 1. Arquitetura

O sistema possui:

```text
GUI Slave 1 → Serial → ESP32 Slave 1 ┐
                                      ├→ ESP-NOW → ESP32 Master → Serial → GUI Master
GUI Slave 2 → Serial → ESP32 Slave 2 ┘
```

Cada Slave pode enviar mensagens para o Master. Se os dois Slaves tiverem a mesma chave pré-compartilhada, ambos conseguem produzir mensagens que o Master decodifica.

## 2. Responsabilidades

### Python emissor

Responsável por:

- Receber mensagem e chave do usuário.
- Chamar funções do `encode.py`.
- Mostrar mensagem original, mensagem criptografada, binário, trits e forma de onda.
- Enviar os trits para o ESP32 Slave via Serial.

### ESP32 Slave

Responsável apenas por:

- Receber uma linha via Serial.
- Enviar essa linha para o ESP32 Master via ESP-NOW.

### ESP32 Master

Responsável apenas por:

- Receber payload via ESP-NOW.
- Imprimir payload recebido na Serial.

### Python receptor / GUI Master

Responsável por:

- Ler linha recebida pela Serial.
- Converter linha para lista de trits.
- Exibir trits e forma de onda.
- Chamar `tritsToBinary`.
- Converter binário para texto criptografado.
- Chamar `decode_message` com a chave digitada.
- Exibir mensagem original recuperada.

## 3. Funções esperadas no `encode.py`

O arquivo `encode.py` deve ser o único lugar com lógica de codificação.

Funções esperadas:

```python
encodeMessage(message: str, encode_key: str) -> str
decode_message(encoded_message: str, encode_key: str) -> str
textToBinary(message: str) -> str
binaryToText(binary_message: str) -> str
binaryToTrits(binary_message: str, table_path: str = "") -> list[int]
tritsToBinary(trits: list[int], table_path: str = "") -> str
```

## 4. Fluxo de codificação no emissor

```python
encrypted = encodeMessage(message, key)
binary = textToBinary(encrypted)
trits = binaryToTrits(binary)
serial_payload = "TRITS:" + ",".join(map(str, trits)) + "\n"
serial.write(serial_payload.encode("utf-8"))
```

## 5. Fluxo de decodificação no receptor

```python
line = serial.readline().decode("utf-8", errors="replace").strip()

if line.startswith("TRITS:"):
    raw = line.removeprefix("TRITS:")
    trits = [int(x) for x in raw.split(",") if x.strip()]

    binary = tritsToBinary(trits)
    encrypted = binaryToText(binary)
    message = decode_message(encrypted, key)
```

## 6. Validações mínimas

A implementação deve validar:

- Chave não pode ser vazia.
- Linha recebida deve começar com `TRITS:`.
- Cada trit deve ser `-1`, `0` ou `1`.
- Quantidade de trits deve ser múltipla de 6.
- String binária deve conter apenas `0` e `1`.
- Tamanho da string binária deve ser múltiplo de 8.

## 7. Dependências Python

Usar apenas o necessário:

```text
pyserial
PySide6 opcional, se o front já usa
pyqtgraph opcional, se for mostrar forma de onda
```

Para instalação local no Ubuntu, preferir ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyserial PySide6 pyqtgraph
```

## 8. Resultado esperado

Ao enviar:

```text
Mensagem: TESTE
Chave: ABC
```

O receptor deve exibir:

```text
Mensagem final: TESTE
```

A forma de onda deve ser reconstruída a partir da mesma lista de trits recebida.

