"""
KIYA Piano Studio Pro - Physical Hardware Button Component
Recreates authentic PSR-S975 tactile push-buttons with beveled surfaces,
ambient drop shadows, pressed-down displacement animation, and integrated jewel LEDs.
"""

from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QTimer, QPropertyAnimation, Property
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QMouseEvent, QPaintEvent
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
    """Custom-painted tactile physical hardware workstation button."""

    clicked = Signal()
    toggled = Signal(bool)

    def __init__(
        self,
        label: str,
        secondary_label: str = "",
        secondary_text: str = "",
        led_color: str = "",       # "green", "red", "amber", "blue", or "" (no LED)
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

        # Pressed state vertical offset (0.0 to 1.5 pixels)
        self._press_offset = 0.0

    def set_led_color(self, color: str):
        self.led_color = color
        self.update()

    def flash(self, duration_ms: int = 150):
        self.set_led(True)
        QTimer.singleShot(duration_ms, lambda: self.set_led(False))

    # --- Qt Properties for smooth press animation ---
    def get_press_offset(self) -> float:
        return self._press_offset

    def set_press_offset(self, val: float):
        self._press_offset = val
        self.update()

    press_offset = Property(float, get_press_offset, set_press_offset)

    # --- State Setters ---
    def set_checked(self, checked: bool):
        if self._is_checked != checked:
            self._is_checked = checked
            # Typically LED follows checked state if LED is configured
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

    # --- Mouse Events ---
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

    # --- Realistic Hardware Rendering ---
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        radius = 3.0

        # Ambient drop shadow beneath button in unpressed state
        if not self._is_pressed:
            shadow_rect = QRectF(1.0, 2.5, w - 2.0, h - 2.5)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(HW_BTN_SHADOW))
            painter.drawRoundedRect(shadow_rect, radius, radius)

        # Button Face Geometry (displaced down when pressed)
        y_off = self._press_offset
        face_rect = QRectF(1.0, 1.0 + y_off, w - 2.0, h - 3.0)

        # 1. Button Face Gradient
        face_grad = QLinearGradient(0, face_rect.top(), 0, face_rect.bottom())
        if not self.isEnabled():
            face_grad.setColorAt(0.0, QColor("#1C1E22"))
            face_grad.setColorAt(1.0, QColor("#15171A"))
        elif self._is_pressed:
            face_grad.setColorAt(0.0, QColor(HW_BTN_PRESSED))
            face_grad.setColorAt(1.0, QColor("#141619"))
        elif self._is_checked and not self.led_color:
            # Highlight face if button is checked and has no dedicated LED
            face_grad.setColorAt(0.0, QColor("#3D424F"))
            face_grad.setColorAt(1.0, QColor("#2A2D36"))
        elif self._is_hovered:
            face_grad.setColorAt(0.0, QColor(HW_BTN_HOVER))
            face_grad.setColorAt(1.0, QColor("#2C2F37"))
        else:
            face_grad.setColorAt(0.0, QColor(HW_BTN_SURFACE))
            face_grad.setColorAt(1.0, QColor("#1E2026"))

        painter.setPen(QPen(QColor(HW_BTN_BORDER), 1.0))
        painter.setBrush(face_grad)
        painter.drawRoundedRect(face_rect, radius, radius)

        # 2. 1px Top-edge Highlight Line
        if self.isEnabled() and not self._is_pressed:
            highlight_pen = QPen(QColor(HW_BTN_HIGHLIGHT), 1.0)
            painter.setPen(highlight_pen)
            painter.drawLine(
                int(face_rect.left() + 2), int(face_rect.top() + 1),
                int(face_rect.right() - 2), int(face_rect.top() + 1)
            )

        # 3. Optional Integrated Jewel LED
        has_led = bool(self.led_color)
        if has_led:
            led_cx = face_rect.center().x()
            led_cy = face_rect.top() + 5.5
            draw_led_jewel(painter, led_cx, led_cy, radius=2.5, is_on=self._is_led_on, color_type=self.led_color)

        # 4. Button Text Silkscreen
        painter.setPen(QColor(HW_BTN_TEXT if self.isEnabled() else "#484D58"))

        avail_w = max(10.0, face_rect.width() - 4.0)
        avail_h = max(10.0, face_rect.height())

        if self.secondary_label:
            # Two-line button text layout
            f_size = 7.0
            font = get_hardware_font(size=int(f_size), bold=True)
            painter.setFont(font)
            while f_size > 4.5 and painter.fontMetrics().horizontalAdvance(self.label) > avail_w:
                f_size -= 0.5
                font = get_hardware_font(size=max(5, int(f_size)), bold=True)
                painter.setFont(font)

            if has_led:
                prim_y = face_rect.top() + 8.0
                row_h = (avail_h - 10.0) / 2.0
                sec_y = prim_y + row_h
            else:
                prim_y = face_rect.top() + 2.0
                row_h = (avail_h - 4.0) / 2.0
                sec_y = prim_y + row_h

            painter.drawText(
                QRectF(face_rect.left() + 2, prim_y, avail_w, row_h),
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )

            # Secondary label
            painter.setPen(QColor(HW_BTN_TEXT_SEC if self.isEnabled() else "#3A3E46"))
            sec_f_size = 6.0
            font_sec = get_hardware_font(size=int(sec_f_size), bold=False)
            painter.setFont(font_sec)
            while sec_f_size > 4.5 and painter.fontMetrics().horizontalAdvance(self.secondary_label) > avail_w:
                sec_f_size -= 0.5
                font_sec = get_hardware_font(size=max(4, int(sec_f_size)), bold=False)
                painter.setFont(font_sec)

            painter.drawText(
                QRectF(face_rect.left() + 2, sec_y, avail_w, row_h),
                Qt.AlignmentFlag.AlignCenter,
                self.secondary_label
            )
        else:
            # Single-line button text layout
            f_size = 8.0
            font = get_hardware_font(size=int(f_size), bold=True)
            painter.setFont(font)
            while f_size > 5.0 and painter.fontMetrics().horizontalAdvance(self.label) > avail_w:
                f_size -= 0.5
                font = get_hardware_font(size=max(5, int(f_size)), bold=True)
                painter.setFont(font)

            if has_led:
                prim_y = face_rect.top() + 7.5
                prim_h = avail_h - 9.0
            else:
                prim_y = face_rect.top()
                prim_h = avail_h

            painter.drawText(
                QRectF(face_rect.left() + 2, prim_y, avail_w, prim_h),
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )
