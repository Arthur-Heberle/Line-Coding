import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import serial
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.encode import binaryToText, decode_message, tritsToBinary
from core.serial_protocol import parse_trits_line


def display_text(text: str) -> str:
    output = ""
    for char in text:
        value = ord(char)
        if (value >= 32 and value != 127) and not (128 <= value <= 159):
            output += char
        else:
            output += f"\\x{value:02X}"
    return output


class ReceiverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.read_serial)

        self.setWindowTitle("8B6T Signal Receiver")
        self.resize(900, 720)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(40, 36, 40, 36)
        main.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("8B6T")
        title.setObjectName("title")
        tag = QLabel("Signal Receiver")
        tag.setObjectName("tag")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(tag)
        main.addLayout(header)

        controls = QGridLayout()
        controls.setHorizontalSpacing(12)
        controls.setVerticalSpacing(8)

        controls.addWidget(self.label("PORTA SERIAL"), 0, 0)
        controls.addWidget(self.label("BAUD"), 0, 1)
        controls.addWidget(self.label("CHAVE VIGENERE"), 0, 2)

        self.port_input = QLineEdit("/dev/ttyACM0")
        self.baud_input = QLineEdit("115200")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Chave de decodificacao")

        controls.addWidget(self.port_input, 1, 0)
        controls.addWidget(self.baud_input, 1, 1)
        controls.addWidget(self.key_input, 1, 2)

        self.connect_button = QPushButton("Conectar")
        self.connect_button.clicked.connect(self.toggle_connection)
        controls.addWidget(self.connect_button, 1, 3)

        controls.setColumnStretch(0, 2)
        controls.setColumnStretch(1, 1)
        controls.setColumnStretch(2, 2)
        main.addLayout(controls)

        self.status_label = QLabel("Desconectado.")
        self.status_label.setObjectName("status")
        main.addWidget(self.status_label)

        self.raw_output = self.output_box()
        self.trits_output = self.output_box()
        self.binary_output = self.output_box()
        self.encrypted_output = self.output_box()
        self.message_output = self.output_box()

        main.addWidget(self.section("LINHA BRUTA", self.raw_output))
        main.addWidget(self.section("TRITS RECEBIDOS", self.trits_output))
        main.addWidget(self.section("BINARIO RECUPERADO", self.binary_output))
        main.addWidget(self.section("TEXTO CIFRADO RECUPERADO", self.encrypted_output))
        main.addWidget(self.section("MENSAGEM FINAL", self.message_output))

        self.apply_style()

    def label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def output_box(self) -> QPlainTextEdit:
        box = QPlainTextEdit()
        box.setReadOnly(True)
        box.setMaximumBlockCount(200)
        box.setMinimumHeight(72)
        return box

    def section(self, title: str, box: QPlainTextEdit) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.label(title))
        layout.addWidget(box)
        return widget

    def toggle_connection(self) -> None:
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self) -> None:
        port = self.port_input.text().strip()
        if not port:
            self.set_status("Digite a porta serial do ESP32 Master.", error=True)
            return

        try:
            baud = int(self.baud_input.text().strip() or "115200")
            self.serial_port = serial.Serial(port, baud, timeout=0)
        except Exception as exc:
            self.serial_port = None
            self.set_status(f"Nao foi possivel abrir {port}: {exc}", error=True)
            return

        self.connect_button.setText("Desconectar")
        self.set_status(f"Conectado em {port} @ {baud}.")
        self.timer.start()

    def disconnect_serial(self) -> None:
        self.timer.stop()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.connect_button.setText("Conectar")
        self.set_status("Desconectado.")

    def read_serial(self) -> None:
        if not self.serial_port or not self.serial_port.is_open:
            return

        try:
            while self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode("utf-8", errors="replace").strip()
                if line:
                    self.process_line(line)
        except Exception as exc:
            self.set_status(f"Falha ao ler serial: {exc}", error=True)
            self.disconnect_serial()

    def process_line(self, line: str) -> None:
        self.raw_output.setPlainText(line)

        key = self.key_input.text()
        if not key:
            self.set_status("Digite a chave para decodificar a mensagem.", error=True)
            return

        try:
            trits = parse_trits_line(line)
            binary = tritsToBinary(trits)
            encrypted = binaryToText(binary)
            message = decode_message(encrypted, key)
        except Exception as exc:
            self.set_status(str(exc), error=True)
            return

        self.trits_output.setPlainText(",".join(str(trit) for trit in trits))
        self.binary_output.setPlainText(" ".join(binary[i : i + 8] for i in range(0, len(binary), 8)))
        self.encrypted_output.setPlainText(display_text(encrypted))
        self.message_output.setPlainText(message)
        self.set_status("Mensagem recebida e decodificada.")

    def set_status(self, text: str, error: bool = False) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("error", error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def apply_style(self) -> None:
        self.setStyleSheet(
            """
            #root {
                background: #080D1C;
                color: #E2E8F0;
                font-family: Ubuntu, Segoe UI, sans-serif;
            }
            QLabel {
                color: #E2E8F0;
            }
            #title {
                color: #E2E8F0;
                font-family: JetBrains Mono, Courier New, monospace;
                font-size: 30px;
                font-weight: 700;
            }
            #tag, #fieldLabel {
                color: #64748B;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 2px;
            }
            #status {
                color: #64748B;
                font-size: 12px;
            }
            #status[error="true"] {
                color: #EF4444;
            }
            QLineEdit, QPlainTextEdit {
                background: #0F1629;
                border: 1px solid #1E2D4A;
                border-radius: 8px;
                color: #E2E8F0;
                font-family: JetBrains Mono, Courier New, monospace;
                font-size: 13px;
                padding: 10px 12px;
            }
            QLineEdit:focus, QPlainTextEdit:focus {
                border-color: #4F46E5;
            }
            QPushButton {
                background: #4F46E5;
                border: 0;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background: #4338CA;
            }
            """
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("8B6T Signal Receiver")
    window = ReceiverWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
