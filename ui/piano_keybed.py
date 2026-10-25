"""
KIYA Piano Studio Pro - Premium Piano Keybed Assembly (PSR-S975 Style)
Integrates:
1. Left Cheekblock with Pitch Bend & Modulation Wheels (premium dark finish)
2. Deep Crimson Velvet Felt Strip across top of keys
3. 61-Key Interactive Virtual Piano Keyboard (C2 to C7) 
4. Split point zone visualization & Computer key labels
5. Right cheekblock with brushed metallic chassis styling
"""

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QPaintEvent
)

from ui.widgets.piano_widget import PianoKeyboardWidget
from ui.widgets.pitch_mod_wheels import PitchModWheelWidget
from ui.hardware_theme import HardwareColors, HardwareFonts


class FeltStripWidget(QWidget):
    """
    Deep crimson velvet felt strip running across the back of the keys —
    a classic acoustic grand piano feature.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        w = self.width()
        h = self.height()

        # Deep crimson velvet with subtle sheen
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#3A0808"))
        grad.setColorAt(0.3, QColor("#7A1212"))
        grad.setColorAt(0.6, QColor("#9A1818"))
        grad.setColorAt(1.0, QColor("#2E0606"))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(0, 0, w, h)

        # Subtle fabric texture lines (velvet sheen)
        painter.setPen(QPen(QColor(255, 100, 100, 20), 1.0))
        for x in range(0, w, 4):
            painter.drawLine(x, 1, x, h - 2)

        # Top highlight thread
        painter.setPen(QPen(QColor(200, 80, 80, 60), 1.0))
        painter.drawLine(0, 1, w, 1)


class CheekBlock(QWidget):
    """Premium brushed-metal cheek block end panel."""
    def __init__(self, parent=None, side: str = "left", label: str = ""):
        super().__init__(parent)
        self.side = side
        self.label = label

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Rich dark brushed metal gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#1A1E28"))
        grad.setColorAt(0.3, QColor("#141820"))
        grad.setColorAt(0.6, QColor("#10141C"))
        grad.setColorAt(1.0, QColor("#0C1016"))

        painter.setPen(QPen(QColor("#0A0D16"), 1.5))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(QRectF(0, 0, w, h), 5.0, 5.0)

        # Left/right edge chrome accent
        edge_grad = QLinearGradient(0, 0, 0, h)
        edge_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        edge_grad.setColorAt(0.2, QColor(255, 255, 255, 40))
        edge_grad.setColorAt(0.5, QColor(255, 255, 255, 30))
        edge_grad.setColorAt(0.8, QColor(255, 255, 255, 20))
        edge_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        edge_x = 1 if self.side == "left" else w - 2
        painter.setPen(QPen(QBrush(edge_grad), 1.0))
        painter.drawLine(edge_x, 4, edge_x, h - 5)

        # Label text
        if self.label:
            painter.setPen(QColor("#5A6880"))
            font = HardwareFonts.micro_bold()
            painter.setFont(font)
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, self.label)


class PianoKeybedAssembly(QWidget):
    """
    Complete lower instrument section:
    - Left cheekblock with Pitch & Mod wheels (premium dark finish)
    - Deep crimson velvet felt strip
    - 61-Key Piano Keyboard (world-class rendering)
    - Right cheekblock
    """
    noteOn = Signal(int, int)    # note, velocity
    noteOff = Signal(int)        # note
    pitchBend = Signal(int)      # -8192 to 8191
    modulation = Signal(int)     # 0 to 127

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PianoKeybedAssembly")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(170)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 2, 8, 6)
        main_layout.setSpacing(6)

        # ── 1. Left Cheekblock (Pitch Bend & Mod Wheels) ────────────────────
        left_cheek = QFrame()
        left_cheek.setFixedWidth(106)
        left_cheek.setStyleSheet(
            "background: #0C0F18; border: 1px solid #1E2230; border-radius: 5px;"
        )
        lc_layout = QVBoxLayout(left_cheek)
        lc_layout.setContentsMargins(4, 6, 4, 6)
        lc_layout.setSpacing(2)

        self.wheels = PitchModWheelWidget(self)
        self.wheels.pitch_bend_changed.connect(self.pitchBend.emit)
        self.wheels.modulation_changed.connect(self.modulation.emit)
        lc_layout.addWidget(self.wheels)

        main_layout.addWidget(left_cheek)

        # ── 2. Main Keyboard Area (Felt Strip + Keys) ────────────────────────
        key_container = QWidget()
        kc_layout = QVBoxLayout(key_container)
        kc_layout.setContentsMargins(0, 0, 0, 0)
        kc_layout.setSpacing(0)

        # Felt strip
        self.felt = FeltStripWidget(key_container)
        kc_layout.addWidget(self.felt)

        # 61-Key Keyboard
        self.piano = PianoKeyboardWidget(key_container)
        self.piano.note_pressed.connect(self.noteOn.emit)
        self.piano.note_released.connect(self.noteOff.emit)
        kc_layout.addWidget(self.piano, 1)

        main_layout.addWidget(key_container, 1)

        # ── 3. Right Cheekblock ─────────────────────────────────────────────
        right_cheek = QFrame()
        right_cheek.setFixedWidth(40)
        right_cheek.setStyleSheet(
            "background: #0C0F18; border: 1px solid #1E2230; border-radius: 5px;"
        )
        rc_layout = QVBoxLayout(right_cheek)
        rc_layout.setContentsMargins(2, 8, 2, 8)
        rc_layout.setAlignment(Qt.AlignCenter)

        lbl_s975 = QLabel("61\nKEYS")
        lbl_s975.setFont(HardwareFonts.micro_bold())
        lbl_s975.setStyleSheet(
            "color: #607090; font-size: 9px; font-weight: bold; "
            "letter-spacing: 0.5px; background: transparent; border: none;"
        )
        lbl_s975.setAlignment(Qt.AlignCenter)
        rc_layout.addWidget(lbl_s975)

        main_layout.addWidget(right_cheek)

    def set_split_point(self, split_note: int, show_marker: bool = True):
        self.piano.set_split_point(split_note, show_marker)

    def set_key_pressed(self, note: int, is_pressed: bool):
        self.piano.set_key_pressed(note, is_pressed)

    def release_all_keys(self):
        self.piano.release_all_keys()
