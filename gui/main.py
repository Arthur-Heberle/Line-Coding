import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
import serial

from core.encode import encodeMessage, textToBinary, binaryToTrits
from core.serial_protocol import format_trits_payload


class Encoder(QObject):
    dataChanged   = Signal()
    errorOccurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._encrypted = ""
        self._binary    = ""
        self._trits: list = []
        self._payload = ""

    @Property(str, notify=dataChanged)
    def encrypted(self) -> str:
        return self._encrypted

    @Property(str, notify=dataChanged)
    def binary(self) -> str:
        return self._binary

    @Property("QVariantList", notify=dataChanged)
    def trits(self) -> list:
        return self._trits

    @Property(str, notify=dataChanged)
    def payload(self) -> str:
        return self._payload

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
            payload = format_trits_payload(trits)
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
        self._payload   = payload
        self.dataChanged.emit()


class SerialBridge(QObject):
    stateChanged = Signal()
    errorOccurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._serial = None
        self._status = "Desconectado."

    @Property(bool, notify=stateChanged)
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    @Property(str, notify=stateChanged)
    def status(self) -> str:
        return self._status

    @Slot(str, str)
    def connectSerial(self, port: str, baud_rate: str) -> None:
        port = port.strip()
        if not port:
            self.errorOccurred.emit("Digite a porta serial do ESP32 Slave.")
            return

        try:
            baud = int(baud_rate.strip() or "115200")
            self._serial = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            self._serial = None
            self._status = "Falha ao conectar."
            self.stateChanged.emit()
            self.errorOccurred.emit(f"Não foi possível abrir {port}: {e}")
            return

        self._status = f"Conectado em {port} @ {baud}."
        self.stateChanged.emit()

    @Slot()
    def disconnectSerial(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()

        self._serial = None
        self._status = "Desconectado."
        self.stateChanged.emit()

    @Slot(str)
    def sendPayload(self, payload: str) -> None:
        if not payload:
            self.errorOccurred.emit("Codifique uma mensagem antes de enviar.")
            return

        if not self.connected:
            self.errorOccurred.emit("Conecte a porta serial do ESP32 Slave antes de enviar.")
            return

        try:
            self._serial.write(payload.encode("utf-8"))
            self._serial.flush()
        except Exception as e:
            self.errorOccurred.emit(f"Falha ao enviar pela serial: {e}")
            return

        self._status = f"Enviado: {payload.strip()}"
        self.stateChanged.emit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("8B6T Signal Encoder")

    engine = QQmlApplicationEngine()
    encoder = Encoder()
    serial_bridge = SerialBridge()
    engine.rootContext().setContextProperty("encoder", encoder)
    engine.rootContext().setContextProperty("serialBridge", serial_bridge)

    qml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encoder.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
