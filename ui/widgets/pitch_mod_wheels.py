"""
KIYA Piano Studio Pro - Pitch Bend and Modulation Wheels Widget
Realistic spring-loaded Pitch Bend wheel and friction-held Modulation wheel
recreating authentic hardware workstation performance controllers.
"""

from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QMouseEvent
from app.constants import (
    COLOR_PANEL_MAIN,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_TEXT_SECONDARY
)

class PitchModWheelsWidget(QWidget):
    """Dual hardware performance wheels: Pitch Bend (spring return) and Modulation (CC 1)."""

    pitch_bend_changed = Signal(int)   # -8192 to +8191 (center 0)
    modulation_changed = Signal(int)   # 0 to 127

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(84)
        self.setMinimumHeight(130)

        # Normalized positions: -1.0 to +1.0 for pitch bend, 0.0 to 1.0 for mod
        self._pitch_val = 0.0   # Center is 0.0
        self._mod_val = 0.0     # Bottom is 0.0

        # Mouse tracking
        self._active_wheel: str = ""  # "pitch" or "mod"
        self._drag_start_y = 0.0
        self._drag_start_val = 0.0

        # Spring return timer for pitch bend
        self._spring_timer = QTimer(self)
        self._spring_timer.setInterval(16)
        self._spring_timer.timeout.connect(self._on_spring_step)

    def _get_pitch_rect(self) -> QRectF:
        w = (self.width() - 16) / 2.0
        h = self.height() - 28.0
        return QRectF(6.0, 8.0, w, h)

    def _get_mod_rect(self) -> QRectF:
        w = (self.width() - 16) / 2.0
        h = self.height() - 28.0
        return QRectF(w + 10.0, 8.0, w, h)

    def mousePressEvent(self, event: QMouseEvent):
        p_rect = self._get_pitch_rect()
        m_rect = self._get_mod_rect()
        pos = event.position()

        if p_rect.contains(pos):
            self._active_wheel = "pitch"
            self._spring_timer.stop()
            self._drag_start_y = pos.y()
            self._drag_start_val = self._pitch_val
            self._update_pitch_from_y(pos.y(), p_rect)
        elif m_rect.contains(pos):
            self._active_wheel = "mod"
            self._drag_start_y = pos.y()
            self._drag_start_val = self._mod_val
            self._update_mod_from_y(pos.y(), m_rect)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        if self._active_wheel == "pitch":
            self._update_pitch_from_y(pos.y(), self._get_pitch_rect())
        elif self._active_wheel == "mod":
            self._update_mod_from_y(pos.y(), self._get_mod_rect())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._active_wheel == "pitch":
            # Start smooth spring return to center
            self._spring_timer.start()
        self._active_wheel = ""

    def _update_pitch_from_y(self, y: float, rect: QRectF):
        # Top of rect is +1.0, center is 0.0, bottom is -1.0
        rel_y = (y - rect.top()) / rect.height()
        norm = 1.0 - (rel_y * 2.0)
        self._pitch_val = max(-1.0, min(1.0, norm))
        midi_pitch = int(self._pitch_val * 8191)
        self.pitch_bend_changed.emit(midi_pitch)
        self.update()

    def _update_mod_from_y(self, y: float, rect: QRectF):
        # Top of rect is 1.0, bottom is 0.0
        rel_y = (y - rect.top()) / rect.height()
        norm = 1.0 - rel_y
        self._mod_val = max(0.0, min(1.0, norm))
        midi_mod = int(self._mod_val * 127)
        self.modulation_changed.emit(midi_mod)
        self.update()

    def _on_spring_step(self):
        # Exponential decay to center 0.0
        if abs(self._pitch_val) < 0.05:
            self._pitch_val = 0.0
            self._spring_timer.stop()
            self.pitch_bend_changed.emit(0)
        else:
            self._pitch_val *= 0.65
            self.pitch_bend_changed.emit(int(self._pitch_val * 8191))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        p_rect = self._get_pitch_rect()
        m_rect = self._get_mod_rect()

        # Background chassis housing
        painter.setPen(QPen(QColor(COLOR_BORDER), 1.0))
        painter.setBrush(QColor("#12151B"))
        painter.drawRoundedRect(QRectF(1, 1, self.width() - 2, self.height() - 2), 6, 6)

        # 1. Render Pitch Bend Wheel
        self._draw_wheel(painter, p_rect, self._pitch_val, is_center_detent=True, accent_color=QColor(COLOR_ACCENT_ORANGE))

        # 2. Render Modulation Wheel
        self._draw_wheel(painter, m_rect, (self._mod_val * 2.0) - 1.0, is_center_detent=False, accent_color=QColor(COLOR_ACCENT_BLUE))

        # Wheel Labels
        painter.setPen(QColor(COLOR_TEXT_SECONDARY))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)

        lbl_y = self.height() - 16
        painter.drawText(QRectF(p_rect.left() - 4, lbl_y, p_rect.width() + 8, 14), Qt.AlignmentFlag.AlignCenter, "PITCH")
        painter.drawText(QRectF(m_rect.left() - 4, lbl_y, m_rect.width() + 8, 14), Qt.AlignmentFlag.AlignCenter, "MOD")

    def _draw_wheel(self, painter: QPainter, rect: QRectF, norm_val: float, is_center_detent: bool, accent_color: QColor):
        # Wheel Well / Slot
        painter.setPen(QPen(QColor("#08090C"), 1.5))
        painter.setBrush(QColor("#0E1015"))
        painter.drawRoundedRect(rect, 4, 4)

        # Wheel Cylinder 3D Gradient
        grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        grad.setColorAt(0.0, QColor("#1C2028"))
        grad.setColorAt(0.2, QColor("#353C4B"))
        grad.setColorAt(0.5, QColor("#4B556A"))
        grad.setColorAt(0.8, QColor("#353C4B"))
        grad.setColorAt(1.0, QColor("#1C2028"))

        inner_rect = rect.adjusted(3, 4, -3, -4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawRoundedRect(inner_rect, 3, 3)

        # Tactile Horizontal Grooves
        center_y = inner_rect.center().y()
        offset_y = -norm_val * (inner_rect.height() * 0.38)
        notch_y = center_y + offset_y

        painter.setPen(QPen(QColor("#1A1D24"), 1.0))
        for g_offset in [-24, -18, -12, -6, 6, 12, 18, 24]:
            gy = notch_y + g_offset
            if inner_rect.top() + 2 < gy < inner_rect.bottom() - 2:
                painter.drawLine(int(inner_rect.left() + 2), int(gy), int(inner_rect.right() - 2), int(gy))

        # Center indicator strip (Illuminated Notch)
        if inner_rect.top() + 2 < notch_y < inner_rect.bottom() - 2:
            notch_rect = QRectF(inner_rect.left() + 1, notch_y - 2, inner_rect.width() - 2, 4)
            painter.setBrush(accent_color)
            painter.drawRoundedRect(notch_rect, 2, 2)


# Alias for singular/plural compatibility
PitchModWheelWidget = PitchModWheelsWidget
