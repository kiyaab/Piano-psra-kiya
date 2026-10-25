"""
KIYA Piano Studio Pro - Real-Time Audio Oscilloscope & Waveform Visualizer
Renders live audio waveforms directly from the AudioEngine output stream.
"""

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
import numpy as np
from app.constants import COLOR_BG, COLOR_ACCENT_BLUE, COLOR_PANEL_MAIN, COLOR_BORDER

class WaveformWidget(QWidget):
    """Real-time audio oscilloscope visualizer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 36)
        self.buffer = np.zeros(256, dtype=np.float32)

        # Refresh timer (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def set_audio_data(self, data: np.ndarray):
        """Update audio waveform data."""
        if len(data) > 0:
            # Downsample to 256 points for smooth rendering
            if len(data) >= 256:
                step = len(data) // 256
                self.buffer = data[::step][:256]
            else:
                self.buffer = data

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        width = self.width()
        height = self.height()
        mid_y = height * 0.5

        # Background & border
        painter.fillRect(0, 0, width, height, QColor(COLOR_BG))
        painter.setPen(QColor(COLOR_BORDER))
        painter.drawRect(0, 0, width - 1, height - 1)

        # Center zero line
        painter.setPen(QPen(QColor("#1A202A"), 1.0, Qt.PenStyle.DashLine))
        painter.drawLine(0, int(mid_y), width, int(mid_y))

        # Waveform path
        n_points = len(self.buffer)
        if n_points < 2:
            return

        path = QPainterPath()
        dx = width / float(n_points - 1)
        amp = (height * 0.45)

        for i in range(n_points):
            val = float(self.buffer[i])
            x = i * dx
            y = mid_y - (val * amp)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # Draw glowing waveform line
        painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 1.8))
        painter.drawPath(path)
