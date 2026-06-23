import csv
from pathlib import Path


def textToBinary(message: str) -> str:
    return "".join(format(byte, "08b") for byte in message.encode("utf-8"))


def binaryToTrits(binary_message: str, table_path: str = "tabela_8b6t.csv") -> list[int]:
    binary_message = "".join(binary_message.split())

    if any(bit not in "01" for bit in binary_message):
        raise ValueError("Binary message must contain only 0 and 1.")

    if len(binary_message) % 8 != 0:
        raise ValueError("Binary message must have a length multiple of 8.")

    table = {}
    path_to_table = Path(table_path)

    if path_to_table.suffix == ".csv":
        with path_to_table.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for line in reader:
                byte = format(int(line["byte"]), "08b")
                table[byte] = [int(line[f"t{i}"]) for i in range(1, 7)]
    else:
        with path_to_table.open(encoding="utf-8") as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue

                byte = parts[0]
                table[byte] = [
                    -1 if trit == "-" else 1 if trit == "+" else 0
                    for trit in parts[1:7]
                ]

    trits = []
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i : i + 8]
        trits.extend(table[byte])

    return trits


def tritsToBinary(trits: list[int], table_path: str = "tabela_8b6t.csv") -> str:

    if any(trinary not in [-1,0,1] for trinary in trits):
        raise ValueError("Binary message must contain only 0 and 1.")

    if len(trits) % 6 != 0:
        raise ValueError("Trinary message must have a length multiple of 6.")

    table = {}
    path_to_table = Path(table_path)

    if path_to_table.suffix == ".csv":
        with path_to_table.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for line in reader:
                byte = format(int(line["byte"]), "08b")
                table[byte] = [int(line[f"t{i}"]) for i in range(1, 7)]
    else:
        with path_to_table.open(encoding="utf-8") as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue

                byte = parts[0]
                table[byte] = [
                    -1 if trit == "-" else 1 if trit == "+" else 0
                    for trit in parts[1:7]
                ]

    trits = []
    for i in range(0, len(trits), 6):
        byte = trits[i : i + 8]
        trits.extend(table[byte])

    return trits


def encodeMessage(message: str, encode_key: str) -> str:
    '''
    Args: 
    message = Message to be encoded; encode_key = key to encode in Vingenere cipher
    '''
    if not encode_key:
        raise ValueError("Encode key cannot be empty.")

    output = ""

    for i, char in enumerate(message):
        message_value = ord(char)
        key_value = ord(encode_key[i % len(encode_key)])

        encoded_value = (message_value + key_value) % 256

        output += chr(encoded_value)

    return output


def decode_message(encoded_message: str, encode_key: str) -> str:
    if not encode_key:
        raise ValueError("Encode key cannot be empty.")

    output = ""

    for i, char in enumerate(encoded_message):
        encoded_value = ord(char)
        key_value = ord(encode_key[i % len(encode_key)])

        decoded_value = (encoded_value - key_value + 256) % 256

        output += chr(decoded_value)

    return output

