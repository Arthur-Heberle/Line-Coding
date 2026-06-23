import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl

from encode import encodeMessage, textToBinary, binaryToTrits


class Encoder(QObject):
    dataChanged   = Signal()
    errorOccurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._encrypted = ""
        self._binary    = ""
        self._trits: list = []

    @Property(str, notify=dataChanged)
    def encrypted(self) -> str:
        return self._encrypted

    @Property(str, notify=dataChanged)
    def binary(self) -> str:
        return self._binary

    @Property("QVariantList", notify=dataChanged)
    def trits(self) -> list:
        return self._trits

    @Slot(str, str)
    def encode(self, message: str, key: str) -> None:
        if not message.strip():
            self.errorOccurred.emit("Digite uma mensagem.")
            return
        if not key.strip():
            self.errorOccurred.emit("Digite uma chave de criptografia.")
            return

        try:
            enc   = encodeMessage(message, key)
            bin_  = textToBinary(enc)
            trits = binaryToTrits(bin_)
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return

        display = ""
        for ch in enc:
            c = ord(ch)
            if (c >= 32 and c != 127) and not (128 <= c <= 159):
                display += ch
            else:
                display += f"\\x{c:02X}"

        self._encrypted = display
        self._binary    = bin_
        self._trits     = trits
        self.dataChanged.emit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("8B6T Signal Encoder")

    engine = QQmlApplicationEngine()
    encoder = Encoder()
    engine.rootContext().setContextProperty("encoder", encoder)

    qml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encoder.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
