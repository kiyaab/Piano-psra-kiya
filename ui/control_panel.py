"""
KIYA Piano Studio Pro - Upper Hardware Control Panel (PSR-S975 Style)
Assembles the complete upper 55% of the instrument:
- Left Control Panel (Song transport, Master volume, Style categories, Tempo & Transpose)
- Central Recessed Color LCD Screen with softkeys [A]-[E] and [F]-[J]
- Metallic Rotary Encoder Jog Dial & Navigation cluster
- Right Instrument Panel (16 Voice categories, Part Select, Voice Effects)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame
)

from ui.arranger_controls import LeftControlPanel
from ui.lcd_screen import CentralLCDDisplay
from ui.rotary_encoder import RotaryEncoderCluster
from ui.instrument_buttons import RightInstrumentPanel
from ui.hardware_theme import HardwareColors


class HardwareControlPanel(QWidget):
    """
    Complete upper control panel widget for the PSR-S975 layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HardwareControlPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {HardwareColors.PANEL_DARK};")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # 1. Left Control Panel
        self.left_panel = LeftControlPanel(self)
        self.left_panel.setMaximumWidth(370)
        main_layout.addWidget(self.left_panel, 0)

        # 2. Central LCD Display (Recessed color screen with softkeys)
        self.lcd_screen = CentralLCDDisplay(self)
        self.lcd_screen.setMinimumWidth(520)
        main_layout.addWidget(self.lcd_screen, 1)

        # 3. Rotary Encoder & Nav Cluster
        self.rotary_cluster = RotaryEncoderCluster(self)
        self.rotary_cluster.setFixedWidth(185)
        main_layout.addWidget(self.rotary_cluster, 0)

        # 4. Right Instrument Selection & Voice Effects Panel
        self.right_panel = RightInstrumentPanel(self)
        self.right_panel.setMaximumWidth(350)
        main_layout.addWidget(self.right_panel, 0)
