"""
KIYA Piano Studio Pro - Premium Physical Hardware Button Component
Recreates authentic PSR-S975 tactile push-buttons with:
- Ultra-rich multi-stop beveled surfaces with premium gradient fills
- Intense ambient glow drop shadows
- Smooth pressed-down displacement with realistic physics feel
- Vivid integrated jewel LEDs with full atmospheric glow
- Crisp silkscreen typography with perfect layout
"""

from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QTimer, QPropertyAnimation, Property
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QMouseEvent, QPaintEvent
)
from ui.hardware_theme import (
    HW_BTN_SURFACE,
    HW_BTN_HOVER,
    HW_BTN_PRESSED,
    HW_BTN_BORDER,
    HW_BTN_HIGHLIGHT,
    HW_BTN_SHADOW,
    HW_BTN_TEXT,
    HW_BTN_TEXT_SEC,
    get_hardware_font,
    draw_led_jewel
)


class PhysicalButton(QWidget):
    """Premium custom-painted tactile physical hardware workstation button."""

    clicked = Signal()
    toggled = Signal(bool)

    def __init__(
        self,
        label: str,
        secondary_label: str = "",
        secondary_text: str = "",
        led_color: str = "",
        indicator: str = "",
        button_color: str = "",
        accent_line: bool = False,
        checkable: bool = False,
        width: int = 56,
        height: int = 34,
        parent=None,
        **kwargs
    ):
        super().__init__(parent)
        self.label = label
        self.secondary_label = secondary_label or secondary_text
        self.led_color = led_color or indicator
        self.button_color = button_color
        self.accent_line = accent_line
        self.checkable = checkable
        self._is_checked = False
        self._is_pressed = False
        self._is_hovered = False
        self._is_led_on = False

        # Visual dimensions
        self.setFixedSize(width, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Pressed state vertical offset
        self._press_offset = 0.0

    def set_led_color(self, color: str):
        self.led_color = color
        self.update()

    def flash(self, duration_ms: int = 150):
        self.set_led(True)
        QTimer.singleShot(duration_ms, lambda: self.set_led(False))

    def get_press_offset(self) -> float:
        return self._press_offset

    def set_press_offset(self, val: float):
        self._press_offset = val
        self.update()

    press_offset = Property(float, get_press_offset, set_press_offset)

    def set_checked(self, checked: bool):
        if self._is_checked != checked:
            self._is_checked = checked
            if self.led_color:
                self._is_led_on = checked
            self.update()
            self.toggled.emit(checked)

    def is_checked(self) -> bool:
        return self._is_checked

    def set_led(self, state: bool):
        if self._is_led_on != state:
            self._is_led_on = state
            self.update()

    def is_led_on(self) -> bool:
        return self._is_led_on

    def set_label(self, text: str):
        self.label = text
        self.update()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._is_pressed = False
        self._press_offset = 0.0
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._is_pressed = True
            self._press_offset = 1.5
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled() and self._is_pressed:
            self._is_pressed = False
            self._press_offset = 0.0
            if self.rect().contains(event.position().toPoint()):
                if self.checkable:
                    self.set_checked(not self._is_checked)
                self.clicked.emit()
            self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        radius = 4.0

        # ── 1. Ambient drop shadow (multi-layer for depth) ──────────────────
        if not self._is_pressed:
            for i, (offset, alpha) in enumerate([(3.0, 60), (2.0, 80), (1.5, 50)]):
                shadow_rect = QRectF(1.0, offset, w - 2.0, h - 1.5)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 0, alpha))
                painter.drawRoundedRect(shadow_rect, radius, radius)

        # ── 2. Button face geometry ─────────────────────────────────────────
        y_off = self._press_offset
        face_rect = QRectF(1.0, 1.0 + y_off, w - 2.0, h - 3.5)

        # ── 3. Button face gradient (premium multi-stop) ────────────────────
        face_grad = QLinearGradient(0, face_rect.top(), 0, face_rect.bottom())

        if not self.isEnabled():
            face_grad.setColorAt(0.0, QColor("#181C24"))
            face_grad.setColorAt(1.0, QColor("#121520"))
        elif self._is_pressed:
            face_grad.setColorAt(0.0, QColor("#141828"))
            face_grad.setColorAt(0.4, QColor("#181E2E"))
            face_grad.setColorAt(1.0, QColor("#0E1220"))
        elif self._is_checked and not self.led_color:
            face_grad.setColorAt(0.0, QColor("#353D58"))
            face_grad.setColorAt(0.5, QColor("#2C3450"))
            face_grad.setColorAt(1.0, QColor("#222840"))
        elif self._is_hovered:
            face_grad.setColorAt(0.0, QColor("#2E3858"))
            face_grad.setColorAt(0.35, QColor("#283250"))
            face_grad.setColorAt(1.0, QColor("#1E2640"))
        else:
            face_grad.setColorAt(0.0, QColor("#252C40"))
            face_grad.setColorAt(0.3, QColor("#202838"))
            face_grad.setColorAt(0.7, QColor("#1C2230"))
            face_grad.setColorAt(1.0, QColor("#161C28"))

        painter.setPen(QPen(QColor(HW_BTN_BORDER), 1.0))
        painter.setBrush(face_grad)
        painter.drawRoundedRect(face_rect, radius, radius)

        # ── 4. Top-edge chrome highlight bevel ──────────────────────────────
        if self.isEnabled() and not self._is_pressed:
            # Bright top rim
            highlight_grad = QLinearGradient(face_rect.left(), face_rect.top(),
                                              face_rect.right(), face_rect.top())
            highlight_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
            highlight_grad.setColorAt(0.2, QColor(255, 255, 255, 80))
            highlight_grad.setColorAt(0.5, QColor(255, 255, 255, 100))
            highlight_grad.setColorAt(0.8, QColor(255, 255, 255, 70))
            highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(highlight_grad), 1.0))
            painter.drawLine(
                int(face_rect.left() + 3), int(face_rect.top() + 1),
                int(face_rect.right() - 3), int(face_rect.top() + 1)
            )

        # ── 5. Left edge vertical highlight ─────────────────────────────────
        if self.isEnabled() and not self._is_pressed:
            left_grad = QLinearGradient(face_rect.left(), face_rect.top(),
                                         face_rect.left(), face_rect.bottom())
            left_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
            left_grad.setColorAt(0.3, QColor(255, 255, 255, 30))
            left_grad.setColorAt(0.7, QColor(255, 255, 255, 20))
            left_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(left_grad), 1.0))
            painter.drawLine(
                int(face_rect.left() + 1), int(face_rect.top() + 3),
                int(face_rect.left() + 1), int(face_rect.bottom() - 3)
            )

        # ── 6. Bottom edge inner shadow ──────────────────────────────────────
        if not self._is_pressed:
            painter.setPen(QPen(QColor(0, 0, 0, 100), 1.0))
            painter.drawLine(
                int(face_rect.left() + 3), int(face_rect.bottom()),
                int(face_rect.right() - 3), int(face_rect.bottom())
            )

        # ── 7. Integrated Jewel LED ─────────────────────────────────────────
        has_led = bool(self.led_color)
        if has_led:
            led_cx = face_rect.center().x()
            led_cy = face_rect.top() + 5.5
            draw_led_jewel(painter, led_cx, led_cy, radius=3.0, is_on=self._is_led_on, color_type=self.led_color)

        # ── 8. Button text silkscreen ───────────────────────────────────────
        enabled_col = QColor(HW_BTN_TEXT) if self.isEnabled() else QColor("#3A4058")
        sec_col = QColor(HW_BTN_TEXT_SEC) if self.isEnabled() else QColor("#252C3A")

        avail_w = max(10.0, face_rect.width() - 6.0)
        avail_h = max(10.0, face_rect.height())

        if self.secondary_label:
            # Two-line layout
            f_size = 7.5
            font = get_hardware_font(size=int(f_size), bold=True)
            painter.setFont(font)
            while f_size > 5.0 and painter.fontMetrics().horizontalAdvance(self.label) > avail_w:
                f_size -= 0.5
                font = get_hardware_font(size=max(5, int(f_size)), bold=True)
                painter.setFont(font)

            if has_led:
                prim_y = face_rect.top() + 9.0
                row_h = (avail_h - 11.0) / 2.0
                sec_y = prim_y + row_h
            else:
                prim_y = face_rect.top() + 2.0
                row_h = (avail_h - 4.0) / 2.0
                sec_y = prim_y + row_h

            painter.setPen(enabled_col)
            painter.drawText(
                QRectF(face_rect.left() + 3, prim_y, avail_w, row_h),
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )
            painter.setPen(sec_col)
            sec_f_size = 6.5
            font_sec = get_hardware_font(size=int(sec_f_size), bold=False)
            painter.setFont(font_sec)
            while sec_f_size > 4.5 and painter.fontMetrics().horizontalAdvance(self.secondary_label) > avail_w:
                sec_f_size -= 0.5
                font_sec = get_hardware_font(size=max(4, int(sec_f_size)), bold=False)
                painter.setFont(font_sec)
            painter.drawText(
                QRectF(face_rect.left() + 3, sec_y, avail_w, row_h),
                Qt.AlignmentFlag.AlignCenter,
                self.secondary_label
            )
        else:
            # Single-line layout
            f_size = 8.5
            font = get_hardware_font(size=int(f_size), bold=True)
            painter.setFont(font)
            while f_size > 5.0 and painter.fontMetrics().horizontalAdvance(self.label) > avail_w:
                f_size -= 0.5
                font = get_hardware_font(size=max(5, int(f_size)), bold=True)
                painter.setFont(font)

            if has_led:
                prim_y = face_rect.top() + 8.5
                prim_h = avail_h - 10.0
            else:
                prim_y = face_rect.top()
                prim_h = avail_h

            painter.setPen(enabled_col)
            painter.drawText(
                QRectF(face_rect.left() + 3, prim_y, avail_w, prim_h),
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )

        # ── 9. Hover glow overlay ───────────────────────────────────────────
        if self._is_hovered and self.isEnabled() and not self._is_pressed:
            hover_grad = QLinearGradient(0, face_rect.top(), 0, face_rect.bottom())
            hover_grad.setColorAt(0.0, QColor(100, 130, 220, 25))
            hover_grad.setColorAt(1.0, QColor(60, 80, 180, 10))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover_grad)
            painter.drawRoundedRect(face_rect, radius, radius)
