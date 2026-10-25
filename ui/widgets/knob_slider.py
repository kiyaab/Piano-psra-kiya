"""
KIYA Piano Studio Pro - Custom Knob & Mixer Fader Widgets
"""

import math
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent
from app.constants import (
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_PANEL_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ERROR
)

class DialKnob(QWidget):
    """Rotary dial control widget with drag interaction."""

    valueChanged = Signal(float)

    def __init__(self, title: str = "", min_val: float = 0.0, max_val: float = 1.0, default_val: float = 0.5, parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.setMinimumSize(48, 58)
        self.is_dragging = False
        self.last_mouse_y = 0

    def set_value(self, val: float):
        self.value = max(self.min_val, min(self.max_val, val))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.last_mouse_y = event.position().y()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging:
            dy = self.last_mouse_y - event.position().y()
            self.last_mouse_y = event.position().y()

            span = self.max_val - self.min_val
            step = (dy / 100.0) * span
            new_val = max(self.min_val, min(self.max_val, self.value + step))
            if new_val != self.value:
                self.value = new_val
                self.valueChanged.emit(self.value)
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        width = self.width()
        height = self.height()

        dial_size = min(width - 8, height - 20)
        dial_rect = QRectF((width - dial_size) / 2.0, 4.0, dial_size, dial_size)

        # Background Arc Track (from 135 deg to 405 deg)
        painter.setPen(QPen(QColor(COLOR_BORDER), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(dial_rect, int(-45 * 16), int(-270 * 16))

        # Value Arc Track
        norm_val = (self.value - self.min_val) / max(0.001, (self.max_val - self.min_val))
        val_span = norm_val * 270.0
        painter.setPen(QPen(QColor(COLOR_ACCENT_ORANGE), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(dial_rect, int(225 * 16), int(-val_span * 16))

        # Inner Dial Circle
        inner_rect = dial_rect.adjusted(5, 5, -5, -5)
        painter.setPen(QPen(QColor(COLOR_BORDER), 1.0))
        painter.setBrush(QBrush(QColor(COLOR_PANEL_SECONDARY)))
        painter.drawEllipse(inner_rect)

        # Dial Pointer Line
        angle_deg = 135.0 + (norm_val * 270.0)
        angle_rad = math.radians(angle_deg)
        center = inner_rect.center()
        radius = inner_rect.width() * 0.45
        pointer_end = QPointF(center.x() + radius * math.cos(angle_rad), center.y() + radius * math.sin(angle_rad))
        painter.setPen(QPen(QColor(COLOR_TEXT_PRIMARY), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(center, pointer_end)

        # Title Label
        if self.title:
            painter.setPen(QColor(COLOR_TEXT_SECONDARY))
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(0, height - 16, width, 16), Qt.AlignmentFlag.AlignCenter, self.title)


class ChannelFaderWidget(QWidget):
    """Mixer Channel strip fader with Mute, Solo, and slider."""

    volumeChanged = Signal(float)
    muteToggled = Signal(bool)
    soloToggled = Signal(bool)

    def __init__(self, channel_name: str = "Ch 1", default_vol: float = 0.85, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(54)
        self.setMaximumWidth(78)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(4)

        # Track title
        self.title_lbl = QLabel(channel_name)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(self.title_lbl)

        # Mute / Solo buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(2)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_mute = QPushButton("M")
        self.btn_mute.setCheckable(True)
        self.btn_mute.setMaximumWidth(24)
        self.btn_mute.setStyleSheet("QPushButton:checked { background-color: #FF626B; color: white; }")
        self.btn_mute.toggled.connect(self.muteToggled.emit)

        self.btn_solo = QPushButton("S")
        self.btn_solo.setCheckable(True)
        self.btn_solo.setMaximumWidth(24)
        self.btn_solo.setStyleSheet("QPushButton:checked { background-color: #FFC83B; color: black; }")
        self.btn_solo.toggled.connect(self.soloToggled.emit)

        btn_layout.addWidget(self.btn_mute)
        btn_layout.addWidget(self.btn_solo)
        layout.addLayout(btn_layout)

        # Vertical Slider
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(0, 127)
        self.slider.setValue(int(default_vol * 127))
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider, 1, Qt.AlignmentFlag.AlignHCenter)

        # Volume readout
        self.val_lbl = QLabel(f"{int(default_vol * 100)}%")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.val_lbl.setStyleSheet(f"font-size: 10px; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(self.val_lbl)

    def _on_slider_changed(self, val: int):
        normalized = val / 127.0
        self.val_lbl.setText(f"{int(normalized * 100)}%")
        self.volumeChanged.emit(normalized)

    def set_volume(self, vol: float):
        self.slider.blockSignals(True)
        self.slider.setValue(int(vol * 127))
        self.val_lbl.setText(f"{int(vol * 100)}%")
        self.slider.blockSignals(False)
