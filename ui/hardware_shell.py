"""
KIYA Piano Studio Pro - Realistic Physical Instrument Hardware Chassis
Renders:
1. Deep textured charcoal chassis (#111214) with subtle gradients
2. Dual Left & Right Acoustic Speaker Grilles with woven hexagonal mesh
3. Chrome branding badge "KIYA PSR-S975 ARRANGER WORKSTATION"
4. Brushed metallic trim seam dividing upper panel, middle strip, and keybed
5. Proportional 55% Upper / 17% Middle / 28% Keybed vertical layout
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPaintEvent
)

from ui.control_panel import HardwareControlPanel
from ui.middle_strip import MiddleControlStrip
from ui.piano_keybed import PianoKeybedAssembly
from ui.hardware_theme import HardwareColors, HardwareFonts


class SpeakerGrille(QWidget):
    """
    Acoustic speaker grille with micro-perforated acoustic mesh
    matching the physical PSR-S975 stereo speaker wings.
    """
    def __init__(self, parent=None, is_left: bool = True):
        super().__init__(parent)
        self.is_left = is_left
        self.setFixedHeight(28)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Recessed grille tray with metallic border
        rect = QRectF(2, 2, w - 4, h - 4)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#08090B"))
        grad.setColorAt(0.5, QColor("#14161A"))
        grad.setColorAt(1.0, QColor("#0E1013"))
        painter.setPen(QPen(QColor("#030405"), 1.2))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, 4.0, 4.0)

        # 1px top edge rim highlight
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        painter.drawLine(4, 3, int(w) - 5, 3)

        # Micro-dot perforated acoustic pattern
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(50, 56, 68, 160)))
        step_x = 7
        step_y = 5
        for x in range(10, int(w) - 10, step_x):
            for y in range(6, int(h) - 6, step_y):
                offset = (x // step_x) % 2 * 2
                painter.drawEllipse(x, y + offset, 2, 2)


class MetallicTrimSeam(QWidget):
    """
    Brushed aluminum accent seam line separating control sections.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        w = self.width()

        # 1px dark shadow, 1px bright chrome highlight
        painter.setPen(QPen(QColor("#060709"), 1.0))
        painter.drawLine(0, 0, w, 0)

        painter.setPen(QPen(QColor("#424752"), 1.0))
        painter.drawLine(0, 1, w, 1)

        painter.setPen(QPen(QColor("#181A1F"), 1.0))
        painter.drawLine(0, 2, w, 2)


class HardwareShell(QWidget):
    """
    Main instrument chassis widget.
    Hosts the upper panel, middle strip, and keybed in exact proportions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HardwareShell")
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 8)
        main_layout.setSpacing(4)

        # --- TOP HEADER: SPEAKER GRILLES & BRANDING ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(4, 0, 4, 0)
        top_bar.setSpacing(12)

        self.speaker_left = SpeakerGrille(self, is_left=True)
        top_bar.addWidget(self.speaker_left, 1)

        # Chrome Branding Badge
        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)
        brand_box.setAlignment(Qt.AlignCenter)

        lbl_brand = QLabel("KIYA")
        lbl_brand.setFont(HardwareFonts.title_bold())
        lbl_brand.setStyleSheet("color: #E2E8F0; font-weight: bold; letter-spacing: 2px;")
        lbl_brand.setAlignment(Qt.AlignCenter)
        brand_box.addWidget(lbl_brand)

        lbl_model = QLabel("PIANO STUDIO PRO  ·  PSR-S975 ARRANGER")
        lbl_model.setFont(HardwareFonts.micro_bold())
        lbl_model.setStyleSheet("color: #7B8594; letter-spacing: 1px;")
        lbl_model.setAlignment(Qt.AlignCenter)
        brand_box.addWidget(lbl_model)

        top_bar.addLayout(brand_box)

        self.speaker_right = SpeakerGrille(self, is_left=False)
        top_bar.addWidget(self.speaker_right, 1)

        main_layout.addLayout(top_bar)

        # --- SEAM TRIM ---
        main_layout.addWidget(MetallicTrimSeam(self))

        # --- AREA A: UPPER CONTROL PANEL (~48%) ---
        self.control_panel = HardwareControlPanel(self)
        main_layout.addWidget(self.control_panel, 48)

        # --- SEAM TRIM ---
        main_layout.addWidget(MetallicTrimSeam(self))

        # --- AREA B: MIDDLE CONTROL STRIP (~16%) ---
        self.middle_strip = MiddleControlStrip(self)
        main_layout.addWidget(self.middle_strip, 16)

        # --- SEAM TRIM ---
        main_layout.addWidget(MetallicTrimSeam(self))

        # --- AREA C: PIANO KEYBED (~36%) ---
        self.keybed = PianoKeybedAssembly(self)
        main_layout.addWidget(self.keybed, 36)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Chassis body with subtle gradient
        body_rect = QRectF(0, 0, w, h)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#141619"))
        grad.setColorAt(0.5, QColor("#101114"))
        grad.setColorAt(1.0, QColor("#0A0B0D"))

        painter.setPen(QPen(QColor("#050607"), 2.0))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(body_rect, 6.0, 6.0)

        # Subtle chassis bevel highlights on edges
        painter.setPen(QPen(QColor(255, 255, 255, 18), 1.0))
        painter.drawLine(2, 2, w - 3, 2)
        painter.drawLine(2, 2, 2, h - 3)
