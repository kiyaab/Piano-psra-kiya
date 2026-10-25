"""
KIYA Piano Studio Pro - Professional Arranger & Style Studio Page
High-end arranger workstation screen with hero style showcase, genre filters,
authentic tactile section matrix (Mains, Fills, Intros, Endings), digital tempo console,
chord recognition modes, and 5-channel precision balance mixer.
"""

import time
from typing import List, Optional, Dict
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QSlider,
    QComboBox, QScrollArea, QSizePolicy
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QFont
)

from app.constants import (
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_PANEL_SECONDARY,
    COLOR_PANEL_ELEVATED,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
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
from arranger.style_loader import StyleDefinition
from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class DigitalDisplayBox(QFrame):
    """Sleek glowing digital LCD display readout."""
    def __init__(self, title: str, value: str, accent: str = "#4DA8DA", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: #0B0E14; border: 1px solid #1E2633; border-radius: 6px; padding: 4px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(HardwareFonts.micro_bold())
        self.lbl_title.setStyleSheet("color: #7B8A9E; letter-spacing: 0.5px;")
        layout.addWidget(self.lbl_title, 0, Qt.AlignCenter)

        self.lbl_value = QLabel(value)
        font = QFont("Consolas", 13, QFont.Bold)
        self.lbl_value.setFont(font)
        self.lbl_value.setStyleSheet(f"color: {accent}; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(self.lbl_value, 0, Qt.AlignCenter)

    def set_value(self, text: str):
        self.lbl_value.setText(text)


class ChannelFaderStrip(QWidget):
    """
    Professional hardware mixing console fader strip:
    Icon, title, graduated dB scale ticks, vertical fader slider, %, and Mute button.
    """
    volumeChanged = Signal(float)
    muteToggled = Signal(bool)

    def __init__(self, title: str, icon: str, default_val: float = 0.85, accent: str = "#4DA8DA", parent=None):
        super().__init__(parent)
        self.accent = accent
        self._is_muted = False

        self.setStyleSheet("""
            QSlider::groove:vertical {
                background: #0D1016;
                width: 6px;
                border: 1px solid #1E2530;
                border-radius: 3px;
            }
            QSlider::sub-page:vertical {
                background: #181D26;
                border-radius: 3px;
            }
            QSlider::add-page:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4DA8DA, stop:1 #1E3A5F);
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #606875, stop:0.5 #383D48, stop:1 #22252C);
                border: 1px solid #757F90;
                height: 22px;
                margin-left: -9px;
                margin-right: -9px;
                border-radius: 3px;
            }
            QSlider::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #757F90, stop:0.5 #4D5463, stop:1 #2D313A);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Track Icon & Header
        header = QLabel(f"{icon}\n{title.upper()}")
        header.setFont(HardwareFonts.micro_bold())
        header.setStyleSheet("color: #BAC7D5; text-align: center;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Fader with decibel markings
        fader_box = QHBoxLayout()
        fader_box.setSpacing(4)
        fader_box.setAlignment(Qt.AlignCenter)

        # dB scale
        db_labels = QVBoxLayout()
        db_labels.setSpacing(0)
        db_labels.setContentsMargins(0, 0, 0, 0)
        for mark in ["+6", " 0", "-6", "-12", "-24", "-∞"]:
            lbl_db = QLabel(mark)
            lbl_db.setFont(HardwareFonts.micro_regular())
            lbl_db.setStyleSheet("color: #4C5564; font-size: 8px;")
            db_labels.addWidget(lbl_db)
        fader_box.addLayout(db_labels)

        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(0, 127)
        self.slider.setValue(int(default_val * 127))
        self.slider.setMinimumHeight(120)
        self.slider.valueChanged.connect(self._on_slider_changed)
        fader_box.addWidget(self.slider)

        layout.addLayout(fader_box)

        # Percentage label
        self.lbl_pct = QLabel(f"{int(default_val * 100)}%")
        self.lbl_pct.setFont(HardwareFonts.micro_bold())
        self.lbl_pct.setStyleSheet(f"color: {self.accent}; background: #0A0D12; border: 1px solid #1C2330; border-radius: 3px; padding: 2px;")
        self.lbl_pct.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_pct)

        # Mute button
        self.btn_mute = PhysicalButton("MUTE", width=46, height=22, indicator="red")
        self.btn_mute.clicked.connect(self._toggle_mute)
        layout.addWidget(self.btn_mute, 0, Qt.AlignCenter)

    def _on_slider_changed(self, val: int):
        pct = int((val / 127.0) * 100)
        self.lbl_pct.setText(f"{pct}%")
        if not self._is_muted:
            self.volumeChanged.emit(val / 127.0)

    def _toggle_mute(self):
        self._is_muted = not self._is_muted
        self.btn_mute.set_led(self._is_muted)
        self.muteToggled.emit(self._is_muted)
        if self._is_muted:
            self.volumeChanged.emit(0.0)
            self.lbl_pct.setStyleSheet("color: #E63946; background: #0A0D12; border: 1px solid #4D1A1E; border-radius: 3px; padding: 2px;")
        else:
            self.volumeChanged.emit(self.slider.value() / 127.0)
            self.lbl_pct.setStyleSheet(f"color: {self.accent}; background: #0A0D12; border: 1px solid #1C2330; border-radius: 3px; padding: 2px;")


class ArrangerPage(QWidget):
    """
    KIYA Piano Studio Pro - Dedicated Arranger & Style Workstation Screen.
    Provides complete arranger configuration, rich style browsing, pattern section matrix,
    live chord recognition tuning, tempo console, and multi-track balance mixer.
    """

    style_selected = Signal(str)            # style_name
    section_selected = Signal(str)          # section_name
    tempo_changed = Signal(int)             # bpm
    chord_mode_changed = Signal(str)        # "full" or "simplified"
    track_volume_changed = Signal(str, float) # track_key, volume (0.0 to 1.0)

    GENRE_ICONS = {
        "pop": "🎸", "rock": "⚡", "ballad": "🎹", "dance": "🎛",
        "funk": "🕺", "disco": "✨", "latin": "🌴", "bossa": "🏖",
        "jazz": "🎷", "swing": "🎺", "r&b": "🎤", "soul": "🎶",
        "country": "🪕", "folk": "🎻", "world": "🪘", "ethiopian": "🌍",
        "reggae": "☀️", "classical": "🎼", "waltz": "💃",
    }

    def __init__(self, available_styles: List[StyleDefinition], parent=None):
        super().__init__(parent)
        self.available_styles = available_styles
        self.setObjectName("ArrangerPage")
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_TEXT_PRIMARY};")

        self.current_style: Optional[StyleDefinition] = available_styles[0] if available_styles else None
        self._active_section = SECTION_MAIN_A
        self._tap_times = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 12, 16, 14)
        root_layout.setSpacing(12)

        # =====================================================================
        # 1. TOP HERO SHOWCASE CARD (Active Style Banner & Metadata)
        # =====================================================================
        self._build_hero_header(root_layout)

        # =====================================================================
        # 2. MAIN WORKSPACE (Split Left: Style Browser | Split Right: Matrix & Mix)
        # =====================================================================
        body_layout = QHBoxLayout()
        body_layout.setSpacing(14)

        # Left Column: Categorized Style Library
        self._build_style_browser_panel(body_layout)

        # Right Column: Section Matrix, Tempo/Chord Studio, Track Mixer
        self._build_controls_mixer_panel(body_layout)

        root_layout.addLayout(body_layout, 1)

        # Select initial style
        if self.available_styles:
            self._select_style_by_index(0)

    # =========================================================================
    # HERO HEADER CARD
    # =========================================================================
    def _build_hero_header(self, parent_layout: QVBoxLayout):
        hero = QFrame()
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #141822, stop:0.4 #1A202E, stop:1 #11141B);
                border: 1px solid #2B3547;
                border-radius: 8px;
            }
        """)
        h_layout = QHBoxLayout(hero)
        h_layout.setContentsMargins(16, 10, 16, 10)
        h_layout.setSpacing(16)

        # Style Name & Badge
        info_box = QVBoxLayout()
        info_box.setSpacing(2)

        sub_head = QHBoxLayout()
        sub_head.setSpacing(8)

        lbl_pulse = QLabel("● ACTIVE STYLE")
        lbl_pulse.setFont(HardwareFonts.micro_bold())
        lbl_pulse.setStyleSheet("color: #10B981; font-weight: bold; letter-spacing: 1px;")
        sub_head.addWidget(lbl_pulse)

        self.badge_cat = QLabel("POP & ROCK")
        self.badge_cat.setFont(HardwareFonts.micro_bold())
        self.badge_cat.setStyleSheet("background: #2563EB; color: #FFFFFF; padding: 2px 8px; border-radius: 4px; font-weight: bold;")
        sub_head.addWidget(self.badge_cat)

        self.badge_ts = QLabel("4/4")
        self.badge_ts.setFont(HardwareFonts.micro_bold())
        self.badge_ts.setStyleSheet("background: #1E293B; color: #94A3B8; border: 1px solid #334155; padding: 2px 6px; border-radius: 4px;")
        sub_head.addWidget(self.badge_ts)

        sub_head.addStretch()
        info_box.addLayout(sub_head)

        self.lbl_hero_title = QLabel("8-Beat Modern Pop")
        font_hero = QFont("Outfit", 18, QFont.Bold) if QFont("Outfit").exactMatch() else QFont("Segoe UI", 18, QFont.Bold)
        self.lbl_hero_title.setFont(font_hero)
        self.lbl_hero_title.setStyleSheet("color: #FFFFFF; font-weight: bold; letter-spacing: 0.5px;")
        info_box.addWidget(self.lbl_hero_title)

        h_layout.addLayout(info_box, 3)

        # Quick Digital Indicators (Tempo, Section, Chord)
        self.disp_tempo = DigitalDisplayBox("TEMPO", "120 BPM", accent="#FFB347")
        h_layout.addWidget(self.disp_tempo)

        self.disp_section = DigitalDisplayBox("CURRENT SECTION", "MAIN A", accent="#10B981")
        h_layout.addWidget(self.disp_section)

        self.disp_chord_mode = DigitalDisplayBox("CHORD ENGINE", "CHROMATIC", accent="#38BDF8")
        h_layout.addWidget(self.disp_chord_mode)

        parent_layout.addWidget(hero)

    # =========================================================================
    # LEFT COLUMN: STYLE BROWSER
    # =========================================================================
    def _build_style_browser_panel(self, parent_layout: QHBoxLayout):
        browser_frame = QFrame()
        browser_frame.setStyleSheet("""
            QFrame {
                background: #151821;
                border: 1px solid #232A38;
                border-radius: 8px;
            }
        """)
        bf_layout = QVBoxLayout(browser_frame)
        bf_layout.setContentsMargins(12, 10, 12, 10)
        bf_layout.setSpacing(8)

        # Header Title
        title_box = QHBoxLayout()
        lbl_b_title = QLabel("STYLE LIBRARY")
        lbl_b_title.setFont(HardwareFonts.sub_bold())
        lbl_b_title.setStyleSheet("color: #E2E8F0; font-weight: bold;")
        title_box.addWidget(lbl_b_title)

        lbl_count = QLabel(f"{len(self.available_styles)} Styles")
        lbl_count.setFont(HardwareFonts.micro_bold())
        lbl_count.setStyleSheet("color: #64748B;")
        title_box.addWidget(lbl_count, 0, Qt.AlignRight)
        bf_layout.addLayout(title_box)

        # Category Filter Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(4)
        chips = ["ALL", "POP", "DANCE", "LATIN", "JAZZ", "WORLD"]
        self.chip_buttons = {}
        for c in chips:
            btn = QPushButton(c)
            btn.setFont(HardwareFonts.micro_bold())
            btn.setCheckable(True)
            if c == "ALL":
                btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: #1E2430;
                    color: #94A3B8;
                    border: 1px solid #2D3748;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #283244;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background: #2563EB;
                    color: #FFFFFF;
                    font-weight: bold;
                    border: 1px solid #3B82F6;
                }
            """)
            btn.clicked.connect(lambda checked=False, chip=c: self._filter_by_chip(chip))
            self.chip_buttons[c] = btn
            chips_layout.addWidget(btn)
        bf_layout.addLayout(chips_layout)

        # Styled Style List
        self.style_list = QListWidget()
        self.style_list.setStyleSheet("""
            QListWidget {
                background: #0E1118;
                border: 1px solid #1E2533;
                border-radius: 6px;
                padding: 4px;
                color: #E2E8F0;
                outline: none;
            }
            QListWidget::item {
                background: #141720;
                border: 1px solid #1F2736;
                border-radius: 5px;
                padding: 8px 10px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background: #1C2332;
                border: 1px solid #3B82F6;
                color: #FFFFFF;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E3A8A, stop:1 #1E293B);
                border: 1px solid #60A5FA;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        self._populate_style_list(self.available_styles)
        self.style_list.currentRowChanged.connect(self._on_style_row_changed)
        bf_layout.addWidget(self.style_list, 1)

        parent_layout.addWidget(browser_frame, 3)

    def _get_icon_for_style(self, name: str, cat: str) -> str:
        name_l = name.lower()
        cat_l = cat.lower()
        for k, icon in self.GENRE_ICONS.items():
            if k in name_l or k in cat_l:
                return icon
        return "🥁"

    def _populate_style_list(self, styles: List[StyleDefinition]):
        self.style_list.clear()
        for s in styles:
            icon = self._get_icon_for_style(s.name, s.category)
            item_text = f"{icon}  {s.name}  [{s.tempo} BPM]"
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(220, 36))
            item.setData(Qt.UserRole, s.name)
            self.style_list.addItem(item)

    def _filter_by_chip(self, chip: str):
        for c_name, btn in self.chip_buttons.items():
            btn.setChecked(c_name == chip)

        if chip == "ALL":
            filtered = self.available_styles
        else:
            chip_l = chip.lower()
            filtered = [
                s for s in self.available_styles
                if chip_l in s.category.lower() or chip_l in s.name.lower()
            ]
        self._populate_style_list(filtered)
        if self.style_list.count() > 0:
            self.style_list.setCurrentRow(0)

    # =========================================================================
    # RIGHT COLUMN: SECTION MATRIX, TEMPO & MIXER
    # =========================================================================
    def _build_controls_mixer_panel(self, parent_layout: QHBoxLayout):
        right_container = QVBoxLayout()
        right_container.setSpacing(12)

        # --- A. PRO ARRANGER SECTION MATRIX ---
        matrix_frame = QFrame()
        matrix_frame.setStyleSheet("""
            QFrame {
                background: #151821;
                border: 1px solid #232A38;
                border-radius: 8px;
            }
        """)
        mf_layout = QVBoxLayout(matrix_frame)
        mf_layout.setContentsMargins(12, 10, 12, 10)
        mf_layout.setSpacing(8)

        m_title = QLabel("ARRANGER SECTION TRANSITION MATRIX")
        m_title.setFont(HardwareFonts.sub_bold())
        m_title.setStyleSheet("color: #E2E8F0; font-weight: bold;")
        mf_layout.addWidget(m_title)

        matrix_grid = QGridLayout()
        matrix_grid.setSpacing(6)

        self.section_buttons: Dict[str, PhysicalButton] = {}

        # Row 0: Intros, Break, Endings
        row0_defs = [
            ("INTRO I", SECTION_INTRO, "red", 0, 0),
            ("INTRO II", SECTION_INTRO, "red", 0, 1),
            ("BREAK", SECTION_BREAK, "amber", 0, 2),
            ("ENDING I", SECTION_ENDING, "red", 0, 3),
            ("ENDING II", SECTION_ENDING, "red", 0, 4),
        ]
        for label, sec_id, led, r, c in row0_defs:
            btn = PhysicalButton(label, width=88, height=32, indicator=led)
            btn.clicked.connect(lambda s=sec_id, l=label: self._on_section_clicked(s, l))
            self.section_buttons[label] = btn
            matrix_grid.addWidget(btn, r, c)

        # Row 1: Main Variations A, B, C, D
        row1_defs = [
            ("MAIN A", SECTION_MAIN_A, "green", 1, 0),
            ("MAIN B", SECTION_MAIN_B, "green", 1, 1),
            ("MAIN C", SECTION_MAIN_C, "green", 1, 2),
            ("MAIN D", SECTION_MAIN_D, "green", 1, 3),
        ]
        for label, sec_id, led, r, c in row1_defs:
            btn = PhysicalButton(label, width=88, height=32, indicator=led)
            if label == "MAIN A":
                btn.set_led(True)
            btn.clicked.connect(lambda s=sec_id, l=label: self._on_section_clicked(s, l))
            self.section_buttons[label] = btn
            matrix_grid.addWidget(btn, r, c)

        # Row 2: Fills AA, BB, CC, DD
        row2_defs = [
            ("FILL AA", SECTION_FILL_AA, "amber", 2, 0),
            ("FILL BB", SECTION_FILL_BB, "amber", 2, 1),
            ("FILL CC", SECTION_FILL_CC, "amber", 2, 2),
            ("FILL DD", SECTION_FILL_DD, "amber", 2, 3),
        ]
        for label, sec_id, led, r, c in row2_defs:
            btn = PhysicalButton(label, width=88, height=30, indicator=led)
            btn.clicked.connect(lambda s=sec_id, l=label: self._on_section_clicked(s, l))
            self.section_buttons[label] = btn
            matrix_grid.addWidget(btn, r, c)

        mf_layout.addLayout(matrix_grid)
        right_container.addWidget(matrix_frame)

        # --- B. DIGITAL TEMPO CONSOLE & CHORD RECOGNITION STUDIO ---
        tune_frame = QFrame()
        tune_frame.setStyleSheet("""
            QFrame {
                background: #151821;
                border: 1px solid #232A38;
                border-radius: 8px;
            }
        """)
        tf_layout = QHBoxLayout(tune_frame)
        tf_layout.setContentsMargins(12, 10, 12, 10)
        tf_layout.setSpacing(14)

        # Chord Recognition Mode Box
        chord_box = QVBoxLayout()
        chord_box.setSpacing(4)
        c_title = QLabel("CHORD DETECTION MODE")
        c_title.setFont(HardwareFonts.micro_bold())
        c_title.setStyleSheet("color: #7B8A9E;")
        chord_box.addWidget(c_title)

        self.combo_chord_mode = QComboBox()
        self.combo_chord_mode.setStyleSheet("""
            QComboBox {
                background: #0E1218;
                color: #FFFFFF;
                border: 1px solid #2B3547;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                min-width: 220px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: #151821;
                color: #FFFFFF;
                selection-background-color: #2563EB;
                border: 1px solid #2B3547;
            }
        """)
        self.combo_chord_mode.addItem("🎹 Full-Finger Chromatic (Advanced)", "full")
        self.combo_chord_mode.addItem("✨ Single-Finger / Easy Chord (Yamaha)", "simplified")
        self.combo_chord_mode.currentIndexChanged.connect(self._on_chord_mode_changed)
        chord_box.addWidget(self.combo_chord_mode)
        tf_layout.addLayout(chord_box, 1)

        # Master Tempo Console
        tempo_box = QVBoxLayout()
        tempo_box.setSpacing(4)
        t_title = QLabel("GROOVE TEMPO & TIMING")
        t_title.setFont(HardwareFonts.micro_bold())
        t_title.setStyleSheet("color: #7B8A9E;")
        tempo_box.addWidget(t_title)

        t_row = QHBoxLayout()
        t_row.setSpacing(6)

        btn_tempo_minus = PhysicalButton("−", width=30, height=26)
        btn_tempo_minus.clicked.connect(lambda: self._adjust_tempo_delta(-1))
        t_row.addWidget(btn_tempo_minus)

        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setRange(40, 240)
        self.tempo_slider.setValue(120)
        self.tempo_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #0D1016;
                height: 6px;
                border: 1px solid #1E2530;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #38BDF8);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #606875, stop:0.5 #383D48, stop:1 #22252C);
                border: 1px solid #757F90;
                width: 20px;
                margin-top: -8px;
                margin-bottom: -8px;
                border-radius: 3px;
            }
        """)
        self.tempo_slider.valueChanged.connect(self._on_tempo_slider_changed)
        t_row.addWidget(self.tempo_slider, 1)

        btn_tempo_plus = PhysicalButton("+", width=30, height=26)
        btn_tempo_plus.clicked.connect(lambda: self._adjust_tempo_delta(1))
        t_row.addWidget(btn_tempo_plus)

        self.btn_tap = PhysicalButton("TAP", width=42, height=26, indicator="amber")
        self.btn_tap.clicked.connect(self._on_tap_tempo)
        t_row.addWidget(self.btn_tap)

        self.tempo_lbl = QLabel("120 BPM")
        self.tempo_lbl.setFont(HardwareFonts.sub_bold())
        self.tempo_lbl.setStyleSheet("color: #FFB347; font-weight: bold; background: #0A0D12; border: 1px solid #232A38; border-radius: 3px; padding: 3px 6px;")
        t_row.addWidget(self.tempo_lbl)

        tempo_box.addLayout(t_row)
        tf_layout.addLayout(tempo_box, 2)

        right_container.addWidget(tune_frame)

        # --- C. 5-CHANNEL ARRANGER BALANCE MIXER ---
        mix_frame = QFrame()
        mix_frame.setStyleSheet("""
            QFrame {
                background: #151821;
                border: 1px solid #232A38;
                border-radius: 8px;
            }
        """)
        mxf_layout = QVBoxLayout(mix_frame)
        mxf_layout.setContentsMargins(12, 10, 12, 10)
        mxf_layout.setSpacing(6)

        mxf_head = QHBoxLayout()
        mx_title = QLabel("STYLE TRACK BALANCE MIXER")
        mx_title.setFont(HardwareFonts.sub_bold())
        mx_title.setStyleSheet("color: #E2E8F0; font-weight: bold;")
        mxf_head.addWidget(mx_title)
        mxf_head.addStretch()
        mxf_layout.addLayout(mxf_head)

        faders_row = QHBoxLayout()
        faders_row.setSpacing(10)

        # 5 Channels: Drums, Bass, Chords 1, Chords 2, Phrase
        faders_row.addWidget(ChannelFaderStrip("Drums", "🥁", default_val=0.85, accent="#10B981", parent=self))
        faders_row.addWidget(ChannelFaderStrip("Bass", "🎸", default_val=0.85, accent="#3B82F6", parent=self))
        faders_row.addWidget(ChannelFaderStrip("Chord 1", "🎹", default_val=0.75, accent="#F59E0B", parent=self))
        faders_row.addWidget(ChannelFaderStrip("Chord 2", "🎻", default_val=0.70, accent="#EC4899", parent=self))
        faders_row.addWidget(ChannelFaderStrip("Phrase", "✨", default_val=0.70, accent="#8B5CF6", parent=self))

        # Wire faders to track_volume_changed
        for i, key in enumerate(["drums", "bass", "chords", "chords2", "phrase"]):
            fader: ChannelFaderStrip = faders_row.itemAt(i).widget()
            fader.volumeChanged.connect(lambda v, k=key: self.track_volume_changed.emit(k, v))

        mxf_layout.addLayout(faders_row)
        right_container.addWidget(mix_frame)

        parent_layout.addLayout(right_container, 5)

    # =========================================================================
    # EVENT HANDLERS & NOTIFICATIONS
    # =========================================================================
    def _select_style_by_index(self, idx: int):
        if 0 <= idx < len(self.available_styles):
            style = self.available_styles[idx]
            self.current_style = style
            self.lbl_hero_title.setText(style.name)
            self.badge_cat.setText(style.category.upper())
            self.badge_ts.setText(f"{style.time_sig_num}/{style.time_sig_den}")
            self.disp_tempo.set_value(f"{style.tempo} BPM")
            self.tempo_slider.setValue(style.tempo)
            self.tempo_lbl.setText(f"{style.tempo} BPM")
            self.style_selected.emit(style.name)

    def _on_style_row_changed(self, row: int):
        if row >= 0:
            item = self.style_list.item(row)
            if item:
                name = item.data(Qt.UserRole)
                for s in self.available_styles:
                    if s.name == name:
                        self.current_style = s
                        self.lbl_hero_title.setText(s.name)
                        self.badge_cat.setText(s.category.upper())
                        self.badge_ts.setText(f"{s.time_sig_num}/{s.time_sig_den}")
                        self.disp_tempo.set_value(f"{s.tempo} BPM")
                        self.tempo_slider.setValue(s.tempo)
                        self.tempo_lbl.setText(f"{s.tempo} BPM")
                        self.style_selected.emit(s.name)
                        break

    def _on_section_clicked(self, section_name: str, label: str):
        self._active_section = section_name
        self.disp_section.set_value(label)
        # Light up corresponding LED
        for l, btn in self.section_buttons.items():
            btn.set_led(l == label)
        self.section_selected.emit(section_name)

    def _on_tempo_slider_changed(self, val: int):
        self.tempo_lbl.setText(f"{val} BPM")
        self.disp_tempo.set_value(f"{val} BPM")
        self.tempo_changed.emit(val)

    def _adjust_tempo_delta(self, delta: int):
        new_val = max(40, min(240, self.tempo_slider.value() + delta))
        self.tempo_slider.setValue(new_val)

    def _on_tap_tempo(self):
        now = time.time()
        self._tap_times.append(now)
        if len(self._tap_times) > 4:
            self._tap_times.pop(0)
        if len(self._tap_times) >= 2:
            intervals = [self._tap_times[i] - self._tap_times[i - 1] for i in range(1, len(self._tap_times))]
            avg = sum(intervals) / len(intervals)
            if 0.2 < avg < 2.0:
                bpm = int(round(60.0 / avg))
                self.tempo_slider.setValue(bpm)
        self.btn_tap.flash(120)

    def _on_chord_mode_changed(self, idx: int):
        mode = self.combo_chord_mode.currentData()
        self.disp_chord_mode.set_value("CHROMATIC" if mode == "full" else "EASY CHORD")
        self.chord_mode_changed.emit(mode)
