# Contrato de comunicação Serial e ESP-NOW

Este arquivo define o contrato mínimo entre GUI, ESP32 Slave, ESP32 Master e GUI Master.

## 1. Baud rate

Usar:

```text
115200
```

## 2. Formato da mensagem serial

A mensagem deve ser uma linha de texto terminada em `\n`.

Formato:

```text
TRITS:<trit_1>,<trit_2>,<trit_3>,...,<trit_n>\n
```

Exemplo:

```text
TRITS:-1,0,1,1,0,-1,0,0,1,1,-1,0\n
```

## 3. Valores válidos

Cada trit pode ser apenas:

```text
-1
0
1
```

A quantidade total de trits deve ser múltipla de 6, porque o 8B6T transforma cada byte de 8 bits em 6 trits.

## 4. Responsabilidade do emissor Python

O emissor deve enviar apenas a lista final de trits.

Exemplo:

```python
payload = "TRITS:" + ",".join(str(t) for t in trits) + "\n"
ser.write(payload.encode("utf-8"))
```

## 5. Responsabilidade do ESP32 Slave

O ESP32 Slave deve encaminhar o payload sem alterar.

Pseudocódigo:

```cpp
if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line += "\n";
    esp_now_send(masterMac, (uint8_t*) line.c_str(), line.length());
}
```

## 6. Responsabilidade do ESP32 Master

O ESP32 Master deve imprimir na Serial o payload recebido.

Pseudocódigo:

```cpp
void onDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len) {
    String line = "";
    for (int i = 0; i < len; i++) {
        line += (char) incomingData[i];
    }
    line.trim();
    Serial.println(line);
}
```

## 7. Responsabilidade do receptor Python

O receptor deve:

1. Ler uma linha da Serial.
2. Verificar se começa com `TRITS:`.
3. Separar os valores por vírgula.
4. Converter para `list[int]`.
5. Decodificar usando `encode.py`.

Exemplo:

```python
def parse_trits_line(line: str) -> list[int]:
    line = line.strip()

    if not line.startswith("TRITS:"):
        raise ValueError("Invalid line: expected TRITS: prefix")

    raw_values = line.removeprefix("TRITS:").split(",")
    trits = [int(value.strip()) for value in raw_values if value.strip()]

    if not trits:
        raise ValueError("Empty trits payload")

    if any(t not in (-1, 0, 1) for t in trits):
        raise ValueError("Invalid trit value")

    if len(trits) % 6 != 0:
        raise ValueError("Trit count must be multiple of 6")

    return trits
```

## 8. Tamanho do payload

ESP-NOW possui limite prático pequeno de payload. Se uma mensagem grande ultrapassar o limite, implementar envio em partes depois.

Para a primeira versão, limitar a mensagem no front emissor para um tamanho pequeno, por exemplo:

```text
até 30 caracteres
```

Motivo: cada byte vira 6 trits. Como o formato textual `-1,0,1,...` cresce bastante, mensagens grandes podem estourar o payload do ESP-NOW.

## 9. Solução simples para mensagens maiores

Se precisar enviar mensagens maiores, dividir em pacotes:

```text
TRITS_PART:<id>:<parte_atual>:<total_partes>:<trits...>
```

Mas não implementar isso agora se a versão simples funcionar.

