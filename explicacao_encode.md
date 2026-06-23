# Explicacao do arquivo `encode.py`

O arquivo `encode.py` concentra as funcoes usadas para transformar uma mensagem de texto em uma forma codificada. Ele trabalha com tres etapas principais: cifrar a mensagem com uma chave, transformar o resultado em binario e representar esse binario em valores ternarios chamados trits.

Neste documento, a funcao `binaryToTrits` nao sera detalhada, conforme solicitado.

## Importacoes

O arquivo comeca importando dois recursos:

```python
import csv
from pathlib import Path
```

O modulo `csv` e usado para ler a tabela `tabela_8b6t.csv`, que relaciona bytes com sequencias de trits. Ja `Path`, da biblioteca `pathlib`, facilita o tratamento do caminho do arquivo da tabela.

## Funcao `textToBinary`

```python
def textToBinary(message: str) -> str:
    return "".join(format(byte, "08b") for byte in message.encode("utf-8"))
```

A funcao `textToBinary` recebe uma mensagem em texto e retorna uma string binaria.

Primeiro, a mensagem e codificada em UTF-8 com `message.encode("utf-8")`. Isso transforma cada caractere em um ou mais bytes. Depois, cada byte e convertido para uma representacao binaria de 8 bits usando `format(byte, "08b")`.

Por exemplo, a letra `A` em UTF-8 corresponde ao valor decimal `65`. Em binario de 8 bits, esse valor vira:

```text
01000001
```

Se a mensagem tiver varios caracteres, a funcao junta todos os grupos de 8 bits em uma unica string.

## Cifra de Vigenere no arquivo

O arquivo implementa uma versao da cifra de Vigenere nas funcoes `encodeMessage` e `decode_message`.

A cifra de Vigenere tradicional usa uma chave repetida ao longo da mensagem. Cada caractere da chave define um deslocamento aplicado ao caractere correspondente da mensagem. No `encode.py`, esse mesmo principio aparece, mas usando valores numericos dos caracteres e operando no intervalo de 0 a 255.

Esse intervalo representa um byte. Por isso, a operacao usa modulo 256.

## Funcao `encodeMessage`

```python
def encodeMessage(message: str, encode_key: str) -> str:
```

A funcao `encodeMessage` recebe uma mensagem e uma chave de codificacao.

Antes de cifrar, ela verifica se a chave esta vazia:

```python
if not encode_key:
    raise ValueError("Encode key cannot be empty.")
```

Essa validacao e importante porque a chave e usada repetidamente durante a cifra. Sem chave, nao existe deslocamento a aplicar.

Depois, a funcao percorre cada caractere da mensagem:

```python
for i, char in enumerate(message):
```

Para cada caractere, ela calcula:

```python
message_value = ord(char)
key_value = ord(encode_key[i % len(encode_key)])
```

`ord(char)` transforma o caractere em seu valor numerico Unicode. A expressao `i % len(encode_key)` faz a chave repetir quando ela e menor que a mensagem.

Em seguida, a codificacao e feita por soma:

```python
encoded_value = (message_value + key_value) % 256
```

O valor do caractere da mensagem e somado ao valor do caractere da chave. O `% 256` garante que o resultado fique dentro do intervalo de um byte.

Por fim, `chr(encoded_value)` transforma o numero resultante de volta em caractere, e esse caractere e adicionado ao texto cifrado.

## Funcao `decode_message`

```python
def decode_message(encoded_message: str, encode_key: str) -> str:
```

A funcao `decode_message` faz o processo inverso da `encodeMessage`.

Ela tambem exige que a chave nao esteja vazia:

```python
if not encode_key:
    raise ValueError("Encode key cannot be empty.")
```

Depois, percorre cada caractere da mensagem cifrada e pega o caractere correspondente da chave, repetindo a chave quando necessario.

A diferenca principal esta na operacao:

```python
decoded_value = (encoded_value - key_value + 256) % 256
```

Na codificacao, o valor da chave e somado. Na decodificacao, ele e subtraido. O `+ 256` evita resultados negativos antes da aplicacao do modulo.

Assim, se a mesma chave usada para codificar for usada para decodificar, a mensagem original e recuperada.

## Codificacao em trits

Depois que uma mensagem e cifrada e convertida para binario, o projeto trabalha com trits.

Um trit e um digito ternario. Enquanto um bit pode assumir apenas dois valores, `0` ou `1`, um trit pode assumir tres valores. No `encode.py`, esses valores sao representados como:

```text
-1, 0, 1
```

Esses tres valores tambem podem ser visualizados como niveis de sinal:

```text
-1  -> nivel negativo
 0  -> nivel neutro
 1  -> nivel positivo
```

Essa representacao e util para codificacao de linha, pois a informacao binaria passa a ser expressa como uma sequencia de amplitudes ternarias.

## Tabela 8B6T

O projeto usa uma tabela chamada `tabela_8b6t.csv`.

O nome 8B6T indica a ideia central da conversao:

```text
8 bits -> 6 trits
```

Ou seja, cada byte da mensagem binaria, formado por 8 bits, e associado a uma sequencia de 6 trits.

Um byte como:

```text
01000001
```

pode ser associado, pela tabela, a uma sequencia de seis valores ternarios. A tabela e necessaria porque essa associacao nao e calculada diretamente por uma formula simples no restante do arquivo: ela e consultada a partir de um arquivo externo.

## Trits e TALS

No contexto deste projeto, os trits representam os valores logicos ternarios. Os TALS podem ser entendidos como a forma de sinal correspondente a esses valores, isto e, os niveis eletricos ou amplitudes usados para representar cada trit.

Assim:

```text
trit  1  -> amplitude positiva
trit  0  -> amplitude zero/neutra
trit -1  -> amplitude negativa
```

Essa ideia aparece tambem na interface do projeto, que desenha uma forma de onda usando os trits. Cada trit vira um trecho do sinal em um dos tres niveis possiveis.

## Funcao `tritsToBinary`

```python
def tritsToBinary(trits: list[int], table_path: str = "tabela_8b6t.csv") -> str:
```

A funcao `tritsToBinary` parece ter a intencao de realizar o caminho inverso: receber uma sequencia de trits e reconstruir a informacao binaria original.

Ela comeca validando se todos os valores recebidos pertencem ao conjunto ternario esperado:

```python
if any(trinary not in [-1,0,1] for trinary in trits):
```

Depois, verifica se a quantidade de trits e multipla de 6:

```python
if len(trits) % 6 != 0:
```

Essa validacao faz sentido porque a codificacao 8B6T trabalha com blocos de 6 trits para representar cada byte.

A funcao tambem le a mesma tabela externa usada na conversao entre bytes e trits. Se o arquivo for `.csv`, ela usa `csv.DictReader`. Caso contrario, ela le um formato textual em que os sinais `-`, `+` e `0` sao convertidos para `-1`, `1` e `0`.

Porem, do jeito que esta escrita, a parte final da funcao parece incompleta ou incorreta, porque reutiliza a variavel `trits` como lista de saida e tenta consultar a tabela usando fatias da propria lista. A intencao geral e clara, mas a implementacao nao reconstruiu efetivamente o binario.

## Fluxo geral do `encode.py`

O fluxo esperado do arquivo pode ser entendido assim:

```text
mensagem original
        |
        v
cifra de Vigenere com chave
        |
        v
texto cifrado
        |
        v
conversao para binario UTF-8
        |
        v
bytes em grupos de 8 bits
        |
        v
representacao ternaria em trits pela tabela 8B6T
        |
        v
sinal ternario com niveis -1, 0 e 1
```

Portanto, o `encode.py` combina criptografia simples com uma etapa de codificacao de linha. A cifra de Vigenere protege ou embaralha a mensagem, enquanto a codificacao 8B6T transforma os bytes resultantes em trits que podem ser representados como uma forma de onda ternaria.
