"""
KIYA Piano Studio Pro - Arranger Beat Indicator Widget
4-Jewel hardware-style LED beat display simulating Yamaha PSR / Genos arranger keyboards.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen
from app.constants import COLOR_BORDER

class BeatIndicatorWidget(QWidget):
    """4-LED Beat Flasher Jewel Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 28)
        self.current_beat = 1
        self.numerator = 4
        self.is_running = False

    def set_beat(self, beat: int, numerator: int = 4, is_running: bool = True):
        self.current_beat = beat
        self.numerator = max(1, min(8, numerator))
        self.is_running = is_running
        self.update()

    def trigger_beat(self, beat: int, numerator: int = 4):
        self.set_beat(beat, numerator, is_running=True)

    def reset_all(self):
        self.stop()

    def stop(self):
        self.is_running = False
        self.current_beat = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        num_dots = self.numerator if self.numerator in (3, 4, 6) else 4
        spacing = self.width() / float(num_dots)
        radius = 6.0
        cy = self.height() / 2.0

        for i in range(1, num_dots + 1):
            cx = (i - 0.5) * spacing
            is_active = self.is_running and (self.current_beat == i)

            # Outer bezel ring
            painter.setPen(QPen(QColor(COLOR_BORDER), 1.0))
            painter.setBrush(QColor("#0F1116"))
            painter.drawEllipse(QRectF(cx - radius - 1.5, cy - radius - 1.5, (radius + 1.5) * 2, (radius + 1.5) * 2))

            # LED Core
            grad = QRadialGradient(cx - 1.5, cy - 1.5, radius)
            if is_active:
                if i == 1:
                    # Beat 1: Intense Amber / Red downbeat
                    grad.setColorAt(0.0, QColor("#FFE082"))
                    grad.setColorAt(0.5, QColor("#FF6D00"))
                    grad.setColorAt(1.0, QColor("#D50000"))
                else:
                    # Beats 2, 3, 4: Neon Emerald Green
                    grad.setColorAt(0.0, QColor("#B9F6CA"))
                    grad.setColorAt(0.5, QColor("#00E676"))
                    grad.setColorAt(1.0, QColor("#00B0FF") if i == 3 and num_dots == 4 else QColor("#009624"))
            else:
                # Dim unlit LED
                grad.setColorAt(0.0, QColor("#222730"))
                grad.setColorAt(1.0, QColor("#14171E"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))


# Backward & Hardware compatibility alias
HardwareBeatIndicator = BeatIndicatorWidget
