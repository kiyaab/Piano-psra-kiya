"""
KIYA Piano Studio Pro - Arranger Chord Recognition Display Widget
Displays detected harmonic chords, roots, qualities, and bass inversions
in a backlit high-contrast workstation LCD frame.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QLinearGradient, QPen
from app.constants import (
    COLOR_BG,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED
)
from arranger.chord_detector import ChordInfo

class ChordDisplayWidget(QWidget):
    """Visual chord recognition indicator with backlit OLED/LCD styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(110, 48)
        self.chord_name = "---"
        self.chord_root = "-"
        self.chord_quality = ""
        self.chord_bass = ""
        self.is_active = False

    def set_chord(self, chord: ChordInfo):
        self.chord_name = chord.display_name
        self.chord_root = chord.root_name
        self.chord_quality = chord.quality if chord.quality != "Maj" else ""
        self.chord_bass = f"/{chord.bass_name}" if (chord.is_inversion and chord.bass_name != chord.root_name) else ""
        self.is_active = True
        self.update()

    def clear(self):
        self.chord_name = "---"
        self.chord_root = "-"
        self.chord_quality = ""
        self.chord_bass = ""
        self.is_active = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w = float(self.width())
        h = float(self.height())

        # LCD Frame Gradient
        bg_grad = QLinearGradient(0, 0, 0, h)
        if self.is_active:
            bg_grad.setColorAt(0.0, QColor("#141922"))
            bg_grad.setColorAt(1.0, QColor("#0A0C10"))
            border_color = QColor(COLOR_ACCENT_ORANGE)
        else:
            bg_grad.setColorAt(0.0, QColor("#12141A"))
            bg_grad.setColorAt(1.0, QColor("#08090C"))
            border_color = QColor(COLOR_BORDER)

        painter.setPen(QPen(border_color, 1.2))
        painter.setBrush(bg_grad)
        painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 6, 6)

        # Header tag
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        font = painter.font()
        font.setPointSize(7)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(8, 4, w - 16, 12), Qt.AlignmentFlag.AlignLeft, "CHORD")

        # Status Dot
        dot_color = QColor(COLOR_ACCENT_ORANGE) if self.is_active else QColor("#303846")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dot_color)
        painter.drawEllipse(QRectF(w - 14, 6, 6, 6))

        # Main Chord Readout
        font.setPointSize(15)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(COLOR_ACCENT_ORANGE if self.is_active else "#555F70"))

        text = self.chord_name if self.is_active else "---"
        painter.drawText(QRectF(4, 16, w - 8, h - 18), Qt.AlignmentFlag.AlignCenter, text)
