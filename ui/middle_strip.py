"""
KIYA Piano Studio Pro - Middle Hardware Control Strip (PSR-S975 Style)
The horizontal control strip directly above the piano keys:
1. Arranger Style Sections (INTRO I-III, MAIN A-D, BREAK, ENDING I-III, ACMP, SYNC, START/STOP)
2. Hardware 4-Beat LED Flasher
3. Multi-Pad Panel (PAD 1-4, STOP, SELECT)
4. Registration Memory Strip (BANK -/+, MEMORY, Slots 1-8, FREEZE)
"""

from typing import List, Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)

from ui.physical_button import PhysicalButton
from ui.registration_panel import RegistrationPanel
from ui.multipad_panel import MultiPadPanel
from ui.widgets.beat_indicator import HardwareBeatIndicator
from ui.hardware_theme import HardwareColors, HardwareFonts


class MiddleControlStrip(QWidget):
    """
    Horizontal hardware strip separating the upper panel from the piano keybed:
    - Style sections & Transport
    - Beat indicator
    - Multi-pads
    - Registration memory
    """
    # Style / Arranger signals
    introRequested = Signal(int)       # 1, 2, 3
    variationChanged = Signal(str)     # "A", "B", "C", "D"
    fillRequested = Signal()
    breakRequested = Signal()
    endingRequested = Signal(int)      # 1, 2, 3
    acmpToggled = Signal(bool)
    syncStartToggled = Signal(bool)
    syncStopToggled = Signal(bool)
    startStopClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MiddleControlStrip")
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 4, 10, 4)
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignCenter)

        # =====================================================================
        # 1. STYLE CONTROLS & TRANSPORT GROUP
        # =====================================================================
        style_frame = QFrame()
        style_frame.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 2px;")
        sf_layout = QHBoxLayout(style_frame)
        sf_layout.setContentsMargins(4, 2, 4, 2)
        sf_layout.setSpacing(4)

        # ACMP ON/OFF
        self.btn_acmp = PhysicalButton("ACMP", secondary_text="ON/OFF", width=46, height=32, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_acmp.set_led(True)  # ACMP on by default
        self.btn_acmp.clicked.connect(self._toggle_acmp)
        sf_layout.addWidget(self.btn_acmp)

        # SYNC START / STOP
        self.btn_sync_start = PhysicalButton("SYNC", secondary_text="START", width=42, height=32, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_sync_start.set_led(True)  # Sync Start on by default
        self.btn_sync_start.clicked.connect(self._toggle_sync_start)
        sf_layout.addWidget(self.btn_sync_start)

        self.btn_sync_stop = PhysicalButton("SYNC", secondary_text="STOP", width=42, height=32, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_sync_stop.clicked.connect(self._toggle_sync_stop)
        sf_layout.addWidget(self.btn_sync_stop)

        # Large START / STOP Button
        self.btn_start_stop = PhysicalButton(
            "START",
            secondary_text="STOP",
            width=58,
            height=34,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="red"
        )
        self.btn_start_stop.clicked.connect(self.startStopClicked.emit)
        sf_layout.addWidget(self.btn_start_stop)

        # INTRO I, II, III
        self.btn_intro1 = PhysicalButton("INTRO I", width=42, height=30, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_intro1.clicked.connect(lambda: self.introRequested.emit(1))
        sf_layout.addWidget(self.btn_intro1)

        self.btn_intro2 = PhysicalButton("INTRO II", width=44, height=30, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_intro2.clicked.connect(lambda: self.introRequested.emit(2))
        sf_layout.addWidget(self.btn_intro2)

        # MAIN VARIATIONS A, B, C, D
        self.var_buttons: Dict[str, PhysicalButton] = {}
        for var in ["A", "B", "C", "D"]:
            btn = PhysicalButton(
                f"MAIN {var}",
                width=42,
                height=30,
                button_color=HardwareColors.BUTTON_DARK,
                indicator="green"
            )
            btn.set_led(var == "A")
            btn.clicked.connect(lambda checked=False, v=var: self._select_variation(v))
            self.var_buttons[var] = btn
            sf_layout.addWidget(btn)

        # BREAK
        self.btn_break = PhysicalButton("BREAK", width=40, height=30, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_break.clicked.connect(self.breakRequested.emit)
        sf_layout.addWidget(self.btn_break)

        # ENDING I, II, III
        self.btn_ending1 = PhysicalButton("ENDING I", width=44, height=30, button_color=HardwareColors.BUTTON_DARK, indicator="red")
        self.btn_ending1.clicked.connect(lambda: self.endingRequested.emit(1))
        sf_layout.addWidget(self.btn_ending1)

        self.btn_ending2 = PhysicalButton("ENDING II", width=46, height=30, button_color=HardwareColors.BUTTON_DARK, indicator="red")
        self.btn_ending2.clicked.connect(lambda: self.endingRequested.emit(2))
        sf_layout.addWidget(self.btn_ending2)

        main_layout.addWidget(style_frame)

        # =====================================================================
        # 2. HARDWARE BEAT INDICATOR
        # =====================================================================
        self.beat_indicator = HardwareBeatIndicator(self)
        main_layout.addWidget(self.beat_indicator)

        # =====================================================================
        # 3. MULTI-PAD PANEL
        # =====================================================================
        self.multipad_panel = MultiPadPanel(self)
        main_layout.addWidget(self.multipad_panel)

        # =====================================================================
        # 4. REGISTRATION MEMORY STRIP
        # =====================================================================
        self.registration_panel = RegistrationPanel(self)
        main_layout.addWidget(self.registration_panel)

        # State tracking
        self._acmp_enabled = True
        self._sync_start_enabled = True
        self._sync_stop_enabled = False
        self._current_variation = "A"

    def _toggle_acmp(self):
        self._acmp_enabled = not self._acmp_enabled
        self.btn_acmp.set_led(self._acmp_enabled)
        self.acmpToggled.emit(self._acmp_enabled)

    def _toggle_sync_start(self):
        self._sync_start_enabled = not self._sync_start_enabled
        self.btn_sync_start.set_led(self._sync_start_enabled)
        self.syncStartToggled.emit(self._sync_start_enabled)

    def _toggle_sync_stop(self):
        self._sync_stop_enabled = not self._sync_stop_enabled
        self.btn_sync_stop.set_led(self._sync_stop_enabled)
        self.syncStopToggled.emit(self._sync_stop_enabled)

    def _select_variation(self, var: str):
        self._current_variation = var
        for v, btn in self.var_buttons.items():
            btn.set_led(v == var)
        self.variationChanged.emit(var)

    def set_playing_state(self, is_playing: bool):
        """Update Start/Stop LED: Green when playing, Red when stopped."""
        self.btn_start_stop.set_led_color("green" if is_playing else "red")
        self.btn_start_stop.set_led(True)
