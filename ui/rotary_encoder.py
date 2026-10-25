"""
KIYA Piano Studio Pro - Realistic Metallic Rotary Encoder / Jog Dial
Custom-painted hardware dial with metallic brushed aluminum cap, radial knurling notches,
smooth mouse drag / wheel rotation, and surrounding PSR-S975 navigation cluster.
"""

import math
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient, QConicalGradient,
    QLinearGradient, QFont, QPaintEvent, QMouseEvent, QWheelEvent
)

from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class RotaryDial(QWidget):
    """
    Realistic brushed aluminum rotary encoder dial.
    Rotates continuously with mouse wheel or vertical drag.
    """
    valueChanged = Signal(int)  # delta: +1 (clockwise) or -1 (counter-clockwise)
    clicked = Signal()

    def __init__(self, parent=None, size: int = 86):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        self.angle_deg = 0.0
        self._is_dragging = False
        self._last_mouse_pos = None
        self._is_pressed = False
        self._accum_delta = 0.0

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._is_pressed = True
            self._last_mouse_pos = event.position()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging and self._last_mouse_pos is not None:
            delta_y = self._last_mouse_pos.y() - event.position().y()
            delta_x = event.position().x() - self._last_mouse_pos.x()
            self._last_mouse_pos = event.position()

            # Drag sensitivity
            motion = delta_y + delta_x
            self._accum_delta += motion
            self.angle_deg = (self.angle_deg + motion * 3.5) % 360.0

            step_threshold = 12.0
            if abs(self._accum_delta) >= step_threshold:
                steps = int(self._accum_delta / step_threshold)
                self._accum_delta -= steps * step_threshold
                self.valueChanged.emit(steps)

            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            self._is_pressed = False
            self.clicked.emit()
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta != 0:
            step = 1 if delta > 0 else -1
            self.angle_deg = (self.angle_deg + step * 18.0) % 360.0
            self.valueChanged.emit(step)
            self.update()
        event.accept()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2.0, h / 2.0)
        radius = min(w, h) / 2.0 - 4.0

        # 1. Outer recessed mounting bezel
        bezel_rect = QRectF(center.x() - radius - 3, center.y() - radius - 3, (radius + 3) * 2, (radius + 3) * 2)
        bezel_grad = QLinearGradient(bezel_rect.topLeft(), bezel_rect.bottomLeft())
        bezel_grad.setColorAt(0.0, QColor("#08090B"))
        bezel_grad.setColorAt(1.0, QColor("#1C1E23"))
        painter.setPen(QPen(QColor("#040506"), 1.5))
        painter.setBrush(QBrush(bezel_grad))
        painter.drawEllipse(bezel_rect)

        # 2. Outer knurled textured ring (dark rubber/alloy grip)
        outer_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        outer_grad = QRadialGradient(center, radius)
        outer_grad.setColorAt(0.70, QColor("#22252A"))
        outer_grad.setColorAt(0.92, QColor("#141618"))
        outer_grad.setColorAt(1.00, QColor("#0D0E10"))
        painter.setPen(QPen(QColor("#383C44"), 1.0))
        painter.setBrush(QBrush(outer_grad))
        painter.drawEllipse(outer_rect)

        # 3. Knurling notches around circumference
        painter.save()
        painter.translate(center)
        num_notches = 36
        notch_len = 5.0
        for i in range(num_notches):
            angle = (i * 360.0 / num_notches) + self.angle_deg
            rad = math.radians(angle)
            p1 = QPointF((radius - 1.0) * math.cos(rad), (radius - 1.0) * math.sin(rad))
            p2 = QPointF((radius - 1.0 - notch_len) * math.cos(rad), (radius - 1.0 - notch_len) * math.sin(rad))
            painter.setPen(QPen(QColor(10, 11, 13, 180), 1.5))
            painter.drawLine(p1, p2)
            # Subtle highlight next to notch
            rad_hi = math.radians(angle + 1.5)
            p1_hi = QPointF((radius - 1.0) * math.cos(rad_hi), (radius - 1.0) * math.sin(rad_hi))
            p2_hi = QPointF((radius - 1.0 - notch_len) * math.cos(rad_hi), (radius - 1.0 - notch_len) * math.sin(rad_hi))
            painter.setPen(QPen(QColor(80, 88, 98, 120), 1.0))
            painter.drawLine(p1_hi, p2_hi)
        painter.restore()

        # 4. Inner metallic brushed aluminum cap
        cap_radius = radius * 0.72
        cap_rect = QRectF(center.x() - cap_radius, center.y() - cap_radius, cap_radius * 2, cap_radius * 2)

        # Simulated brushed aluminum conical gradient
        conical = QConicalGradient(center, self.angle_deg)
        conical.setColorAt(0.00, QColor("#454A52"))
        conical.setColorAt(0.25, QColor("#8A929E"))
        conical.setColorAt(0.50, QColor("#3E4249"))
        conical.setColorAt(0.75, QColor("#9DA6B4"))
        conical.setColorAt(1.00, QColor("#454A52"))

        painter.setPen(QPen(QColor("#25282E"), 1.2))
        painter.setBrush(QBrush(conical))
        painter.drawEllipse(cap_rect)

        # Inner ring bevel
        inner_bev = QRectF(center.x() - cap_radius * 0.85, center.y() - cap_radius * 0.85, cap_radius * 1.7, cap_radius * 1.7)
        rad_grad = QRadialGradient(center, cap_radius * 0.85)
        rad_grad.setColorAt(0.0, QColor("#5B626C"))
        rad_grad.setColorAt(0.85, QColor("#3A3E45"))
        rad_grad.setColorAt(1.0, QColor("#22252A"))
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.0))
        painter.setBrush(QBrush(rad_grad))
        painter.drawEllipse(inner_bev)

        # 5. Position dimple / finger indent
        dimple_dist = cap_radius * 0.58
        rad_cur = math.radians(self.angle_deg - 90.0)
        dimple_center = QPointF(
            center.x() + dimple_dist * math.cos(rad_cur),
            center.y() + dimple_dist * math.sin(rad_cur)
        )
        dimple_r = 5.0
        dimple_rect = QRectF(dimple_center.x() - dimple_r, dimple_center.y() - dimple_r, dimple_r * 2, dimple_r * 2)

        dimple_grad = QRadialGradient(dimple_center, dimple_r)
        dimple_grad.setColorAt(0.0, QColor("#181A1D"))
        dimple_grad.setColorAt(0.7, QColor("#2A2D33"))
        dimple_grad.setColorAt(1.0, QColor("#858D9A"))
        painter.setPen(QPen(QColor("#0E1012"), 1.0))
        painter.setBrush(QBrush(dimple_grad))
        painter.drawEllipse(dimple_rect)

        # Center subtle hardware label / dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#1A1C20")))
        painter.drawEllipse(center, 2.5, 2.5)


class RotaryEncoderCluster(QWidget):
    """
    Complete PSR-S975 style data dial and navigation cluster:
    - Large metallic jog dial in the center.
    - Surrounding navigation buttons: [ENTER], [EXIT], [▲], [▼], [◄], [►].
    - Quick increment/decrement buttons: [- / NO], [+ / YES].
    """
    dialMoved = Signal(int)       # +1 or -1 step
    enterTriggered = Signal()
    exitTriggered = Signal()
    upTriggered = Signal()
    downTriggered = Signal()
    leftTriggered = Signal()
    rightTriggered = Signal()
    decTriggered = Signal()
    incTriggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RotaryEncoderCluster")
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)
        main_layout.setAlignment(Qt.AlignCenter)

        # Top Section: Title & DEC/INC
        title_box = QHBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        lbl_data = QLabel("DATA ENTRY")
        lbl_data.setFont(HardwareFonts.micro_bold())
        lbl_data.setStyleSheet("color: #7B8594; letter-spacing: 1px;")
        lbl_data.setAlignment(Qt.AlignCenter)
        title_box.addWidget(lbl_data)
        main_layout.addLayout(title_box)

        # Quick - / + Buttons Row
        inc_dec_box = QHBoxLayout()
        inc_dec_box.setSpacing(6)

        self.btn_dec = PhysicalButton(
            "- / NO",
            secondary_text="DEC",
            width=54,
            height=26,
            button_color=HardwareColors.BUTTON_DARK,
            accent_line=False
        )
        self.btn_dec.clicked.connect(self._on_dec)

        self.btn_inc = PhysicalButton(
            "+ / YES",
            secondary_text="INC",
            width=54,
            height=26,
            button_color=HardwareColors.BUTTON_DARK,
            accent_line=False
        )
        self.btn_inc.clicked.connect(self._on_inc)

        inc_dec_box.addWidget(self.btn_dec)
        inc_dec_box.addWidget(self.btn_inc)
        main_layout.addLayout(inc_dec_box)

        # Center Dial + Nav Ring
        center_box = QHBoxLayout()
        center_box.setSpacing(6)
        center_box.setAlignment(Qt.AlignCenter)

        # Left Column: Left arrow & Exit
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        left_col.setAlignment(Qt.AlignCenter)

        self.btn_left = PhysicalButton("◀", width=38, height=32, button_color=HardwareColors.BUTTON_DARK)
        self.btn_left.clicked.connect(self.leftTriggered.emit)
        self.btn_exit = PhysicalButton("EXIT", width=42, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_exit.clicked.connect(self.exitTriggered.emit)

        left_col.addWidget(self.btn_left)
        left_col.addWidget(self.btn_exit)
        center_box.addLayout(left_col)

        # Center Column: Up arrow, Rotary Dial, Down arrow
        mid_col = QVBoxLayout()
        mid_col.setSpacing(4)
        mid_col.setAlignment(Qt.AlignCenter)

        self.btn_up = PhysicalButton("▲", width=38, height=24, button_color=HardwareColors.BUTTON_DARK)
        self.btn_up.clicked.connect(self.upTriggered.emit)

        self.dial = RotaryDial(self, size=86)
        self.dial.valueChanged.connect(self._on_dial_value)
        self.dial.clicked.connect(self.enterTriggered.emit)

        self.btn_down = PhysicalButton("▼", width=38, height=24, button_color=HardwareColors.BUTTON_DARK)
        self.btn_down.clicked.connect(self.downTriggered.emit)

        mid_col.addWidget(self.btn_up, 0, Qt.AlignCenter)
        mid_col.addWidget(self.dial, 0, Qt.AlignCenter)
        mid_col.addWidget(self.btn_down, 0, Qt.AlignCenter)
        center_box.addLayout(mid_col)

        # Right Column: Right arrow & Enter
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_col.setAlignment(Qt.AlignCenter)

        self.btn_right = PhysicalButton("▶", width=38, height=32, button_color=HardwareColors.BUTTON_DARK)
        self.btn_right.clicked.connect(self.rightTriggered.emit)
        self.btn_enter = PhysicalButton(
            "ENTER",
            width=42,
            height=28,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="blue"
        )
        self.btn_enter.clicked.connect(self.enterTriggered.emit)

        right_col.addWidget(self.btn_right)
        right_col.addWidget(self.btn_enter)
        center_box.addLayout(right_col)

        main_layout.addLayout(center_box)

    def _on_dial_value(self, delta: int):
        self.dialMoved.emit(delta)

    def _on_dec(self):
        self.decTriggered.emit()
        self.dialMoved.emit(-1)

    def _on_inc(self):
        self.incTriggered.emit()
        self.dialMoved.emit(1)
