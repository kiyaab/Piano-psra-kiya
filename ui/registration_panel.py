"""
KIYA Piano Studio Pro - Registration Memory Hardware Panel (PSR-S975 Style)
Contains:
- BANK - / + buttons
- MEMORY button with red LED indicator
- Quick-access Registration Slots [1] to [8] with blue/green status LEDs
- FREEZE button with amber indicator
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)

from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class RegistrationPanel(QWidget):
    """
    Physical registration memory control strip:
    - BANK [-] and [+]
    - [MEMORY]
    - [1] [2] [3] [4] [5] [6] [7] [8]
    - [FREEZE]
    """
    bankChanged = Signal(int)       # delta: -1 or +1
    memoryArmed = Signal(bool)      # whether memory arming is active
    slotRecalled = Signal(int)      # slot index 1-8
    slotStored = Signal(int)        # slot index 1-8
    freezeToggled = Signal(bool)
    loadBankRequested = Signal()
    exportBankRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RegistrationPanel")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignCenter)

        # Title & Bank Display
        bank_box = QVBoxLayout()
        bank_box.setSpacing(2)
        bank_box.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("REGIST")
        lbl_title.setFont(HardwareFonts.micro_bold())
        lbl_title.setStyleSheet("color: #7B8594; letter-spacing: 0.5px;")
        bank_box.addWidget(lbl_title, 0, Qt.AlignCenter)

        self.lbl_bank = QLabel("BANK 01")
        self.lbl_bank.setFont(HardwareFonts.micro_bold())
        self.lbl_bank.setFixedWidth(56)
        self.lbl_bank.setAlignment(Qt.AlignCenter)
        self.lbl_bank.setStyleSheet("background: #080D12; color: #4DA8DA; border: 1px solid #1E2B38; padding: 2px 2px; border-radius: 2px;")
        bank_box.addWidget(self.lbl_bank, 0, Qt.AlignCenter)
        main_layout.addLayout(bank_box)

        # Bank - / + Buttons
        self.btn_bank_dec = PhysicalButton("−", width=24, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_bank_dec.clicked.connect(lambda: self._step_bank(-1))
        main_layout.addWidget(self.btn_bank_dec)

        self.btn_bank_inc = PhysicalButton("+", width=24, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_bank_inc.clicked.connect(lambda: self._step_bank(1))
        main_layout.addWidget(self.btn_bank_inc)

        # MEMORY Arm Button (Red LED)
        self.btn_memory = PhysicalButton(
            "MEMORY",
            width=54,
            height=28,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="red"
        )
        self.btn_memory.clicked.connect(self._toggle_memory_arm)
        main_layout.addWidget(self.btn_memory)

        # Slots 1 - 8 Buttons
        self.slot_buttons: List[PhysicalButton] = []
        for i in range(1, 9):
            btn = PhysicalButton(
                str(i),
                width=28,
                height=28,
                button_color=HardwareColors.BUTTON_DARK,
                indicator="blue" if i == 1 else None
            )
            btn.clicked.connect(lambda checked=False, slot=i: self._on_slot_clicked(slot))
            self.slot_buttons.append(btn)
            main_layout.addWidget(btn)

        # FREEZE Button (Amber LED)
        self.btn_freeze = PhysicalButton(
            "FREEZE",
            width=48,
            height=28,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="amber"
        )
        self.btn_freeze.clicked.connect(self._toggle_freeze)
        main_layout.addWidget(self.btn_freeze)

        # Quick LOAD .RGT / EXPORT buttons
        self.btn_load_rgt = PhysicalButton(
            "LOAD",
            secondary_text=".RGT",
            width=50,
            height=28,
            button_color=HardwareColors.BUTTON_DARK,
            indicator="blue"
        )
        self.btn_load_rgt.clicked.connect(self.loadBankRequested.emit)
        main_layout.addWidget(self.btn_load_rgt)

        # Internal state
        self._current_bank = 1
        self._is_memory_armed = False
        self._is_frozen = False
        self._active_slot = 1

    def _step_bank(self, delta: int):
        self._current_bank = max(1, min(99, self._current_bank + delta))
        self.lbl_bank.setText(f"BANK {self._current_bank:02d}")
        self.bankChanged.emit(self._current_bank)

    def _toggle_memory_arm(self):
        self._is_memory_armed = not self._is_memory_armed
        self.btn_memory.set_led(self._is_memory_armed)
        self.memoryArmed.emit(self._is_memory_armed)

    def _on_slot_clicked(self, slot_num: int):
        if self._is_memory_armed:
            # Store to slot
            self._is_memory_armed = False
            self.btn_memory.set_led(False)
            self._set_active_slot(slot_num)
            self.slotStored.emit(slot_num)
        else:
            # Recall slot
            self._set_active_slot(slot_num)
            self.slotRecalled.emit(slot_num)

    def _set_active_slot(self, slot_num: int):
        self._active_slot = slot_num
        for i, btn in enumerate(self.slot_buttons, 1):
            btn.set_led(i == slot_num)

    def _toggle_freeze(self):
        self._is_frozen = not self._is_frozen
        self.btn_freeze.set_led(self._is_frozen)
        self.freezeToggled.emit(self._is_frozen)
