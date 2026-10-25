"""
KIYA Piano Studio Pro - Ultra-Premium Physical Instrument Hardware Chassis
Renders:
1. Ultra-deep textured obsidian chassis with multi-stop gradient body
2. Dual Left & Right premium acoustic speaker grilles with woven hexagonal mesh
3. Illuminated gradient chrome branding badge "KIYA · PSR-S975 ARRANGER WORKSTATION"
4. Brushed metallic trim seam with gold accent dividing all sections
5. Proportional 50% Upper / 16% Middle / 34% Keybed vertical layout
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QPaintEvent
)

from ui.control_panel import HardwareControlPanel
from ui.middle_strip import MiddleControlStrip
from ui.piano_keybed import PianoKeybedAssembly
from ui.hardware_theme import HardwareColors, HardwareFonts


class SpeakerGrille(QWidget):
    """
    Premium acoustic speaker grille with micro-perforated acoustic mesh
    matching the physical PSR-S975 stereo speaker wings, with subtle glow.
    """
    def __init__(self, parent=None, is_left: bool = True):
        super().__init__(parent)
        self.is_left = is_left
        self.setFixedHeight(34)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Recessed grille tray with metallic border
        rect = QRectF(2, 2, w - 4, h - 4)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#06070C"))
        grad.setColorAt(0.4, QColor("#0E1018"))
        grad.setColorAt(0.7, QColor("#0A0C14"))
        grad.setColorAt(1.0, QColor("#050609"))
        painter.setPen(QPen(QColor("#020306"), 1.5))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, 5.0, 5.0)

        # Subtle top metallic rim highlight
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1.0))
        painter.drawLine(5, 3, int(w) - 6, 3)

        # Bottom dark shadow line
        painter.setPen(QPen(QColor(0, 0, 0, 150), 1.0))
        painter.drawLine(5, int(h) - 4, int(w) - 6, int(h) - 4)

        # Micro-dot perforated acoustic pattern (offset rows)
        painter.setPen(Qt.NoPen)
        step_x = 7
        step_y = 5
        for x in range(8, int(w) - 8, step_x):
            for y in range(7, int(h) - 7, step_y):
                row_offset = ((x // step_x) % 2) * 2
                # Dots with subtle blue-tinted glow for premium look
                painter.setBrush(QBrush(QColor(40, 50, 80, 180)))
                painter.drawEllipse(x, y + row_offset, 2, 2)
                # Tiny highlight on each dot
                painter.setBrush(QBrush(QColor(80, 100, 140, 60)))
                painter.drawEllipse(x, y + row_offset, 1, 1)

        # Subtle left/right directional gradient for depth
        side_grad = QLinearGradient(0, 0, w, 0)
        if self.is_left:
            side_grad.setColorAt(0.0, QColor(255, 255, 255, 15))
            side_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        else:
            side_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            side_grad.setColorAt(1.0, QColor(255, 255, 255, 15))
        painter.setBrush(QBrush(side_grad))
        painter.drawRoundedRect(rect, 5.0, 5.0)


class MetallicTrimSeam(QWidget):
    """
    Premium brushed-aluminum + gold accent seam line separating control sections.
    """
    def __init__(self, parent=None, accent_color: str = "#C9A84C"):
        super().__init__(parent)
        self.accent_color = accent_color
        self.setFixedHeight(4)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        w = self.width()

        # Shadow line
        painter.setPen(QPen(QColor("#030408"), 1.0))
        painter.drawLine(0, 0, w, 0)

        # Gold accent stripe
        gold_grad = QLinearGradient(0, 0, w, 0)
        gold_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        gold_grad.setColorAt(0.1, QColor(self.accent_color))
        gold_grad.setColorAt(0.5, QColor(255, 220, 100, 200))
        gold_grad.setColorAt(0.9, QColor(self.accent_color))
        gold_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(QPen(QBrush(gold_grad), 1.0))
        painter.drawLine(0, 1, w, 1)

        # Medium gray middle
        painter.setPen(QPen(QColor("#2A3050"), 1.0))
        painter.drawLine(0, 2, w, 2)

        # Soft highlight at bottom
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        painter.drawLine(0, 3, w, 3)


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
        main_layout.setContentsMargins(12, 8, 12, 10)
        main_layout.setSpacing(4)

        # ── TOP HEADER: SPEAKER GRILLES & BRANDING ──────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(6, 0, 6, 0)
        top_bar.setSpacing(14)

        self.speaker_left = SpeakerGrille(self, is_left=True)
        top_bar.addWidget(self.speaker_left, 1)

        # Chrome Branding Badge (centered)
        brand_box = QVBoxLayout()
        brand_box.setSpacing(1)
        brand_box.setAlignment(Qt.AlignCenter)

        lbl_brand = QLabel("KIYA")
        brand_font = HardwareFonts.title_bold()
        brand_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        lbl_brand.setFont(brand_font)
        lbl_brand.setStyleSheet(
            "color: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #F0F8FF, stop:0.4 #D8E8F8, stop:1.0 #A8C0D8);"
            "font-weight: 800;"
            "letter-spacing: 4px;"
        )
        lbl_brand.setAlignment(Qt.AlignCenter)
        brand_box.addWidget(lbl_brand)

        lbl_model = QLabel("PIANO STUDIO PRO  ·  PSR-S975 ARRANGER")
        lbl_model.setFont(HardwareFonts.micro_bold())
        lbl_model.setStyleSheet("color: #5A6880; letter-spacing: 1.5px;")
        lbl_model.setAlignment(Qt.AlignCenter)
        brand_box.addWidget(lbl_model)

        top_bar.addLayout(brand_box)

        self.speaker_right = SpeakerGrille(self, is_left=False)
        top_bar.addWidget(self.speaker_right, 1)

        main_layout.addLayout(top_bar)
        main_layout.addSpacing(2)

        # ── GOLD ACCENT SEAM ─────────────────────────────────────────────────
        main_layout.addWidget(MetallicTrimSeam(self))

        # ── AREA A: UPPER CONTROL PANEL (~50%) ──────────────────────────────
        self.control_panel = HardwareControlPanel(self)
        main_layout.addWidget(self.control_panel, 50)

        # ── GOLD ACCENT SEAM ─────────────────────────────────────────────────
        main_layout.addWidget(MetallicTrimSeam(self))

        # ── AREA B: MIDDLE CONTROL STRIP (~15%) ─────────────────────────────
        self.middle_strip = MiddleControlStrip(self)
        main_layout.addWidget(self.middle_strip, 15)

        # ── SILVER SEAM ──────────────────────────────────────────────────────
        main_layout.addWidget(MetallicTrimSeam(self, accent_color="#607090"))

        # ── AREA C: PIANO KEYBED (~35%) ──────────────────────────────────────
        self.keybed = PianoKeybedAssembly(self)
        main_layout.addWidget(self.keybed, 35)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # ── Main chassis body: ultra-rich multi-stop dark gradient ──────────
        body_rect = QRectF(0, 0, w, h)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.00, QColor("#131620"))
        grad.setColorAt(0.15, QColor("#0F1218"))
        grad.setColorAt(0.45, QColor("#0C0E16"))
        grad.setColorAt(0.70, QColor("#0A0C14"))
        grad.setColorAt(0.88, QColor("#080B12"))
        grad.setColorAt(1.00, QColor("#06080F"))

        painter.setPen(QPen(QColor("#03040A"), 2.5))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(body_rect, 8.0, 8.0)

        # ── Subtle vignette glow from center-top ────────────────────────────
        vignette = QRadialGradient(w * 0.5, h * 0.1, w * 0.6)
        vignette.setColorAt(0.0, QColor(40, 60, 120, 25))
        vignette.setColorAt(0.6, QColor(20, 30, 70, 10))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(vignette))
        painter.drawRoundedRect(body_rect, 8.0, 8.0)

        # ── Chassis top bevel highlight ──────────────────────────────────────
        top_bevel = QLinearGradient(0, 0, w, 0)
        top_bevel.setColorAt(0.0, QColor(255, 255, 255, 0))
        top_bevel.setColorAt(0.25, QColor(255, 255, 255, 30))
        top_bevel.setColorAt(0.5, QColor(255, 255, 255, 40))
        top_bevel.setColorAt(0.75, QColor(255, 255, 255, 30))
        top_bevel.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(QPen(QBrush(top_bevel), 1.0))
        painter.drawLine(4, 2, w - 5, 2)

        # Left edge highlight
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        painter.drawLine(2, 4, 2, h - 5)
