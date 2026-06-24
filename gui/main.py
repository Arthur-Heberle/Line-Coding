import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import serial
from serial.tools import list_ports
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# 00:70:07:26:7d:bc

from core.encode import encodeMessage, textToBinary, binaryToTrits
from core.serial_protocol import format_trits_payload
from widgets import WaveformWidget, waveform_scroll_area


class SenderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.payload = ""
        self.read_timer = QTimer(self)
        self.read_timer.setInterval(50)
        self.read_timer.timeout.connect(self._read_serial)

        self.setWindowTitle("8B6T Signal Encoder")
        self.resize(900, 720)

        root = QWidget()
        root.setObjectName("root")

        main = QVBoxLayout(root)
        main.setContentsMargins(40, 36, 40, 36)
        main.setSpacing(18)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("8B6T")
        title.setObjectName("title")
        tag = QLabel("Signal Encoder")
        tag.setObjectName("tag")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(tag)
        main.addLayout(header)

        # ── Form: message + key ───────────────────────────────────────────────
        form = QHBoxLayout()
        form.setSpacing(12)

        msg_col = QVBoxLayout()
        msg_col.setSpacing(8)
        msg_col.addWidget(self.label("MENSAGEM"))
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Digite a mensagem a codificar…")
        self.msg_input.returnPressed.connect(self.encode)
        msg_col.addWidget(self.msg_input)

        key_col = QVBoxLayout()
        key_col.setSpacing(8)
        key_col.addWidget(self.label("CHAVE VIGENÈRE"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Chave secreta")
        self.key_input.setFixedWidth(210)
        self.key_input.returnPressed.connect(self.encode)
        key_col.addWidget(self.key_input)

        form.addLayout(msg_col)
        form.addLayout(key_col)
        main.addLayout(form)

        # ── Encode button + error ─────────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(16)
        encode_btn = QPushButton("Codificar")
        encode_btn.clicked.connect(self.encode)
        self.error_label = QLabel()
        self.error_label.setObjectName("error")
        self.error_label.setVisible(False)
        actions.addWidget(encode_btn)
        actions.addWidget(self.error_label)
        actions.addStretch(1)
        main.addLayout(actions)

        # ── Serial controls ───────────────────────────────────────────────────
        serial_row = QHBoxLayout()
        serial_row.setSpacing(12)

        port_col = QVBoxLayout()
        port_col.setSpacing(8)
        port_col.addWidget(self.label("PORTA SERIAL"))
        self.port_combo = QComboBox()
        refresh_btn = QPushButton("⟳")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.setFixedWidth(38)
        refresh_btn.clicked.connect(self._refresh_ports)
        port_row = QHBoxLayout()
        port_row.setSpacing(6)
        port_row.addWidget(self.port_combo, 1)
        port_row.addWidget(refresh_btn)
        port_col.addLayout(port_row)

        baud_col = QVBoxLayout()
        baud_col.setSpacing(8)
        baud_col.addWidget(self.label("BAUD"))
        self.baud_input = QLineEdit("115200")
        self.baud_input.setFixedWidth(120)
        baud_col.addWidget(self.baud_input)

        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.clicked.connect(self.toggle_connection)

        self.send_btn = QPushButton("Enviar TRITS")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_payload)

        self.serial_status = QLabel("Desconectado.")
        self.serial_status.setObjectName("status")

        serial_row.addLayout(port_col)
        serial_row.addLayout(baud_col)
        serial_row.addWidget(self.connect_btn, 0, Qt.AlignmentFlag.AlignBottom)
        serial_row.addWidget(self.send_btn, 0, Qt.AlignmentFlag.AlignBottom)
        serial_row.addWidget(self.serial_status, 1, Qt.AlignmentFlag.AlignBottom)
        main.addLayout(serial_row)

        # ── Results panel (hidden until first encode) ─────────────────────────
        self.results_panel = QFrame()
        self.results_panel.setObjectName("resultsPanel")
        self.results_panel.setVisible(False)

        rp = QVBoxLayout(self.results_panel)
        rp.setContentsMargins(22, 18, 22, 18)
        rp.setSpacing(18)

        self.encrypted_output = self.output_box()
        self.binary_output = self.output_box()

        self.waveform = WaveformWidget()
        wave_scroll = waveform_scroll_area(self.waveform)

        wave_sec = QWidget()
        wl = QVBoxLayout(wave_sec)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)
        wl.addWidget(self.label("FORMA DE ONDA — TRITS"))
        wl.addWidget(wave_scroll)

        results_splitter = QSplitter(Qt.Orientation.Vertical)
        results_splitter.setChildrenCollapsible(False)
        results_splitter.addWidget(self.section("TEXTO CIFRADO", self.encrypted_output))
        results_splitter.addWidget(self.section("BINÁRIO", self.binary_output))
        results_splitter.addWidget(wave_sec)
        results_splitter.setSizes([80, 120, 180])
        rp.addWidget(results_splitter)

        main.addWidget(self.results_panel)
        main.addStretch(1)

        scroll_area = QScrollArea()
        scroll_area.setWidget(root)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(scroll_area)

        self._refresh_ports()
        self.apply_style()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def output_box(self) -> QPlainTextEdit:
        box = QPlainTextEdit()
        box.setReadOnly(True)
        box.setMaximumBlockCount(200)
        return box

    def section(self, title: str, box: QPlainTextEdit) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.label(title))
        layout.addWidget(box)
        return widget

    def _refresh_ports(self) -> None:
        self.port_combo.clear()
        ports = sorted(list_ports.comports(), key=lambda p: p.device)
        if ports:
            for p in ports:
                self.port_combo.addItem(f"{p.device}  —  {p.description}", p.device)
        else:
            self.port_combo.addItem("Nenhuma porta encontrada", "")

    def show_error(self, msg: str) -> None:
        self.error_label.setText(msg)
        self.error_label.setVisible(True)

    def set_serial_status(self, msg: str) -> None:
        self.serial_status.setText(msg)

    def _update_send_btn(self) -> None:
        connected = self.serial_port is not None and self.serial_port.is_open
        self.send_btn.setEnabled(connected and bool(self.payload))

    # ── Encode ────────────────────────────────────────────────────────────────

    def encode(self) -> None:
        message = self.msg_input.text()
        key = self.key_input.text()

        if not message.strip():
            self.show_error("Digite uma mensagem.")
            return
        if not key.strip():
            self.show_error("Digite uma chave de criptografia.")
            return

        try:
            enc    = encodeMessage(message, key)
            bin_   = textToBinary(enc)
            trits  = binaryToTrits(bin_)
            self.payload = format_trits_payload(trits)
        except Exception as e:
            self.show_error(str(e))
            return

        display = ""
        for ch in enc:
            c = ord(ch)
            if (c >= 32 and c != 127) and not (128 <= c <= 159):
                display += ch
            else:
                display += f"\\x{c:02X}"

        self.encrypted_output.setPlainText(display)
        self.binary_output.setPlainText(
            " ".join(bin_[i : i + 8] for i in range(0, len(bin_), 8))
        )
        self.waveform.setTrits(trits)

        self.results_panel.setVisible(True)
        self.error_label.setVisible(False)
        self._update_send_btn()

    # ── Serial ────────────────────────────────────────────────────────────────

    def toggle_connection(self) -> None:
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self) -> None:
        port = self.port_combo.currentData() or ""
        if not port:
            self.show_error("Digite a porta serial do ESP32.")
            return
        try:
            baud = int(self.baud_input.text().strip() or "115200")
            self.serial_port = serial.Serial(port, baud, timeout=1)
        except Exception as exc:
            self.serial_port = None
            self.set_serial_status(f"Não foi possível abrir {port}: {exc}")
            return
        self.connect_btn.setText("Desconectar")
        self.set_serial_status(f"Conectado em {port} @ {baud}.")
        self._update_send_btn()
        self.read_timer.start()

    def disconnect_serial(self) -> None:
        self.read_timer.stop()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.connect_btn.setText("Conectar")
        self.set_serial_status("Desconectado.")
        self._update_send_btn()

    def _read_serial(self) -> None:
        if not self.serial_port or not self.serial_port.is_open:
            return
        try:
            while self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode("utf-8", errors="replace").strip()
                if line:
                    self.set_serial_status(line)
        except Exception as exc:
            self.set_serial_status(f"Falha ao ler serial: {exc}")
            self.disconnect_serial()

    def send_payload(self) -> None:
        if not self.payload:
            self.show_error("Codifique uma mensagem antes de enviar.")
            return
        if not (self.serial_port and self.serial_port.is_open):
            self.show_error("Conecte a porta serial antes de enviar.")
            return
        try:
            self.serial_port.flush()
            self.serial_port.write(self.payload.encode("utf-8"))
        except Exception as exc:
            self.show_error(f"Falha ao enviar: {exc}")
            return
        self.set_serial_status(f"Enviado: {self.payload.strip()}")

    # ── Style ─────────────────────────────────────────────────────────────────

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
            #error {
                color: #EF4444;
                font-size: 13px;
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
            QPushButton:disabled {
                background: #1E2D4A;
                color: #64748B;
            }
            QComboBox {
                background: #0F1629;
                border: 1px solid #1E2D4A;
                border-radius: 8px;
                color: #E2E8F0;
                font-family: JetBrains Mono, Courier New, monospace;
                font-size: 13px;
                padding: 10px 12px;
            }
            QComboBox:focus {
                border-color: #4F46E5;
            }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748B;
                width: 0; height: 0;
            }
            QComboBox QAbstractItemView {
                background: #0F1629;
                border: 1px solid #1E2D4A;
                color: #E2E8F0;
                selection-background-color: #4F46E5;
                outline: none;
            }
            #refreshBtn {
                background: #1E2D4A;
                border-radius: 8px;
                color: #E2E8F0;
                font-size: 16px;
                padding: 10px 0;
            }
            #refreshBtn:hover { background: #2A3F66; }
            #resultsPanel {
                background: #0F1629;
                border: 1px solid #1E2D4A;
                border-radius: 12px;
            }
            QScrollArea { background: #080D1C; border: none; }
            QScrollBar:vertical {
                background: #0F1629;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #1E2D4A;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #4F46E5; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QSplitter::handle:vertical {
                background: #1E2D4A;
                height: 4px;
                margin: 2px 0;
            }
            QSplitter::handle:vertical:hover { background: #4F46E5; }
            """
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("8B6T Signal Encoder")
    window = SenderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
