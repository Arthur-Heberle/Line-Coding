import csv
from pathlib import Path


def texto_para_binario(mensagem: str) -> str:
    return "".join(format(byte, "08b") for byte in mensagem.encode("utf-8"))


def binario_para_trits(mensagem_binaria: str, tabela_path: str = "tabela_8b6t.csv") -> list[int]:
    binario = "".join(mensagem_binaria.split())

    if any(bit not in "01" for bit in binario):
        raise ValueError("A mensagem binaria deve conter apenas 0 e 1.")

    if len(binario) % 8 != 0:
        raise ValueError("A mensagem binaria deve ter tamanho multiplo de 8.")

    tabela = {}
    caminho_tabela = Path(tabela_path)

    if caminho_tabela.suffix == ".csv":
        with caminho_tabela.open(newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                byte = format(int(linha["byte"]), "08b")
                tabela[byte] = [int(linha[f"t{i}"]) for i in range(1, 7)]
    else:
        with caminho_tabela.open(encoding="utf-8") as arquivo:
            for linha in arquivo:
                partes = linha.split()
                if not partes:
                    continue

                byte = partes[0]
                tabela[byte] = [
                    -1 if trit == "-" else 1 if trit == "+" else 0
                    for trit in partes[1:7]
                ]

    trits = []
    for i in range(0, len(binario), 8):
        byte = binario[i : i + 8]
        trits.extend(tabela[byte])

    return trits

if __name__ == "__main__":
    while True:
        mensagem = input("Digite a mensagem: ")
        binario = texto_para_binario(mensagem)
        trits = binario_para_trits(binario)
        print(binario)
        print(trits)