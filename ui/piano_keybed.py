"""
KIYA Piano Studio Pro - Realistic Piano Keybed Assembly (PSR-S975 Style)
Integrates:
1. Left Cheekblock with Pitch Bend & Modulation Wheels
2. Red Velvet Keybed Felt Strip across top of keys
3. 61-Key Interactive Virtual Piano Keyboard (C2 to C7)
4. Split point zone visualization & Computer key labels
5. Hardware End-Cheeks with brushed metallic chassis styling
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
    Classic acoustic piano red velvet felt strip running across the back of the keys.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(5)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        w = self.width()
        h = self.height()

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#4A0D0D"))
        grad.setColorAt(0.5, QColor("#851818"))
        grad.setColorAt(1.0, QColor("#3D0B0B"))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(0, 0, w, h)


class PianoKeybedAssembly(QWidget):
    """
    Complete lower instrument section:
    - Left cheekblock with Pitch & Mod wheels
    - Red felt strip
    - 61-Key Piano Keyboard
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
        self.setMinimumHeight(160)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 0, 8, 4)
        main_layout.setSpacing(6)

        # 1. Left Cheekblock (Houses Pitch Bend & Mod Wheels)
        left_cheek = QFrame()
        left_cheek.setFixedWidth(104)
        left_cheek.setStyleSheet("background: #0E1012; border: 1px solid #1E2126; border-radius: 4px;")
        lc_layout = QVBoxLayout(left_cheek)
        lc_layout.setContentsMargins(4, 4, 4, 4)
        lc_layout.setSpacing(2)

        self.wheels = PitchModWheelWidget(self)
        self.wheels.pitch_bend_changed.connect(self.pitchBend.emit)
        self.wheels.modulation_changed.connect(self.modulation.emit)
        lc_layout.addWidget(self.wheels)

        main_layout.addWidget(left_cheek)

        # 2. Main Keyboard Area (Felt Strip + Keys)
        key_container = QWidget()
        kc_layout = QVBoxLayout(key_container)
        kc_layout.setContentsMargins(0, 0, 0, 0)
        kc_layout.setSpacing(0)

        # Red felt strip
        self.felt = FeltStripWidget(key_container)
        kc_layout.addWidget(self.felt)

        # 61-Key Keyboard
        self.piano = PianoKeyboardWidget(key_container)
        self.piano.note_pressed.connect(self.noteOn.emit)
        self.piano.note_released.connect(self.noteOff.emit)
        kc_layout.addWidget(self.piano, 1)

        main_layout.addWidget(key_container, 1)

        # 3. Right Cheekblock (Symmetric brushed hardware finish)
        right_cheek = QFrame()
        right_cheek.setFixedWidth(38)
        right_cheek.setStyleSheet("background: #0E1012; border: 1px solid #1E2126; border-radius: 4px;")
        rc_layout = QVBoxLayout(right_cheek)
        rc_layout.setContentsMargins(2, 8, 2, 8)
        rc_layout.setAlignment(Qt.AlignCenter)

        lbl_s975 = QLabel("61\nKEYS")
        lbl_s975.setFont(HardwareFonts.micro_bold())
        lbl_s975.setStyleSheet("color: #717D8E; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;")
        lbl_s975.setAlignment(Qt.AlignCenter)
        rc_layout.addWidget(lbl_s975)

        main_layout.addWidget(right_cheek)

    def set_split_point(self, split_note: int, show_marker: bool = True):
        self.piano.set_split_point(split_note, show_marker)

    def set_key_pressed(self, note: int, is_pressed: bool):
        self.piano.set_key_pressed(note, is_pressed)

    def release_all_keys(self):
        self.piano.release_all_keys()
