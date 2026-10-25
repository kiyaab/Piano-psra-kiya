"""
KIYA Piano Studio Pro - Master Arranger Workstation Console
Authentic hardware console layout inspired by Yamaha Genos / PSR-SX900 and Korg Pa5X.
Unifies central backlit multi-display, full style & section controls, transpose & octave,
one-touch voice selection, mixer faders, 4 multi-pads, and registration memory on one cohesive page.
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QGroupBox, QSlider, QComboBox, QScrollArea
)
from PySide6.QtGui import QColor, QFont
from app.constants import (
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_PANEL_SECONDARY,
    COLOR_PANEL_ELEVATED,
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_ORANGE_HOVER,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_BLUE_HOVER,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    SECTION_INTRO,
    SECTION_MAIN_A,
    SECTION_MAIN_B,
    SECTION_MAIN_C,
    SECTION_MAIN_D,
    SECTION_FILL_AA,
    SECTION_FILL_BB,
    SECTION_FILL_CC,
    SECTION_FILL_DD,
    SECTION_BREAK,
    SECTION_ENDING
)
from ui.widgets.waveform_widget import WaveformWidget
from ui.widgets.chord_display import ChordDisplayWidget
from ui.widgets.beat_indicator import BeatIndicatorWidget

class PerformancePage(QWidget):
    """Complete Master Arranger Keyboard Workstation Console."""

    # Arranger Playback & Sections
    start_stop_requested = Signal()
    section_requested = Signal(str)
    fill_requested = Signal(str, str) # fill_name, target_main
    sync_start_toggled = Signal(bool)
    sync_stop_toggled = Signal(bool)
    acmp_toggled = Signal(bool)
    style_selected = Signal(str)

    # Tempo & Metronome
    tempo_changed = Signal(int)
    tap_tempo_clicked = Signal()
    metronome_toggled = Signal(bool)

    # Transposition & Tuning
    transpose_changed = Signal(int)  # -12 to +12
    octave_changed = Signal(int)     # -3 to +3

    # Voices & Performance Modes
    voice_assigned = Signal(str, int)  # target ("right1", "right2", "left"), program (0-127)
    layer_toggled = Signal(bool)
    split_toggled = Signal(bool)
    sustain_toggled = Signal(bool)
    touch_curve_changed = Signal(str)  # "normal", "soft", "hard"
    open_voice_browser_requested = Signal()

    # Chord Recognition
    chord_mode_changed = Signal(str)   # "full" or "simplified"

    # Registrations & Multi-Pads
    registration_selected = Signal(int) # 0 to 7
    registration_store_requested = Signal(int)
    multipad_triggered = Signal(int)   # 0 to 3

    # Hardware Faders
    master_vol_changed = Signal(float)
    acmp_vol_changed = Signal(float)
    keyboard_vol_changed = Signal(float)
    split_vol_changed = Signal(float)
    reverb_changed = Signal(float)

    # One-Touch Preset Voices Definition (Name, Category, GM Program)
    ONE_TOUCH_VOICES = [
        ("Grand Piano", "Piano", 0),
        ("E. Piano", "E.Piano", 4),
        ("Church Organ", "Organ", 19),
        ("Rock Organ", "Organ", 18),
        ("Strings", "Ensemble", 48),
        ("Brass Section", "Brass", 61),
        ("Synth Lead", "Synth", 80),
        ("Warm Pad", "Synth", 89),
        ("Acoustic Guitar", "Guitar", 24),
        ("Finger Bass", "Bass", 33),
        ("Alto Sax", "Reed", 65),
        ("Accordion", "Accordion", 21),
    ]

    # Style Categories Definition
    STYLE_CATEGORIES = [
        ("POP", "Pop Groove"),
        ("ROCK", "Classic Rock"),
        ("BALLAD", "Slow Ballad"),
        ("DANCE", "80s Synthwave"),
        ("FUNK", "Funk & Disco"),
        ("JAZZ", "Jazz Swing"),
        ("LATIN", "Latin Bossa Nova"),
        ("WALTZ", "Classical Waltz"),
        ("R&B", "R&B Smooth Soul"),
        ("WORLD", "Ethiopian Tizita"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        # State tracking
        self.current_transpose = 0
        self.current_octave = 0
        self.current_tempo = 120
        self.current_time_sig = "4/4"
        self.touch_modes = ["normal", "soft", "hard"]
        self.current_touch_idx = 0
        self.current_section = SECTION_MAIN_A

        # Layout Setup
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # -------------------------------------------------------------
        # 1. CENTRAL WORKSTATION COLOR DISPLAY SCREEN (OLED / LCD CONSOLE)
        # -------------------------------------------------------------
        self._build_central_display(main_layout)

        # -------------------------------------------------------------
        # 2. MASTER HARDWARE DECK (LEFT: STYLE & ARRANGER | RIGHT: VOICES & OTS)
        # -------------------------------------------------------------
        deck_layout = QHBoxLayout()
        deck_layout.setSpacing(10)

        # Left Deck: Style & Arranger Section
        self._build_arranger_deck(deck_layout)

        # Right Deck: Voices & Performance Controls
        self._build_voice_deck(deck_layout)

        main_layout.addLayout(deck_layout, 1)

        # -------------------------------------------------------------
        # 3. BOTTOM HARDWARE FADER STRIP (Master, Accompaniment, Voice Volumes)
        # -------------------------------------------------------------
        self._build_fader_strip(main_layout)

    # =========================================================================
    # SECTION 1: Central Workstation Color Display
    # =========================================================================
    def _build_central_display(self, parent_layout: QVBoxLayout):
        """Build glowing hardware LCD screen showing Style, Chord, Tempo, Transpose, Waveform."""
        disp_frame = QFrame()
        disp_frame.setObjectName("WorkstationLCD")
        disp_frame.setStyleSheet("""
            QFrame#WorkstationLCD {
                background-color: #0B0E14;
                border: 2px solid #232A36;
                border-radius: 8px;
                padding: 6px 12px;
            }
        """)

        disp_layout = QHBoxLayout(disp_frame)
        disp_layout.setContentsMargins(6, 4, 6, 4)
        disp_layout.setSpacing(12)

        # --- A. Style & Rhythm Monitor ---
        style_box = QVBoxLayout()
        style_box.setSpacing(2)

        cat_lbl = QLabel("CURRENT STYLE")
        cat_lbl.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COLOR_TEXT_MUTED}; letter-spacing: 1px;")
        style_box.addWidget(cat_lbl)

        self.lbl_style_title = QLabel("Pop Groove")
        self.lbl_style_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        style_box.addWidget(self.lbl_style_title)

        self.lbl_style_info = QLabel("POP • 120 BPM • 4/4")
        self.lbl_style_info.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        style_box.addWidget(self.lbl_style_info)

        # Bar & Beat & Flasher
        beat_row = QHBoxLayout()
        beat_row.setSpacing(6)
        self.lbl_bar_beat = QLabel("BAR: 1 | BEAT: 1")
        self.lbl_bar_beat.setStyleSheet(f"background-color: #151922; color: {COLOR_SUCCESS}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        beat_row.addWidget(self.lbl_bar_beat)

        self.beat_indicator = BeatIndicatorWidget()
        beat_row.addWidget(self.beat_indicator)
        style_box.addLayout(beat_row)

        disp_layout.addLayout(style_box, 3)

        # Separator line
        disp_layout.addWidget(self._create_vsep())

        # --- B. Backlit Chord Visualizer ---
        chord_box = QVBoxLayout()
        chord_box.setSpacing(2)
        chord_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.chord_widget = ChordDisplayWidget()
        chord_box.addWidget(self.chord_widget)

        self.lbl_chord_mode = QLabel("MODE: FINGERED")
        self.lbl_chord_mode.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COLOR_TEXT_MUTED};")
        self.lbl_chord_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chord_box.addWidget(self.lbl_chord_mode)

        disp_layout.addLayout(chord_box, 2)

        # Separator line
        disp_layout.addWidget(self._create_vsep())

        # --- C. Transpose & Octave Hardware Controls ---
        tune_box = QVBoxLayout()
        tune_box.setSpacing(4)
        tune_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Transpose row
        tr_row = QHBoxLayout()
        tr_row.setSpacing(4)
        btn_tr_down = QPushButton("-")
        btn_tr_down.setFixedSize(22, 22)
        btn_tr_down.setToolTip("Transpose Down by 1 Semitone")
        btn_tr_down.clicked.connect(self._transpose_down)
        tr_row.addWidget(btn_tr_down)

        self.lbl_transpose = QLabel("TRANSPOSE: 0")
        self.lbl_transpose.setStyleSheet(f"background-color: #141820; border: 1px solid {COLOR_BORDER}; color: {COLOR_ACCENT_ORANGE}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        self.lbl_transpose.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tr_row.addWidget(self.lbl_transpose)

        btn_tr_up = QPushButton("+")
        btn_tr_up.setFixedSize(22, 22)
        btn_tr_up.setToolTip("Transpose Up by 1 Semitone")
        btn_tr_up.clicked.connect(self._transpose_up)
        tr_row.addWidget(btn_tr_up)

        btn_tr_zero = QPushButton("0")
        btn_tr_zero.setFixedSize(22, 22)
        btn_tr_zero.setToolTip("Reset Transposition to 0")
        btn_tr_zero.clicked.connect(self._transpose_reset)
        tr_row.addWidget(btn_tr_zero)
        tune_box.addLayout(tr_row)

        # Octave row
        oct_row = QHBoxLayout()
        oct_row.setSpacing(4)
        btn_oct_down = QPushButton("-")
        btn_oct_down.setFixedSize(22, 22)
        btn_oct_down.setToolTip("Octave Shift Down")
        btn_oct_down.clicked.connect(self._octave_down)
        oct_row.addWidget(btn_oct_down)

        self.lbl_octave = QLabel("OCTAVE: 0")
        self.lbl_octave.setStyleSheet(f"background-color: #141820; border: 1px solid {COLOR_BORDER}; color: {COLOR_ACCENT_BLUE}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        self.lbl_octave.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oct_row.addWidget(self.lbl_octave)

        btn_oct_up = QPushButton("+")
        btn_oct_up.setFixedSize(22, 22)
        btn_oct_up.setToolTip("Octave Shift Up")
        btn_oct_up.clicked.connect(self._octave_up)
        oct_row.addWidget(btn_oct_up)

        btn_oct_zero = QPushButton("0")
        btn_oct_zero.setFixedSize(22, 22)
        btn_oct_zero.setToolTip("Reset Octave Shift to 0")
        btn_oct_zero.clicked.connect(self._octave_reset)
        oct_row.addWidget(btn_oct_zero)
        tune_box.addLayout(oct_row)

        disp_layout.addLayout(tune_box, 3)

        # Separator line
        disp_layout.addWidget(self._create_vsep())

        # --- D. Active Voices Monitor ---
        voice_mon_box = QVBoxLayout()
        voice_mon_box.setSpacing(2)

        v_hdr = QLabel("ACTIVE VOICES")
        v_hdr.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COLOR_TEXT_MUTED}; letter-spacing: 1px;")
        voice_mon_box.addWidget(v_hdr)

        self.lbl_r1_mon = QLabel("R1: Acoustic Grand Piano")
        self.lbl_r1_mon.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        voice_mon_box.addWidget(self.lbl_r1_mon)

        self.lbl_r2_mon = QLabel("R2: String Ensemble 1 (Off)")
        self.lbl_r2_mon.setStyleSheet("font-size: 10px; color: #707C8D;")
        voice_mon_box.addWidget(self.lbl_r2_mon)

        self.lbl_left_mon = QLabel("Left: Acoustic Bass (Off)")
        self.lbl_left_mon.setStyleSheet("font-size: 10px; color: #707C8D;")
        voice_mon_box.addWidget(self.lbl_left_mon)

        disp_layout.addLayout(voice_mon_box, 3)

        # Separator line
        disp_layout.addWidget(self._create_vsep())

        # --- E. Real-Time Oscilloscope Waveform Monitor ---
        wave_box = QVBoxLayout()
        wave_box.setSpacing(2)
        w_hdr = QLabel("AUDIO MONITOR")
        w_hdr.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COLOR_TEXT_MUTED}; letter-spacing: 1px;")
        wave_box.addWidget(w_hdr)

        self.waveform_widget = WaveformWidget()
        self.waveform_widget.setFixedSize(130, 42)
        wave_box.addWidget(self.waveform_widget)

        disp_layout.addLayout(wave_box, 2)

        parent_layout.addWidget(disp_frame)

    # =========================================================================
    # SECTION 2: Arranger & Style Deck (Left Side)
    # =========================================================================
    def _build_arranger_deck(self, parent_layout: QHBoxLayout):
        """Build Arranger & Style Section with Categories, Sections, Start/Stop, Tempo."""
        arr_group = QGroupBox("STYLE & ARRANGER CONTROLS")
        arr_layout = QVBoxLayout(arr_group)
        arr_layout.setContentsMargins(8, 8, 8, 8)
        arr_layout.setSpacing(8)

        # 1. Style Category Selectors (Top Row)
        cat_scroll = QHBoxLayout()
        cat_scroll.setSpacing(4)
        for cat_name, default_style in self.STYLE_CATEGORIES:
            btn_cat = QPushButton(cat_name)
            btn_cat.setFixedHeight(26)
            btn_cat.setStyleSheet(f"font-size: 10px; font-weight: bold; padding: 2px 6px;")
            btn_cat.clicked.connect(lambda ch, s=default_style: self.select_style_name(s))
            cat_scroll.addWidget(btn_cat)
        arr_layout.addLayout(cat_scroll)

        # 2. Style Dropdown Quick-Picker
        picker_row = QHBoxLayout()
        picker_row.setSpacing(8)
        picker_lbl = QLabel("STYLE:")
        picker_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_TEXT_MUTED};")
        picker_row.addWidget(picker_lbl)

        self.style_combo = QComboBox()
        self.style_combo.setStyleSheet("font-size: 12px; font-weight: bold; padding: 4px 8px;")
        # Populate all 12 styles
        styles_list = [
            ("Pop Groove (120 BPM - Pop)", "Pop Groove"),
            ("Classic Rock (130 BPM - Rock)", "Classic Rock"),
            ("Slow Ballad (68 BPM - Ballad)", "Slow Ballad"),
            ("80s Synthwave (124 BPM - Dance)", "80s Synthwave"),
            ("Funk & Disco (116 BPM - Dance)", "Funk & Disco"),
            ("Jazz Swing (140 BPM - Jazz)", "Jazz Swing"),
            ("Latin Bossa Nova (128 BPM - Latin)", "Latin Bossa Nova"),
            ("Classical Waltz (138 BPM - Classical)", "Classical Waltz"),
            ("R&B Smooth Soul (84 BPM - R&B)", "R&B Smooth Soul"),
            ("Ethiopian Tizita (105 BPM - World)", "Ethiopian Tizita"),
            ("Reggae Sunshine (80 BPM - World)", "Reggae Sunshine"),
            ("Country Folk (112 BPM - Country)", "Country Folk"),
        ]
        for title, s_name in styles_list:
            self.style_combo.addItem(title, s_name)
        self.style_combo.currentIndexChanged.connect(self._on_style_combo_changed)
        picker_row.addWidget(self.style_combo, 1)

        # Metronome button
        self.btn_metronome = QPushButton("⏱ METRO")
        self.btn_metronome.setCheckable(True)
        self.btn_metronome.setToolTip("Toggle audible metronome click")
        self.btn_metronome.toggled.connect(self.metronome_toggled.emit)
        picker_row.addWidget(self.btn_metronome)

        # Chord Mode button
        self.btn_chord_mode = QPushButton("FINGERED")
        self.btn_chord_mode.setToolTip("Switch between Full Fingered and Single-Finger Easy chord mode")
        self.btn_chord_mode.clicked.connect(self._toggle_chord_mode)
        picker_row.addWidget(self.btn_chord_mode)

        arr_layout.addLayout(picker_row)

        # 3. Arranger Sections Matrix (Yamaha PSR / Korg Pa Hardware Button Matrix)
        sec_grid = QGridLayout()
        sec_grid.setSpacing(6)

        # Row 0: Intro 1, Main A, Main B, Main C, Main D, Ending 1
        self.btn_intro = QPushButton("INTRO")
        self.btn_intro.clicked.connect(lambda: self.section_requested.emit(SECTION_INTRO))
        sec_grid.addWidget(self.btn_intro, 0, 0)

        self.btn_main_a = QPushButton("MAIN A")
        self.btn_main_a.setCheckable(True)
        self.btn_main_a.setChecked(True)
        self.btn_main_a.clicked.connect(lambda: self._select_main(SECTION_MAIN_A))
        sec_grid.addWidget(self.btn_main_a, 0, 1)

        self.btn_main_b = QPushButton("MAIN B")
        self.btn_main_b.setCheckable(True)
        self.btn_main_b.clicked.connect(lambda: self._select_main(SECTION_MAIN_B))
        sec_grid.addWidget(self.btn_main_b, 0, 2)

        self.btn_main_c = QPushButton("MAIN C")
        self.btn_main_c.setCheckable(True)
        self.btn_main_c.clicked.connect(lambda: self._select_main(SECTION_MAIN_C))
        sec_grid.addWidget(self.btn_main_c, 0, 3)

        self.btn_main_d = QPushButton("MAIN D")
        self.btn_main_d.setCheckable(True)
        self.btn_main_d.clicked.connect(lambda: self._select_main(SECTION_MAIN_D))
        sec_grid.addWidget(self.btn_main_d, 0, 4)

        self.btn_ending = QPushButton("ENDING")
        self.btn_ending.clicked.connect(lambda: self.section_requested.emit(SECTION_ENDING))
        sec_grid.addWidget(self.btn_ending, 0, 5)

        # Row 1: Break, Fill AA, Fill BB, Fill CC, Fill DD, Sync Stop
        self.btn_break = QPushButton("BREAK")
        self.btn_break.clicked.connect(lambda: self.section_requested.emit(SECTION_BREAK))
        sec_grid.addWidget(self.btn_break, 1, 0)

        self.btn_fill_aa = QPushButton("FILL A")
        self.btn_fill_aa.clicked.connect(lambda: self.fill_requested.emit(SECTION_FILL_AA, SECTION_MAIN_A))
        sec_grid.addWidget(self.btn_fill_aa, 1, 1)

        self.btn_fill_bb = QPushButton("FILL B")
        self.btn_fill_bb.clicked.connect(lambda: self.fill_requested.emit(SECTION_FILL_BB, SECTION_MAIN_B))
        sec_grid.addWidget(self.btn_fill_bb, 1, 2)

        self.btn_fill_cc = QPushButton("FILL C")
        self.btn_fill_cc.clicked.connect(lambda: self.fill_requested.emit(SECTION_FILL_CC, SECTION_MAIN_C))
        sec_grid.addWidget(self.btn_fill_cc, 1, 3)

        self.btn_fill_dd = QPushButton("FILL D")
        self.btn_fill_dd.clicked.connect(lambda: self.fill_requested.emit(SECTION_FILL_DD, SECTION_MAIN_D))
        sec_grid.addWidget(self.btn_fill_dd, 1, 4)

        self.btn_sync_stop = QPushButton("SYNC STOP")
        self.btn_sync_stop.setCheckable(True)
        self.btn_sync_stop.toggled.connect(self.sync_stop_toggled.emit)
        sec_grid.addWidget(self.btn_sync_stop, 1, 5)

        # Row 2: ACMP ON, SYNC START, START / STOP (Highlighted Big Button)
        self.btn_acmp = QPushButton("ACMP ON")
        self.btn_acmp.setCheckable(True)
        self.btn_acmp.setChecked(True)
        self.btn_acmp.toggled.connect(self.acmp_toggled.emit)
        sec_grid.addWidget(self.btn_acmp, 2, 0, 1, 2)

        self.btn_sync_start = QPushButton("SYNC START")
        self.btn_sync_start.setCheckable(True)
        self.btn_sync_start.toggled.connect(self.sync_start_toggled.emit)
        sec_grid.addWidget(self.btn_sync_start, 2, 2, 1, 2)

        # BIG START/STOP ILLUMINATED BUTTON
        self.btn_start_stop = QPushButton("▶ START")
        self.btn_start_stop.setCheckable(True)
        self.btn_start_stop.setFixedHeight(34)
        self.btn_start_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_ORANGE};
                color: #101216;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {COLOR_ACCENT_ORANGE_HOVER};
                border-radius: 6px;
            }}
            QPushButton:checked {{
                background-color: {COLOR_ERROR};
                color: white;
                border-color: #FF858B;
            }}
        """)
        self.btn_start_stop.clicked.connect(self.start_stop_requested.emit)
        sec_grid.addWidget(self.btn_start_stop, 2, 4, 1, 2)

        arr_layout.addLayout(sec_grid)

        # 4. Tempo Controls & Tap Tempo
        tempo_row = QHBoxLayout()
        tempo_row.setSpacing(6)

        btn_tap = QPushButton("TAP TEMPO")
        btn_tap.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        btn_tap.setToolTip("Tap rhythmically to set BPM")
        btn_tap.clicked.connect(self.tap_tempo_clicked.emit)
        tempo_row.addWidget(btn_tap)

        btn_tempo_dec = QPushButton("-")
        btn_tempo_dec.setFixedSize(26, 26)
        btn_tempo_dec.clicked.connect(lambda: self._adjust_tempo(-1))
        tempo_row.addWidget(btn_tempo_dec)

        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setRange(40, 240)
        self.tempo_slider.setValue(120)
        self.tempo_slider.valueChanged.connect(self._on_tempo_slider_changed)
        tempo_row.addWidget(self.tempo_slider, 1)

        btn_tempo_inc = QPushButton("+")
        btn_tempo_inc.setFixedSize(26, 26)
        btn_tempo_inc.clicked.connect(lambda: self._adjust_tempo(1))
        tempo_row.addWidget(btn_tempo_inc)

        self.lbl_tempo_val = QLabel("120 BPM")
        self.lbl_tempo_val.setStyleSheet("font-size: 11px; font-weight: bold; color: #E0E6ED; min-width: 52px;")
        tempo_row.addWidget(self.lbl_tempo_val)

        arr_layout.addLayout(tempo_row)

        parent_layout.addWidget(arr_group, 5)

    # =========================================================================
    # SECTION 3: Voice Selection & Performance Deck (Right Side)
    # =========================================================================
    def _build_voice_deck(self, parent_layout: QHBoxLayout):
        """Build Voice Presets, Registration Memory (OTS 1-8), Multi-Pads & Toggles."""
        v_group = QGroupBox("VOICE SELECTION & REGISTRATIONS")
        v_layout = QVBoxLayout(v_group)
        v_layout.setContentsMargins(8, 8, 8, 8)
        v_layout.setSpacing(8)

        # 1. One-Touch Preset Voices Grid (12 Direct Hardware Buttons)
        preset_grid = QGridLayout()
        preset_grid.setSpacing(6)
        self.voice_buttons: List[QPushButton] = []

        for idx, (v_name, v_cat, prog) in enumerate(self.ONE_TOUCH_VOICES):
            row = idx // 4
            col = idx % 4
            btn = QPushButton(v_name)
            btn.setFixedHeight(28)
            btn.setCheckable(True)
            btn.setToolTip(f"{v_cat} • GM #{prog}")
            btn.clicked.connect(lambda ch, p=prog, name=v_name: self._on_quick_voice_clicked(p, name))
            self.voice_buttons.append(btn)
            preset_grid.addWidget(btn, row, col)

        self.voice_buttons[0].setChecked(True)
        v_layout.addLayout(preset_grid)

        # 2. Performance Switches: Layer, Split, Sustain, Touch, Voice Browser
        switch_row = QHBoxLayout()
        switch_row.setSpacing(6)

        self.btn_layer = QPushButton("DUAL / LAYER")
        self.btn_layer.setCheckable(True)
        self.btn_layer.setToolTip("Layer two voices simultaneously (Right 1 + Right 2)")
        self.btn_layer.toggled.connect(self.layer_toggled.emit)
        switch_row.addWidget(self.btn_layer)

        self.btn_split = QPushButton("SPLIT")
        self.btn_split.setCheckable(True)
        self.btn_split.setToolTip("Split keyboard for left hand chord accompaniment")
        self.btn_split.toggled.connect(self.split_toggled.emit)
        switch_row.addWidget(self.btn_split)

        self.btn_sustain = QPushButton("SUSTAIN")
        self.btn_sustain.setCheckable(True)
        self.btn_sustain.setToolTip("Toggle sustain hold pedal (or hold Spacebar)")
        self.btn_sustain.toggled.connect(self.sustain_toggled.emit)
        switch_row.addWidget(self.btn_sustain)

        self.btn_touch = QPushButton("TOUCH: NORM")
        self.btn_touch.setToolTip("Cycle velocity touch curve: Normal / Soft / Hard")
        self.btn_touch.clicked.connect(self._cycle_touch_curve)
        switch_row.addWidget(self.btn_touch)

        btn_browser = QPushButton("🔍 ALL VOICES...")
        btn_browser.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_BLUE};")
        btn_browser.setToolTip("Open full Voice Library with search")
        btn_browser.clicked.connect(self.open_voice_browser_requested.emit)
        switch_row.addWidget(btn_browser)

        v_layout.addLayout(switch_row)

        # 3. Registration Memory (One Touch Settings 1 - 8 + Store)
        reg_row = QHBoxLayout()
        reg_row.setSpacing(4)
        reg_lbl = QLabel("REGISTRATION (OTS):")
        reg_lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLOR_TEXT_MUTED};")
        reg_row.addWidget(reg_lbl)

        self.reg_buttons: List[QPushButton] = []
        for i in range(8):
            btn = QPushButton(str(i + 1))
            btn.setCheckable(True)
            btn.setFixedSize(30, 26)
            btn.setToolTip(f"Recall Registration Memory Slot {i + 1}")
            slot_idx = i
            btn.clicked.connect(lambda checked, idx=slot_idx: self._on_reg_clicked(idx))
            self.reg_buttons.append(btn)
            reg_row.addWidget(btn)

        self.reg_buttons[0].setChecked(True)

        btn_store = QPushButton("STORE")
        btn_store.setFixedSize(48, 26)
        btn_store.setStyleSheet(f"color: {COLOR_ACCENT_ORANGE}; font-weight: bold;")
        btn_store.setToolTip("Store current setup into active registration slot")
        btn_store.clicked.connect(self._on_store_clicked)
        reg_row.addWidget(btn_store)

        v_layout.addLayout(reg_row)

        # 4. Multi-Pads (Performance Drum / FX Hit Pads)
        pad_row = QHBoxLayout()
        pad_row.setSpacing(6)
        pad_lbl = QLabel("MULTI-PADS:")
        pad_lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLOR_TEXT_MUTED};")
        pad_row.addWidget(pad_lbl)

        pad_names = ["1: CLAP", "2: SNARE", "3: CYMBAL", "4: SCRATCH"]
        for idx, p_name in enumerate(pad_names):
            p_btn = QPushButton(p_name)
            p_btn.setFixedHeight(26)
            p_btn.setStyleSheet(f"background-color: #1A212D; color: {COLOR_ACCENT_BLUE}; font-size: 10px; font-weight: bold;")
            pad_idx = idx
            p_btn.clicked.connect(lambda ch, p=pad_idx: self.multipad_triggered.emit(p))
            pad_row.addWidget(p_btn)

        v_layout.addLayout(pad_row)

        parent_layout.addWidget(v_group, 5)

    # =========================================================================
    # SECTION 4: Bottom Mixer Fader Strip
    # =========================================================================
    def _build_fader_strip(self, parent_layout: QVBoxLayout):
        """Hardware slider mixer strip: Master, Style, Keyboard, Split, Reverb."""
        fader_frame = QFrame()
        fader_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_PANEL_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """)
        fader_layout = QHBoxLayout(fader_frame)
        fader_layout.setContentsMargins(8, 2, 8, 2)
        fader_layout.setSpacing(16)

        # 1. Master Volume
        fader_layout.addWidget(self._create_slider_control("MASTER VOL", 0.85, self.master_vol_changed))

        # 2. Accompaniment Volume
        fader_layout.addWidget(self._create_slider_control("STYLE VOL", 0.85, self.acmp_vol_changed))

        # 3. Keyboard Solo Voice Volume
        fader_layout.addWidget(self._create_slider_control("MAIN KEYBOARD", 0.95, self.keyboard_vol_changed))

        # 4. Split / Left Voice Volume
        fader_layout.addWidget(self._create_slider_control("SPLIT / LOWER", 0.80, self.split_vol_changed))

        # 5. Reverb Depth
        fader_layout.addWidget(self._create_slider_control("REVERB", 0.35, self.reverb_changed))

        parent_layout.addWidget(fader_frame)

    def _create_slider_control(self, label_text: str, default_val: float, signal: Signal) -> QWidget:
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLOR_TEXT_SECONDARY};")
        lay.addWidget(lbl)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(default_val * 100))
        slider.valueChanged.connect(lambda v: signal.emit(v / 100.0))
        lay.addWidget(slider, 1)

        val_lbl = QLabel(f"{int(default_val * 100)}%")
        val_lbl.setStyleSheet("font-size: 10px; color: #8F9CAE; min-width: 32px;")
        slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v}%"))
        lay.addWidget(val_lbl)

        return container

    def _create_vsep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #232A36;")
        return sep

    # =========================================================================
    # Event Handlers & Public Update Methods
    # =========================================================================
    def _select_main(self, section: str):
        self.btn_main_a.setChecked(section == SECTION_MAIN_A)
        self.btn_main_b.setChecked(section == SECTION_MAIN_B)
        self.btn_main_c.setChecked(section == SECTION_MAIN_C)
        self.btn_main_d.setChecked(section == SECTION_MAIN_D)
        self.current_section = section
        self.section_requested.emit(section)

    def _on_style_combo_changed(self, idx: int):
        style_name = self.style_combo.currentData()
        if style_name:
            self.style_selected.emit(style_name)

    def select_style_name(self, style_name: str):
        for i in range(self.style_combo.count()):
            if self.style_combo.itemData(i) == style_name:
                self.style_combo.setCurrentIndex(i)
                break
        self.style_selected.emit(style_name)

    def _on_quick_voice_clicked(self, prog: int, name: str):
        for btn in self.voice_buttons:
            btn.setChecked(btn.text() == name)
        self.voice_assigned.emit("right1", prog)

    def _toggle_chord_mode(self):
        if self.btn_chord_mode.text() == "FINGERED":
            self.btn_chord_mode.setText("EASY CHORD")
            self.lbl_chord_mode.setText("MODE: EASY CHORD")
            self.chord_mode_changed.emit("simplified")
        else:
            self.btn_chord_mode.setText("FINGERED")
            self.lbl_chord_mode.setText("MODE: FINGERED")
            self.chord_mode_changed.emit("full")

    def _cycle_touch_curve(self):
        self.current_touch_idx = (self.current_touch_idx + 1) % len(self.touch_modes)
        mode = self.touch_modes[self.current_touch_idx]
        self.btn_touch.setText(f"TOUCH: {mode.upper()[:4]}")
        self.touch_curve_changed.emit(mode)

    def _on_reg_clicked(self, slot_idx: int):
        for i, btn in enumerate(self.reg_buttons):
            btn.setChecked(i == slot_idx)
        self.registration_selected.emit(slot_idx)

    def _on_store_clicked(self):
        # Find active slot
        for i, btn in enumerate(self.reg_buttons):
            if btn.isChecked():
                self.registration_store_requested.emit(i)
                break

    def _transpose_up(self):
        if self.current_transpose < 12:
            self.current_transpose += 1
            self._update_transpose_ui()

    def _transpose_down(self):
        if self.current_transpose > -12:
            self.current_transpose -= 1
            self._update_transpose_ui()

    def _transpose_reset(self):
        self.current_transpose = 0
        self._update_transpose_ui()

    def _update_transpose_ui(self):
        sign = "+" if self.current_transpose > 0 else ""
        self.lbl_transpose.setText(f"TRANSPOSE: {sign}{self.current_transpose}")
        self.transpose_changed.emit(self.current_transpose)

    def _octave_up(self):
        if self.current_octave < 3:
            self.current_octave += 1
            self._update_octave_ui()

    def _octave_down(self):
        if self.current_octave > -3:
            self.current_octave -= 1
            self._update_octave_ui()

    def _octave_reset(self):
        self.current_octave = 0
        self._update_octave_ui()

    def _update_octave_ui(self):
        sign = "+" if self.current_octave > 0 else ""
        self.lbl_octave.setText(f"OCTAVE: {sign}{self.current_octave}")
        self.octave_changed.emit(self.current_octave)

    def _adjust_tempo(self, delta: int):
        new_val = max(40, min(240, self.tempo_slider.value() + delta))
        self.tempo_slider.setValue(new_val)

    def _on_tempo_slider_changed(self, val: int):
        self.lbl_tempo_val.setText(f"{val} BPM")
        self.tempo_changed.emit(val)

    def update_voices_display(self, r1_name: str, r2_name: str, left_name: str, layer_on: bool, split_on: bool, split_pt_name: str):
        self.lbl_r1_mon.setText(f"R1: {r1_name}")
        self.lbl_r2_mon.setText(f"R2: {r2_name}" if layer_on else f"R2: {r2_name} (Off)")
        self.lbl_r2_mon.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLOR_ACCENT_BLUE if layer_on else '#707C8D'};")

        self.lbl_left_mon.setText(f"Left: {left_name} [{split_pt_name}]" if split_on else f"Left: {left_name} (Off)")
        self.lbl_left_mon.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLOR_ACCENT_BLUE if split_on else '#707C8D'};")

        self.btn_layer.setChecked(layer_on)
        self.btn_split.setChecked(split_on)

    def update_style_display(self, style_name: str, bpm: int, time_sig: str):
        self.lbl_style_title.setText(style_name)
        self.lbl_style_info.setText(f"{bpm} BPM • {time_sig}")
        self.tempo_slider.blockSignals(True)
        self.tempo_slider.setValue(bpm)
        self.lbl_tempo_val.setText(f"{bpm} BPM")
        self.tempo_slider.blockSignals(False)

        # Sync combo without re-firing
        for i in range(self.style_combo.count()):
            if self.style_combo.itemData(i) == style_name:
                self.style_combo.blockSignals(True)
                self.style_combo.setCurrentIndex(i)
                self.style_combo.blockSignals(False)
                break

    def update_beat(self, beat: int, bar: int, is_downbeat: bool = False):
        color = COLOR_ACCENT_ORANGE if is_downbeat else COLOR_SUCCESS
        self.lbl_bar_beat.setText(f"BAR: {bar} | BEAT: {beat}")
        self.lbl_bar_beat.setStyleSheet(f"background-color: #151922; color: {color}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        self.beat_indicator.set_beat(beat, numerator=4, is_running=True)

    def set_start_stop_state(self, is_running: bool):
        self.btn_start_stop.setChecked(is_running)
        if is_running:
            self.btn_start_stop.setText("■ STOP")
            self.btn_start_stop.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ERROR};
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #FF858B;
                    border-radius: 6px;
                }}
            """)
        else:
            self.btn_start_stop.setText("▶ START")
            self.btn_start_stop.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT_ORANGE};
                    color: #101216;
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid {COLOR_ACCENT_ORANGE_HOVER};
                    border-radius: 6px;
                }}
            """)
            self.beat_indicator.stop()
