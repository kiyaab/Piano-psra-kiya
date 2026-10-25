"""
KIYA Piano Studio Pro - Bottom Performance Control Strip
Houses Quick Registration Memory slots 1-8, Layer/Split toggles, Master Panic, and Record status.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from app.constants import (
    COLOR_PANEL_MAIN,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED
)

class PerformanceStripWidget(QWidget):
    """Bottom performance strip with registration buttons 1-8 and quick controls."""

    registration_selected = Signal(int) # 0 to 7
    layer_toggled = Signal(bool)
    split_toggled = Signal(bool)
    panic_triggered = Signal()
    record_toggled = Signal()
    tap_tempo_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        # 1. Performance Toggles: Layer & Split
        self.btn_layer = QPushButton("DUAL / LAYER")
        self.btn_layer.setCheckable(True)
        self.btn_layer.setToolTip("Toggle Layering two instrument voices simultaneously")
        self.btn_layer.toggled.connect(self.layer_toggled.emit)
        layout.addWidget(self.btn_layer)

        self.btn_split = QPushButton("SPLIT")
        self.btn_split.setCheckable(True)
        self.btn_split.setToolTip("Divide keyboard into Left Hand and Right Hand voices")
        self.btn_split.toggled.connect(self.split_toggled.emit)
        layout.addWidget(self.btn_split)

        # Separator line
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"color: {COLOR_BORDER};")
        layout.addWidget(sep1)

        # 2. Registration Memory Slots 1-8
        reg_label = QLabel("REGISTRATION:")
        reg_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_TEXT_MUTED};")
        layout.addWidget(reg_label)

        self.reg_buttons: list[QPushButton] = []
        for i in range(8):
            btn = QPushButton(str(i + 1))
            btn.setCheckable(True)
            btn.setFixedSize(32, 32)
            btn.setToolTip(f"Recall Registration Memory Slot {i + 1}")
            slot_idx = i
            btn.clicked.connect(lambda checked, idx=slot_idx: self._on_reg_clicked(idx))
            self.reg_buttons.append(btn)
            layout.addWidget(btn)

        self.reg_buttons[0].setChecked(True)

        # Separator line
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"color: {COLOR_BORDER};")
        layout.addWidget(sep2)

        # 3. Tap Tempo
        self.btn_tap = QPushButton("TAP TEMPO")
        self.btn_tap.setToolTip("Tap rhythmically to set tempo")
        self.btn_tap.clicked.connect(self.tap_tempo_clicked.emit)
        layout.addWidget(self.btn_tap)

        # 4. Record Button
        self.btn_record = QPushButton("● REC")
        self.btn_record.setCheckable(True)
        self.btn_record.setStyleSheet("QPushButton:checked { background-color: #FF626B; color: white; }")
        self.btn_record.setToolTip("Start or stop performance recording")
        self.btn_record.clicked.connect(self.record_toggled.emit)
        layout.addWidget(self.btn_record)

        # 5. Master Panic Button
        self.btn_panic = QPushButton("PANIC / STOP")
        self.btn_panic.setStyleSheet(f"background-color: #2E1B20; border-color: {COLOR_ERROR}; color: {COLOR_ERROR};")
        self.btn_panic.setToolTip("Emergency kill all sounding notes and reset controllers")
        self.btn_panic.clicked.connect(self.panic_triggered.emit)
        layout.addWidget(self.btn_panic)

    def _on_reg_clicked(self, slot_idx: int):
        for i, btn in enumerate(self.reg_buttons):
            btn.blockSignals(True)
            btn.setChecked(i == slot_idx)
            btn.blockSignals(False)
        self.registration_selected.emit(slot_idx)

    def set_active_slot(self, slot_idx: int):
        for i, btn in enumerate(self.reg_buttons):
            btn.blockSignals(True)
            btn.setChecked(i == slot_idx)
            btn.blockSignals(False)
