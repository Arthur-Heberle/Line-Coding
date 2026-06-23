# Prompt para o Codex — Implementação simples do projeto ESP-NOW + 8B6T

Você está trabalhando no projeto de Comunicação de Dados da UTFPR. O objetivo é deixar o sistema funcionando de forma simples, sem refatorações grandes e sem criar arquitetura complexa.

## Contexto do projeto

O projeto implementa uma rede com **3 ESP32**:

- **ESP32 Slave 1**: emissor.
- **ESP32 Slave 2**: emissor.
- **ESP32 Master**: receptor.

Cada ESP32 se comunica com um computador por **Serial/USB**. Os ESP32 se comunicam entre si por **ESP-NOW**.

O pipeline lógico é:

```text
Mensagem original
→ Cifra de Vigenère usando chave pré-compartilhada
→ Conversão para binário usando ASCII estendido / bytes
→ Codificação 8B6T
→ Lista de trits {-1, 0, +1}
→ Envio Serial para ESP32 Slave
→ Envio via ESP-NOW para ESP32 Master
→ Repasse Serial para PC Master
→ Receptor Python recupera trits
→ Decodificação 8B6T
→ Binário
→ Texto criptografado
→ Decifra Vigenère com a mesma chave
→ Mensagem original
```

## Estado atual esperado do projeto

Já existe:

- `encode.py`, que concentra as funções de codificação/decodificação.
- Um front/interface para o lado emissor.

Você deve reaproveitar isso e evitar duplicar lógica.

## Objetivo da implementação

Implementar o mínimo necessário para o projeto funcionar de ponta a ponta:

1. Garantir que `encode.py` tenha todas as funções necessárias funcionando.
2. Implementar ou ajustar a interface receptora do Master.
3. Implementar firmware ESP32 Slave para receber linha via Serial e enviar via ESP-NOW.
4. Implementar firmware ESP32 Master para receber via ESP-NOW e imprimir a linha na Serial.
5. Definir um protocolo serial simples e estável.

## Regra principal

Não implemente criptografia, 8B6T ou decodificação dentro do ESP32.

Os ESP32 devem funcionar apenas como ponte:

```text
PC Slave → Serial → ESP32 Slave → ESP-NOW → ESP32 Master → Serial → PC Master
```

Toda a inteligência fica no Python.

## O que fazer no `encode.py`

Verifique se existem estas funções:

```python
def encodeMessage(message: str, encode_key: str) -> str: ...
def decode_message(encoded_message: str, encode_key: str) -> str: ...
def textToBinary(message: str) -> str: ...
def binaryToTrits(binary_message: str, table_path: str = "") -> list[int]: ...
def tritsToBinary(trits: list[int], table_path: str = "") -> str: ...
def binaryToText(binary_message: str) -> str: ...
```

Se alguma estiver ausente, implemente.

### Correção importante

A função `tritsToBinary` deve:

- Receber uma lista de trits.
- Validar que o tamanho da lista é múltiplo de 6.
- Ler a mesma tabela 8B6T usada pela codificação.
- Inverter a tabela: `tuple(trits) -> byte_binario`.
- Processar os trits em blocos de 6, não em blocos de 8.
- Não sobrescrever a variável `trits` dentro do laço.

Exemplo de lógica esperada:

```python
for i in range(0, len(trits), 6):
    bloco = tuple(trits[i:i + 6])
    binary += inverse_table[bloco]
```

## Protocolo serial simples

Use uma linha de texto terminada com `\n`.

Formato recomendado:

```text
TRITS:-1,0,1,1,0,-1,0,0,1\n
```

Regras:

- O emissor Python envia exatamente esse formato para o ESP32 Slave.
- O ESP32 Slave envia o mesmo conteúdo via ESP-NOW.
- O ESP32 Master imprime o mesmo conteúdo na Serial.
- O receptor Python lê a linha, remove `TRITS:` e converte para `list[int]`.

Não envie a chave pela rede. A chave deve ser digitada/configurada no emissor e no receptor.

## Interface receptora do Master

Criar uma interface simples, podendo usar o mesmo padrão do front emissor já existente.

Campos mínimos:

- Porta serial, exemplo: `/dev/ttyACM0` ou `/dev/ttyUSB0`.
- Baud rate, padrão `115200`.
- Chave de decodificação.
- Botão conectar/desconectar.
- Área para exibir:
  - linha recebida bruta;
  - trits recebidos;
  - binário recuperado;
  - texto criptografado recuperado;
  - mensagem final descriptografada.

Se o projeto já usa `PySide6` e `pyqtgraph`, mantenha esse padrão. Caso o receptor atual esteja em Tkinter, pode manter Tkinter se isso for mais rápido e simples.

## Firmware ESP32 Slave

Criar firmware simples:

- Inicializar Serial em `115200`.
- Inicializar WiFi em modo `WIFI_STA`.
- Inicializar ESP-NOW.
- Cadastrar o MAC do ESP32 Master como peer.
- Ler uma linha da Serial até `\n`.
- Enviar a linha inteira via `esp_now_send`.
- Mostrar logs simples na Serial.

O mesmo firmware pode ser usado nos dois slaves, mudando apenas alguma identificação opcional.

## Firmware ESP32 Master

Criar firmware simples:

- Inicializar Serial em `115200`.
- Inicializar WiFi em modo `WIFI_STA`.
- Inicializar ESP-NOW.
- Registrar callback de recebimento.
- Ao receber payload ESP-NOW, converter para string e imprimir na Serial com `Serial.println`.

O Master não deve decodificar nada.

## Critérios de aceite

O projeto estará funcionando quando:

1. O emissor aceitar uma mensagem e uma chave.
2. O emissor gerar trits usando `encode.py`.
3. O emissor enviar `TRITS:...` via Serial.
4. O ESP32 Slave encaminhar via ESP-NOW.
5. O ESP32 Master imprimir a mesma linha na Serial.
6. A interface receptora ler a linha.
7. A interface receptora converter trits para binário.
8. A interface receptora recuperar o texto criptografado.
9. A interface receptora decifrar usando a chave.
10. A mensagem final exibida no receptor ser igual à mensagem original.

## Não fazer

- Não criar backend web.
- Não usar banco de dados.
- Não criar autenticação.
- Não enviar chave junto com a mensagem.
- Não reescrever o front emissor se ele já funciona.
- Não colocar lógica de Vigenère ou 8B6T no ESP32.
- Não refatorar o projeto inteiro.

