from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QScrollArea, QWidget


class WaveformWidget(QWidget):
    MARGIN_LEFT = 50
    TRIT_WIDTH  = 28
    HEIGHT      = 160
    Y_TOP       = 28    # +1
    Y_MID       = 80    # 0   (HEIGHT // 2)
    Y_BOT       = 132   # -1  (HEIGHT - 28)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._trits: list[int] = []
        self.setFixedHeight(self.HEIGHT)
        self.setMinimumWidth(self.MARGIN_LEFT + 20)

    def setTrits(self, trits: list[int]) -> None:
        self._trits = list(trits)
        natural_w = self.MARGIN_LEFT + len(self._trits) * self.TRIT_WIDTH + 20
        self.setFixedWidth(max(natural_w, self.MARGIN_LEFT + 20))
        self.update()

    def sizeHint(self):
        w = self.MARGIN_LEFT + len(self._trits) * self.TRIT_WIDTH + 20
        return QSize(max(w, self.MARGIN_LEFT + 20), self.HEIGHT)

    def _trit_y(self, trit: int) -> int:
        return self.Y_TOP if trit == 1 else self.Y_MID if trit == 0 else self.Y_BOT

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        ML, TW = self.MARGIN_LEFT, self.TRIT_WIDTH

        painter.fillRect(0, 0, w, self.HEIGHT, QColor("#050910"))

        for y, color in [(self.Y_TOP, "#2A4070"), (self.Y_MID, "#305090"), (self.Y_BOT, "#2A4070")]:
            painter.setPen(QPen(QColor(color), 1, Qt.PenStyle.DashLine))
            painter.drawLine(ML, y, max(w - 20, ML + 10), y)

        painter.setPen(QPen(QColor("#2A4070"), 1))
        painter.drawLine(ML - 6, 8, ML - 6, self.HEIGHT - 8)

        _font = QFont("Courier New")
        _font.setPixelSize(11)
        painter.setFont(_font)
        painter.setPen(QPen(QColor("#5A7090")))
        fm = painter.fontMetrics()
        for text, y in [("+1", self.Y_TOP), (" 0", self.Y_MID), ("-1", self.Y_BOT)]:
            painter.drawText(ML - 14 - fm.horizontalAdvance(text), y + fm.ascent() // 2, text)

        if not self._trits:
            painter.end()
            return

        path = QPainterPath()
        for i, trit in enumerate(self._trits):
            y  = self._trit_y(trit)
            x  = ML + i * TW
            xe = x + TW
            if i == 0:
                path.moveTo(x, y)
            else:
                py = self._trit_y(self._trits[i - 1])
                if py != y:
                    path.lineTo(x, y)
            path.lineTo(xe, y)

        glow = QPen(QColor(245, 158, 11, 30), 10)
        glow.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(glow)
        painter.drawPath(path)

        core = QPen(QColor("#F59E0B"), 2)
        core.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(core)
        painter.drawPath(path)

        painter.end()


def waveform_scroll_area(widget: WaveformWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidget(widget)
    sa.setWidgetResizable(False)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sa.setFixedHeight(widget.HEIGHT + 14)  # 2px border + 8px scrollbar + 4px padding
    sa.setStyleSheet(
        "QScrollArea { background: #050910; border: 1px solid #1E2D4A; border-radius: 8px; }"
        "QScrollBar:horizontal { background: #0F1629; height: 8px; }"
        "QScrollBar::handle:horizontal { background: #1E2D4A; border-radius: 4px; }"
    )
    return sa
