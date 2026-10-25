"""
KIYA Piano Studio Pro - Right Instrument Selection & Voice Effects Panel (PSR-S975 Style)
Contains:
1. 16 Instrument Category selection buttons (Piano, E.Piano, Organ, Strings, Brass, Synth, etc.)
2. Keyboard Part Select (R1, R2, Left)
3. Keyboard Part On/Off toggles with jewel LEDs
4. Performance Effects (Sustain, Touch, Harmony/Echo, DSP, Mono/Poly)
"""

from typing import Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
)

from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class RightInstrumentPanel(QWidget):
    """
    Upper-right hardware panel:
    - 16 Instrument category grid
    - Part Select [LEFT], [R1], [R2]
    - Part On/Off toggles
    - Voice Effects (Sustain, Touch, Harmony, DSP)
    """
    categorySelected = Signal(str)
    partSelected = Signal(str)       # "R1", "R2", "LEFT"
    partToggled = Signal(str, bool)   # "R1"|"R2"|"LEFT", is_on
    sustainToggled = Signal(bool)
    touchToggled = Signal(bool)
    harmonyToggled = Signal(bool)
    dspToggled = Signal(bool)
    monoPolyToggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightInstrumentPanel")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(8)

        # --- SECTION 1: 16 VOICE CATEGORIES GRID (4 cols x 4 rows) ---
        cat_group = QFrame()
        cat_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        cg_layout = QVBoxLayout(cat_group)
        cg_layout.setContentsMargins(6, 4, 6, 4)
        cg_layout.setSpacing(4)

        cg_title = QLabel("VOICE CATEGORIES")
        cg_title.setFont(HardwareFonts.micro_bold())
        cg_title.setStyleSheet("color: #657585;")
        cg_layout.addWidget(cg_title)

        cat_grid = QGridLayout()
        cat_grid.setSpacing(4)

        categories = [
            ("PIANO", 0, 0), ("E. PIANO", 0, 1), ("ORGAN", 0, 2), ("ACCORDION", 0, 3),
            ("GUITAR", 1, 0), ("BASS", 1, 1), ("STRINGS", 1, 2), ("CHOIR", 1, 3),
            ("BRASS", 2, 0), ("WOODWIND", 2, 1), ("SAXOPHONE", 2, 2), ("SYNTH LEAD", 2, 3),
            ("SYNTH PAD", 3, 0), ("PERCUSSION", 3, 1), ("DRUM KITS", 3, 2), ("EXPANSION", 3, 3)
        ]

        self.cat_buttons: Dict[str, PhysicalButton] = {}
        for cat_name, row, col in categories:
            btn = PhysicalButton(
                cat_name,
                width=68,
                height=25,
                button_color=HardwareColors.BUTTON_DARK,
                indicator="green" if cat_name == "PIANO" else None
            )
            btn.clicked.connect(lambda c=cat_name: self._on_category_clicked(c))
            self.cat_buttons[cat_name] = btn
            cat_grid.addWidget(btn, row, col)

        cg_layout.addLayout(cat_grid)
        main_layout.addWidget(cat_group)

        # --- SECTION 2: KEYBOARD PART SELECT & ON/OFF ---
        part_group = QFrame()
        part_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        pg_layout = QVBoxLayout(part_group)
        pg_layout.setContentsMargins(6, 4, 6, 4)
        pg_layout.setSpacing(4)

        # Part Select Row
        ps_lbl = QLabel("PART SELECT")
        ps_lbl.setFont(HardwareFonts.micro_bold())
        ps_lbl.setStyleSheet("color: #657585;")
        pg_layout.addWidget(ps_lbl)

        ps_row = QHBoxLayout()
        ps_row.setSpacing(6)

        self.btn_sel_left = PhysicalButton("LEFT", width=60, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_sel_left.clicked.connect(lambda: self._select_part("LEFT"))
        ps_row.addWidget(self.btn_sel_left)

        self.btn_sel_r1 = PhysicalButton("RIGHT 1", width=68, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_sel_r1.set_led(True)  # R1 selected by default
        self.btn_sel_r1.clicked.connect(lambda: self._select_part("R1"))
        ps_row.addWidget(self.btn_sel_r1)

        self.btn_sel_r2 = PhysicalButton("RIGHT 2", width=68, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="blue")
        self.btn_sel_r2.clicked.connect(lambda: self._select_part("R2"))
        ps_row.addWidget(self.btn_sel_r2)

        ps_row.addStretch()
        pg_layout.addLayout(ps_row)

        # Part ON/OFF Row
        po_lbl = QLabel("PART ON / OFF")
        po_lbl.setFont(HardwareFonts.micro_bold())
        po_lbl.setStyleSheet("color: #657585;")
        pg_layout.addWidget(po_lbl)

        po_row = QHBoxLayout()
        po_row.setSpacing(6)

        self.btn_on_left = PhysicalButton("LEFT", secondary_text="SPLIT", width=60, height=28, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_on_left.clicked.connect(lambda: self._toggle_part("LEFT"))
        po_row.addWidget(self.btn_on_left)

        self.btn_on_r1 = PhysicalButton("RIGHT 1", secondary_text="MAIN", width=68, height=28, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_on_r1.set_led(True)  # R1 On by default
        self.btn_on_r1.clicked.connect(lambda: self._toggle_part("R1"))
        po_row.addWidget(self.btn_on_r1)

        self.btn_on_r2 = PhysicalButton("RIGHT 2", secondary_text="LAYER", width=68, height=28, button_color=HardwareColors.BUTTON_DARK, indicator="blue")
        self.btn_on_r2.clicked.connect(lambda: self._toggle_part("R2"))
        po_row.addWidget(self.btn_on_r2)

        po_row.addStretch()
        pg_layout.addLayout(po_row)

        main_layout.addWidget(part_group)

        # --- SECTION 3: VOICE EFFECTS CLUSTER ---
        fx_group = QFrame()
        fx_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        fg_layout = QVBoxLayout(fx_group)
        fg_layout.setContentsMargins(6, 4, 6, 4)
        fg_layout.setSpacing(4)

        fg_title = QLabel("VOICE EFFECTS & PERFORMANCE")
        fg_title.setFont(HardwareFonts.micro_bold())
        fg_title.setStyleSheet("color: #657585;")
        fg_layout.addWidget(fg_title)

        fg_row = QHBoxLayout()
        fg_row.setSpacing(4)

        self.btn_sustain = PhysicalButton("SUSTAIN", width=54, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_sustain.clicked.connect(self._toggle_sustain)
        fg_row.addWidget(self.btn_sustain)

        self.btn_touch = PhysicalButton("TOUCH", width=50, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_touch.set_led(True)  # Touch active by default
        self.btn_touch.clicked.connect(self._toggle_touch)
        fg_row.addWidget(self.btn_touch)

        self.btn_harmony = PhysicalButton("HARMONY", width=58, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_harmony.clicked.connect(self._toggle_harmony)
        fg_row.addWidget(self.btn_harmony)

        self.btn_dsp = PhysicalButton("DSP", width=44, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="blue")
        self.btn_dsp.set_led(True)  # DSP active by default
        self.btn_dsp.clicked.connect(self._toggle_dsp)
        fg_row.addWidget(self.btn_dsp)

        self.btn_mono = PhysicalButton("MONO", width=48, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_mono.clicked.connect(self._toggle_mono)
        fg_row.addWidget(self.btn_mono)

        fg_layout.addLayout(fg_row)
        main_layout.addWidget(fx_group)

        # State tracking
        self._part_states = {"R1": True, "R2": False, "LEFT": False}
        self._active_selected_part = "R1"
        self._sustain_active = False
        self._touch_active = True
        self._harmony_active = False
        self._dsp_active = True
        self._mono_active = False

    def _on_category_clicked(self, cat_name: str):
        for name, btn in self.cat_buttons.items():
            btn.set_led(name == cat_name)
        self.categorySelected.emit(cat_name)

    def _select_part(self, part: str):
        self._active_selected_part = part
        self.btn_sel_left.set_led(part == "LEFT")
        self.btn_sel_r1.set_led(part == "R1")
        self.btn_sel_r2.set_led(part == "R2")
        self.partSelected.emit(part)

    def _toggle_part(self, part: str):
        self._part_states[part] = not self._part_states[part]
        is_on = self._part_states[part]
        if part == "LEFT":
            self.btn_on_left.set_led(is_on)
        elif part == "R1":
            self.btn_on_r1.set_led(is_on)
        elif part == "R2":
            self.btn_on_r2.set_led(is_on)
        self.partToggled.emit(part, is_on)

    def _toggle_sustain(self):
        self._sustain_active = not self._sustain_active
        self.btn_sustain.set_led(self._sustain_active)
        self.sustainToggled.emit(self._sustain_active)

    def _toggle_touch(self):
        self._touch_active = not self._touch_active
        self.btn_touch.set_led(self._touch_active)
        self.touchToggled.emit(self._touch_active)

    def _toggle_harmony(self):
        self._harmony_active = not self._harmony_active
        self.btn_harmony.set_led(self._harmony_active)
        self.harmonyToggled.emit(self._harmony_active)

    def _toggle_dsp(self):
        self._dsp_active = not self._dsp_active
        self.btn_dsp.set_led(self._dsp_active)
        self.dspToggled.emit(self._dsp_active)

    def _toggle_mono(self):
        self._mono_active = not self._mono_active
        self.btn_mono.set_led(self._mono_active)
        self.monoPolyToggled.emit(self._mono_active)
