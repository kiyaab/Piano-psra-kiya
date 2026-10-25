"""
KIYA Piano Studio Pro - Multi-Pad Hardware Control Panel (PSR-S975 Style)
Contains:
- Four tactile Multi-Pad buttons [PAD 1] - [PAD 4] with green/amber activity LEDs
- [PAD STOP] button
- [PAD SELECT] button to open bank/phrase picker
- Integrated sound trigger logic routing to Synthesizer percussion/chords/phrases
"""

from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)

from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class MultiPadPanel(QWidget):
    """
    Physical Multi-Pad control section:
    - [PAD 1] [PAD 2] [PAD 3] [PAD 4]
    - [STOP]
    - [SELECT]
    """
    padTriggered = Signal(int)   # pad index 1-4
    padStopped = Signal()
    padSelectRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MultiPadPanel")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(6)
        main_layout.setAlignment(Qt.AlignCenter)

        # Title
        lbl_title = QLabel("MULTI PAD")
        lbl_title.setFont(HardwareFonts.micro_bold())
        lbl_title.setStyleSheet("color: #7B8594; letter-spacing: 0.5px;")
        main_layout.addWidget(lbl_title)

        # 4 Multi-Pads
        self.pad_buttons: List[PhysicalButton] = []
        pad_labels = ["PAD 1", "PAD 2", "PAD 3", "PAD 4"]
        for idx, text in enumerate(pad_labels, 1):
            btn = PhysicalButton(
                str(idx),
                secondary_text="PHRASE",
                width=36,
                height=30,
                button_color=HardwareColors.BUTTON_DARK,
                indicator="green"
            )
            btn.clicked.connect(lambda checked=False, p=idx: self._on_pad_hit(p))
            self.pad_buttons.append(btn)
            main_layout.addWidget(btn)

        # STOP Button
        self.btn_stop = PhysicalButton(
            "STOP",
            width=42,
            height=30,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="red"
        )
        self.btn_stop.clicked.connect(self._on_stop)
        main_layout.addWidget(self.btn_stop)

        # SELECT Button
        self.btn_select = PhysicalButton(
            "SELECT",
            width=48,
            height=30,
            button_color=HardwareColors.BUTTON_DARK
        )
        self.btn_select.clicked.connect(self.padSelectRequested.emit)
        main_layout.addWidget(self.btn_select)

    def _on_pad_hit(self, pad_index: int):
        # Flash the LED on the triggered pad
        for i, btn in enumerate(self.pad_buttons, 1):
            if i == pad_index:
                btn.set_led(True)
        self.padTriggered.emit(pad_index)

    def _on_stop(self):
        for btn in self.pad_buttons:
            btn.set_led(False)
        self.btn_stop.flash(150)
        self.padStopped.emit()
