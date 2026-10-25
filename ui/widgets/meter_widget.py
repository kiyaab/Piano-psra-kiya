"""
KIYA Piano Studio Pro - Stereo Peak VU Level Meter Widget
Renders dynamic Left & Right audio level meters with color gradients and clip indicators.
"""

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from app.constants import COLOR_BG, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR, COLOR_BORDER

class StereoMeterWidget(QWidget):
    """Dual-channel stereo audio peak level meter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(28, 48)
        self.peak_left = 0.0
        self.peak_right = 0.0

        # Clip indicators
        self.clip_left = False
        self.clip_right = False

        # Refresh timer (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._decay_and_update)
        self.timer.start(33)

    def set_levels(self, left: float, right: float):
        self.peak_left = max(left, self.peak_left)
        self.peak_right = max(right, self.peak_right)
        if left >= 0.98:
            self.clip_left = True
        if right >= 0.98:
            self.clip_right = True

    def _decay_and_update(self):
        # Smooth visual decay
        self.peak_left *= 0.88
        self.peak_right *= 0.88
        if self.peak_left < 0.01:
            self.peak_left = 0.0
            self.clip_left = False
        if self.peak_right < 0.01:
            self.peak_right = 0.0
            self.clip_right = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        width = self.width()
        height = self.height()

        bar_width = (width - 6) / 2.0
        meter_height = height - 8.0

        # Background
        painter.fillRect(0, 0, width, height, QColor(COLOR_BG))
        painter.setPen(QColor(COLOR_BORDER))
        painter.drawRect(0, 0, width - 1, height - 1)

        # Draw Left Bar
        self._draw_bar(painter, 2.0, 4.0, bar_width, meter_height, self.peak_left, self.clip_left)

        # Draw Right Bar
        self._draw_bar(painter, 4.0 + bar_width, 4.0, bar_width, meter_height, self.peak_right, self.clip_right)

    def _draw_bar(self, painter: QPainter, x: float, y: float, w: float, h: float, level: float, is_clip: bool):
        # Background slot
        painter.fillRect(QRectF(x, y, w, h), QColor("#14171E"))

        fill_h = min(h, level * h)
        if fill_h > 0.5:
            bar_y = y + h - fill_h

            # Gradient from green -> yellow -> red
            grad = QLinearGradient(x, y + h, x, y)
            grad.setColorAt(0.0, QColor(COLOR_SUCCESS))
            grad.setColorAt(0.75, QColor(COLOR_WARNING))
            grad.setColorAt(1.0, QColor(COLOR_ERROR))

            painter.fillRect(QRectF(x, bar_y, w, fill_h), grad)

        # Top clip light
        if is_clip:
            painter.fillRect(QRectF(x, y, w, 3.0), QColor(COLOR_ERROR))
