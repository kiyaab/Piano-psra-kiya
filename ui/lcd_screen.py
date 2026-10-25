"""
KIYA Piano Studio Pro - Central Recessed Color LCD Display
Styled as the Yamaha PSR-S975 central 7-inch color display.
Features authentic workstation graphics, dark gray-blue palette, softkeys [A]-[E] and [F]-[J],
page tabs, and 10 fully functional interactive screen pages.
"""

from pathlib import Path
from typing import Optional, List, Dict
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QStackedWidget, QFrame, QPushButton, QSlider, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QScrollArea
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QFont,
    QPaintEvent
)

from ui.physical_button import PhysicalButton
from ui.hardware_theme import HardwareColors, HardwareFonts


class LCDScreenBezel(QFrame):
    """
    Physical recessed bezel surrounding the LCD panel.
    Custom painted with deep inset bevel, screws, and glossy edge.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LCDScreenBezel")
        self.setAttribute(Qt.WA_StyledBackground, True)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Outer bezel recess — deep obsidian inset frame
        outer_rect = QRectF(0, 0, w, h)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#040508"))
        grad.setColorAt(0.06, QColor("#0E1018"))
        grad.setColorAt(0.94, QColor("#0E1018"))
        grad.setColorAt(1.0, QColor("#050608"))

        painter.setPen(QPen(QColor("#020308"), 2.5))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(outer_rect, 8.0, 8.0)

        # Inner glowing top rim — blue-tinted chrome
        from PySide6.QtGui import QLinearGradient as LG
        rim_g = LG(0, 0, w, 0)
        rim_g.setColorAt(0.0, QColor(0, 0, 0, 0))
        rim_g.setColorAt(0.2, QColor(40, 80, 160, 60))
        rim_g.setColorAt(0.5, QColor(60, 110, 200, 90))
        rim_g.setColorAt(0.8, QColor(40, 80, 160, 60))
        rim_g.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(QPen(QBrush(rim_g), 1.0))
        painter.drawLine(4, 2, w - 5, 2)

        # Subtle white highlight
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        painter.drawLine(4, 3, w - 5, 3)

        # Bottom deep shadow
        painter.setPen(QPen(QColor(0, 0, 0, 200), 1.5))
        painter.drawLine(4, h - 3, w - 5, h - 3)


# =========================================================================
# 10 DEDICATED LCD SCREEN PAGES
# =========================================================================

class AudioSpectrumWidget(QWidget):
    """
    Realistic 12-band real-time audio visualizer with peak hold dots.
    Bounces dynamically when keyboard keys are touched or accompaniment plays.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.num_bars = 14
        self.values = [0.12] * self.num_bars
        self.peak_values = [0.12] * self.num_bars

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._decay)
        self.timer.start(45)

    def bump(self, intensity: float = 0.85):
        import random
        for i in range(self.num_bars):
            # Center weighted frequency distribution
            weight = 1.0 - abs(i - 6) * 0.08
            v = min(1.0, max(0.12, intensity * weight * random.uniform(0.65, 1.05)))
            self.values[i] = max(self.values[i], v)
            if self.values[i] > self.peak_values[i]:
                self.peak_values[i] = self.values[i]
        self.update()

    def _decay(self):
        for i in range(self.num_bars):
            self.values[i] = max(0.10, self.values[i] * 0.86)
            self.peak_values[i] = max(0.10, self.peak_values[i] - 0.035)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w = float(self.width())
        h = float(self.height())
        bar_w = (w - (self.num_bars - 1) * 2.5) / float(self.num_bars)

        # Tinted background tray with gradient
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor("#081018"))
        bg.setColorAt(1.0, QColor("#0A1420"))
        painter.fillRect(QRectF(0, 0, w, h), QBrush(bg))

        for i in range(self.num_bars):
            bx = i * (bar_w + 2.5)
            val = self.values[i]
            bar_h = val * (h - 4.0)

            # Vivid neon gradient bars
            grad = QLinearGradient(0, h - 2.0, 0, 2.0)
            grad.setColorAt(0.0, QColor("#00CC66"))    # vivid green base
            grad.setColorAt(0.55, QColor("#00EEBB"))   # teal-green mid
            grad.setColorAt(0.80, QColor("#FFB700"))   # amber high
            grad.setColorAt(1.0, QColor("#FF4060"))    # red peak

            # Bar body
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(bx, h - 2.0 - bar_h, bar_w, bar_h), 1.5, 1.5)

            # Subtle bar glow overlay
            glow_g = QLinearGradient(bx, 0, bx + bar_w, 0)
            glow_g.setColorAt(0.0, QColor(255, 255, 255, 30))
            glow_g.setColorAt(0.5, QColor(255, 255, 255, 10))
            glow_g.setColorAt(1.0, QColor(255, 255, 255, 20))
            painter.setBrush(QBrush(glow_g))
            painter.drawRoundedRect(QRectF(bx, h - 2.0 - bar_h, bar_w * 0.4, bar_h), 1.5, 1.5)

            # Peak hold dot (bright red)
            pk = self.peak_values[i]
            pk_y = h - 2.0 - (pk * (h - 4.0))
            painter.setPen(QPen(QColor("#FF4060"), 1.5))
            painter.drawLine(int(bx), int(pk_y), int(bx + bar_w), int(pk_y))


class MainPerformancePage(QWidget):
    """Page 1: PSR-S975 Main Performance Display - Clean 2-Column Workstation Layout."""
    voiceClicked = Signal(str)  # "R1", "R2", "LEFT"
    styleClicked = Signal()
    loadStyleClicked = Signal()
    loadRegistClicked = Signal()
    tempoClicked = Signal()
    registrationClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # -------------------------------------------------------------
        # TOP STATUS HEADER
        # -------------------------------------------------------------
        status_bar = QHBoxLayout()
        status_bar.setSpacing(6)

        self.lbl_title = QLabel("PSR-S975 ARRANGER")
        self.lbl_title.setFont(HardwareFonts.micro_bold())
        self.lbl_title.setStyleSheet("color: #39FF8A; font-weight: bold; letter-spacing: 1px;")
        status_bar.addWidget(self.lbl_title)

        # HUD Toast notification badge (temporary messages)
        self.lbl_hud_toast = QLabel("")
        self.lbl_hud_toast.setFont(HardwareFonts.micro_bold())
        self.lbl_hud_toast.setStyleSheet("color: #39FF8A; padding: 1px 6px; border-radius: 2px;")
        status_bar.addWidget(self.lbl_hud_toast)

        status_bar.addStretch()

        self.lbl_chord = QLabel("CHORD: C Maj")
        self.lbl_chord.setFont(HardwareFonts.micro_bold())
        self.lbl_chord.setStyleSheet("color: #FFB726; background: #160D00; padding: 2px 10px; border-radius: 4px; border: 1px solid #3D2A00; font-weight: bold; letter-spacing: 0.5px;")
        status_bar.addWidget(self.lbl_chord)

        self.lbl_tempo = QLabel("TEMPO: 120 [4/4]")
        self.lbl_tempo.setFont(HardwareFonts.micro_bold())
        self.lbl_tempo.setStyleSheet("color: #E8F4FF; background: #081020; padding: 2px 10px; border-radius: 4px; border: 1px solid #1A3060; font-weight: bold;")
        status_bar.addWidget(self.lbl_tempo)

        self.lbl_measure = QLabel("BAR: 001 : 1")
        self.lbl_measure.setFont(HardwareFonts.micro_bold())
        self.lbl_measure.setStyleSheet("color: #38B4FF; background: #080F20; padding: 2px 10px; border-radius: 4px; border: 1px solid #153060; font-weight: bold;")
        status_bar.addWidget(self.lbl_measure)

        self.lbl_transpose = QLabel("TRANS: +0")
        self.lbl_transpose.setFont(HardwareFonts.micro_bold())
        self.lbl_transpose.setStyleSheet("color: #8AABCC; background: #080E1A; padding: 2px 8px; border-radius: 4px; border: 1px solid #152040;")
        status_bar.addWidget(self.lbl_transpose)

        layout.addLayout(status_bar)

        # -------------------------------------------------------------
        # MAIN WORKSPACE: 2 SPACIOUS COLUMNS (Left: Arranger, Right: Voices)
        # -------------------------------------------------------------
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)

        # === COLUMN 1: ARRANGER STYLE & LIVE CHORD TRACKER ===
        box_left = QFrame()
        box_left.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #101828, stop:1 #0C1420);"
            "border: 1px solid #1A3050; border-radius: 8px;"
        )
        bl_layout = QVBoxLayout(box_left)
        bl_layout.setContentsMargins(12, 10, 12, 10)
        bl_layout.setSpacing(5)

        # Style Header
        style_header = QHBoxLayout()
        lbl_style_title = QLabel("ACCOMPANIMENT STYLE")
        lbl_style_title.setFont(HardwareFonts.micro_bold())
        lbl_style_title.setStyleSheet("color: #4A6A88; letter-spacing: 0.8px;")
        self.lbl_style_genre = QLabel("[POP & ROCK]")
        self.lbl_style_genre.setFont(HardwareFonts.micro_bold())
        self.lbl_style_genre.setStyleSheet(
            "color: #38B4FF; background: #0A1C30; padding: 2px 7px; "
            "border-radius: 3px; border: 1px solid #1A4070; font-weight: bold;"
        )
        style_header.addWidget(lbl_style_title)
        style_header.addStretch()
        style_header.addWidget(self.lbl_style_genre)
        bl_layout.addLayout(style_header)

        # Style Name (large, vivid)
        self.lbl_style_name = QLabel("8-Beat Modern Pop")
        font_style = QFont("Segoe UI", 14, QFont.Bold)
        self.lbl_style_name.setFont(font_style)
        self.lbl_style_name.setStyleSheet("color: #F0F8FF; font-weight: bold; letter-spacing: 0.3px;")
        bl_layout.addWidget(self.lbl_style_name)

        # Section & Action Line
        sec_box = QHBoxLayout()
        self.lbl_style_section = QLabel("SECTION: MAIN A  |  ACMP: ON")
        self.lbl_style_section.setFont(HardwareFonts.label_regular())
        self.lbl_style_section.setStyleSheet("color: #39FF8A; font-weight: bold;")
        sec_box.addWidget(self.lbl_style_section)
        sec_box.addStretch()

        self.btn_load_style_quick = QPushButton("📂 LOAD .STY")
        self.btn_load_style_quick.setFont(HardwareFonts.micro_bold())
        self.btn_load_style_quick.setStyleSheet(
            "background: #0E2418; color: #39FF8A; border: 1px solid #1E5030; "
            "padding: 3px 8px; border-radius: 4px; font-weight: bold;"
        )
        self.btn_load_style_quick.clicked.connect(self.loadStyleClicked.emit)
        sec_box.addWidget(self.btn_load_style_quick)

        self.btn_select_style = QPushButton("BROWSE STYLES")
        self.btn_select_style.setFont(HardwareFonts.micro_bold())
        self.btn_select_style.setStyleSheet(
            "background: #142030; color: #C8DEFA; border: 1px solid #2A4870; "
            "padding: 3px 10px; border-radius: 4px; font-weight: bold;"
        )
        self.btn_select_style.clicked.connect(self.styleClicked.emit)
        sec_box.addWidget(self.btn_select_style)
        bl_layout.addLayout(sec_box)

        # Gold accent divider
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0C1420, stop:0.3 #2A4060, stop:0.7 #2A4060, stop:1 #0C1420);")
        bl_layout.addWidget(div1)

        # Live Chord Tracker Section
        chord_header = QHBoxLayout()
        lbl_c_title = QLabel("LIVE CHORD TRACKER")
        lbl_c_title.setFont(HardwareFonts.micro_bold())
        lbl_c_title.setStyleSheet("color: #7B8D9E; letter-spacing: 0.5px;")
        chord_header.addWidget(lbl_c_title)
        chord_header.addStretch()

        self.lbl_beat_dots = QLabel("●   ○   ○   ○")
        self.lbl_beat_dots.setFont(HardwareFonts.micro_bold())
        self.lbl_beat_dots.setStyleSheet("color: #39FF8A; letter-spacing: 3px; font-weight: bold;")
        chord_header.addWidget(self.lbl_beat_dots)
        bl_layout.addLayout(chord_header)

        chord_row = QHBoxLayout()
        self.lbl_hero_chord = QLabel("C Major")
        font_hero = QFont("Segoe UI", 20, QFont.Bold)
        self.lbl_hero_chord.setFont(font_hero)
        self.lbl_hero_chord.setStyleSheet("color: #FFB726; font-weight: bold; letter-spacing: 0.5px;")
        chord_row.addWidget(self.lbl_hero_chord)
        chord_row.addStretch()

        self.lbl_rec_status = QLabel("SYNC ARMED • 4/4")
        self.lbl_rec_status.setFont(HardwareFonts.micro_bold())
        self.lbl_rec_status.setStyleSheet(
            "color: #38B4FF; background: #081828; padding: 3px 8px; "
            "border-radius: 4px; border: 1px solid #153060; font-weight: bold;"
        )
        chord_row.addWidget(self.lbl_rec_status)
        bl_layout.addLayout(chord_row)

        columns_layout.addWidget(box_left, 1)

        # === COLUMN 2: KEYBOARD VOICES & AUDIO SPECTRUM ===
        box_right = QFrame()
        box_right.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #101828, stop:1 #0C1420);"
            "border: 1px solid #1A3050; border-radius: 8px;"
        )
        br_layout = QVBoxLayout(box_right)
        br_layout.setContentsMargins(12, 10, 12, 10)
        br_layout.setSpacing(5)

        # Voices Title & Quick Load .RGT
        v_head = QHBoxLayout()
        lbl_v_title = QLabel("KEYBOARD VOICES")
        lbl_v_title.setFont(HardwareFonts.micro_bold())
        lbl_v_title.setStyleSheet("color: #4A6A88; letter-spacing: 0.8px;")
        v_head.addWidget(lbl_v_title)
        v_head.addStretch()

        self.btn_load_reg_quick = QPushButton("📂 LOAD .RGT")
        self.btn_load_reg_quick.setFont(HardwareFonts.micro_bold())
        self.btn_load_reg_quick.setStyleSheet(
            "background: #0A1C30; color: #38B4FF; border: 1px solid #1A4070; "
            "padding: 2px 8px; border-radius: 4px; font-weight: bold;"
        )
        self.btn_load_reg_quick.clicked.connect(self.loadRegistClicked.emit)
        v_head.addWidget(self.btn_load_reg_quick)
        br_layout.addLayout(v_head)

        # R1 Voice
        r1_box = QHBoxLayout()
        r1_tag = QLabel("[R1 MAIN]")
        r1_tag.setFont(HardwareFonts.micro_bold())
        r1_tag.setStyleSheet("color: #39FF8A; font-weight: bold; background: #0C2818; border: 1px solid #1E5030; padding: 2px 6px; border-radius: 3px;")
        self.lbl_r1_name = QLabel("Concert Grand Piano")
        self.lbl_r1_name.setFont(HardwareFonts.sub_bold())
        self.lbl_r1_name.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        r1_box.addWidget(r1_tag)
        r1_box.addWidget(self.lbl_r1_name)
        r1_box.addStretch()
        br_layout.addLayout(r1_box)

        # R2 Voice (Layer)
        r2_box = QHBoxLayout()
        r2_tag = QLabel("[R2 LAYER]")
        r2_tag.setFont(HardwareFonts.micro_bold())
        r2_tag.setStyleSheet("color: #38B4FF; font-weight: bold; background: #0E2538; border: 1px solid #1A4070; padding: 2px 6px; border-radius: 3px;")
        self.lbl_r2_name = QLabel("Warm String Ensemble  [OFF]")
        self.lbl_r2_name.setFont(HardwareFonts.label_regular())
        self.lbl_r2_name.setStyleSheet("color: #8C9BAA;")
        r2_box.addWidget(r2_tag)
        r2_box.addWidget(self.lbl_r2_name)
        r2_box.addStretch()
        br_layout.addLayout(r2_box)

        # Left Voice (Split)
        left_box = QHBoxLayout()
        left_tag = QLabel("[LEFT SPLIT]")
        left_tag.setFont(HardwareFonts.micro_bold())
        left_tag.setStyleSheet("color: #FFB726; font-weight: bold; background: #2D1D0A; border: 1px solid #5A3810; padding: 2px 6px; border-radius: 3px;")
        self.lbl_left_name = QLabel("Acoustic Upright Bass  [OFF]")
        self.lbl_left_name.setFont(HardwareFonts.label_regular())
        self.lbl_left_name.setStyleSheet("color: #8C9BAA;")
        left_box.addWidget(left_tag)
        left_box.addWidget(self.lbl_left_name)
        left_box.addStretch()
        br_layout.addLayout(left_box)

        # Subtle divider
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background: #1F2E3C;")
        br_layout.addWidget(div2)

        # Real-time Spectrum Visualizer
        spec_row = QHBoxLayout()
        lbl_spec = QLabel("SPECTRUM")
        lbl_spec.setFont(HardwareFonts.micro_bold())
        lbl_spec.setStyleSheet("color: #64748B; font-size: 8px;")
        spec_row.addWidget(lbl_spec)
        spec_row.addStretch()
        br_layout.addLayout(spec_row)

        self.spectrum = AudioSpectrumWidget(box_right)
        br_layout.addWidget(self.spectrum)

        columns_layout.addWidget(box_right, 1)
        layout.addLayout(columns_layout, 1)

        # -------------------------------------------------------------
        # BOTTOM REGISTRATION MEMORY STRIP (BANK 01 | Slots 1-8)
        # -------------------------------------------------------------
        reg_bar = QHBoxLayout()
        reg_bar.setSpacing(4)

        reg_lbl = QLabel("REGIST [BANK 01]:")
        reg_lbl.setFont(HardwareFonts.micro_bold())
        reg_lbl.setStyleSheet("color: #7B8D9E; font-size: 9px;")
        reg_bar.addWidget(reg_lbl)

        self.reg_indicators: List[QLabel] = []
        for i in range(1, 9):
            lbl = QLabel(f"{i} ○")
            lbl.setFont(HardwareFonts.micro_bold())
            lbl.setFixedSize(36, 18)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background: #0E141B; color: #5D6C7B; border: 1px solid #1E2B38; border-radius: 2px; font-size: 9px;")
            self.reg_indicators.append(lbl)
            reg_bar.addWidget(lbl)

        reg_bar.addStretch()
        layout.addLayout(reg_bar)

    def show_toast(self, text: str, color: str = "#39FF8A", duration_ms: int = 3500):
        """Display an animated HUD toast banner on the LCD screen."""
        self.lbl_hud_toast.setText(text)
        self.lbl_hud_toast.setStyleSheet(
            f"color: {color}; font-weight: bold; background: #0A1820; "
            f"padding: 2px 8px; border-radius: 3px; border: 1px solid {color};"
        )
        QTimer.singleShot(duration_ms, lambda: self.lbl_hud_toast.setText(""))


class VoiceSelectionPage(QWidget):
    """Page 2: PSR-S975 Voice Browser."""
    voiceSelected = Signal(str, int, str)  # target ("R1","R2","LEFT"), program, name

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Left Column: Category List
        cat_box = QVBoxLayout()
        cat_lbl = QLabel("VOICE CATEGORIES")
        cat_lbl.setFont(HardwareFonts.micro_bold())
        cat_lbl.setStyleSheet("color: #7B8D9E;")
        cat_box.addWidget(cat_lbl)

        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(1)
        self.cat_table.horizontalHeader().setVisible(False)
        self.cat_table.verticalHeader().setVisible(False)
        self.cat_table.setSelectionMode(QTableWidget.SingleSelection)
        self.cat_table.setStyleSheet("QTableWidget { background: #0E141B; border: 1px solid #223444; color: #E8EDF1; } QTableWidget::item:selected { background: #2B4560; color: #65D878; }")
        self.cat_table.horizontalHeader().setStretchLastSection(True)

        categories = [
            "Piano", "E.Piano", "Organ", "Accordion", "Guitar",
            "Bass", "Strings", "Choir", "Brass", "Woodwind",
            "Saxophone", "Synth Lead", "Synth Pad", "Percussion", "Drum Kits"
        ]
        self.cat_table.setRowCount(len(categories))
        for r, cat in enumerate(categories):
            item = QTableWidgetItem(cat)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.cat_table.setItem(r, 0, item)
        self.cat_table.selectRow(0)
        self.cat_table.currentCellChanged.connect(self._on_cat_changed)
        cat_box.addWidget(self.cat_table)
        layout.addLayout(cat_box, 1)

        # Right Column: Preset Voices List
        voice_box = QVBoxLayout()
        vh_box = QHBoxLayout()
        voice_lbl = QLabel("PRESET VOICES")
        voice_lbl.setFont(HardwareFonts.micro_bold())
        voice_lbl.setStyleSheet("color: #7B8D9E;")
        vh_box.addWidget(voice_lbl)

        vh_box.addStretch()

        self.btn_to_r1 = QPushButton("SET TO R1")
        self.btn_to_r1.setStyleSheet("background: #1E3825; color: #65D878; font-weight: bold; border: 1px solid #285435; padding: 2px 8px; border-radius: 2px;")
        self.btn_to_r1.clicked.connect(lambda: self._assign_selected("R1"))
        vh_box.addWidget(self.btn_to_r1)

        self.btn_to_r2 = QPushButton("SET TO R2")
        self.btn_to_r2.setStyleSheet("background: #1B3144; color: #4DA8DA; font-weight: bold; border: 1px solid #254764; padding: 2px 8px; border-radius: 2px;")
        self.btn_to_r2.clicked.connect(lambda: self._assign_selected("R2"))
        vh_box.addWidget(self.btn_to_r2)

        self.btn_to_left = QPushButton("SET TO LEFT")
        self.btn_to_left.setStyleSheet("background: #3B2E16; color: #FFB347; font-weight: bold; border: 1px solid #54411E; padding: 2px 8px; border-radius: 2px;")
        self.btn_to_left.clicked.connect(lambda: self._assign_selected("LEFT"))
        vh_box.addWidget(self.btn_to_left)

        voice_box.addLayout(vh_box)

        self.voice_table = QTableWidget()
        self.voice_table.setColumnCount(3)
        self.voice_table.setHorizontalHeaderLabels(["PC#", "Voice Name", "Type"])
        self.voice_table.verticalHeader().setVisible(False)
        self.voice_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.voice_table.setStyleSheet("QTableWidget { background: #0E141B; border: 1px solid #223444; color: #E8EDF1; } QTableWidget::item:selected { background: #2B4560; color: #FFFFFF; }")
        self.voice_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.voice_table.itemClicked.connect(self._on_table_item_clicked)
        self.voice_table.itemDoubleClicked.connect(self._on_table_item_clicked)
        voice_box.addWidget(self.voice_table)
        layout.addLayout(voice_box, 2)

        self._populate_category("Piano")

    def _on_table_item_clicked(self, item):
        self._assign_selected("R1")

    def _on_cat_changed(self, row, col, prev_r, prev_c):
        item = self.cat_table.item(row, 0)
        if item:
            self._populate_category(item.text())

    def _populate_category(self, cat_name: str):
        # Mapping category to GM standard presets
        catalog = {
            "Piano": [(0, "Acoustic Grand Piano"), (1, "Bright Acoustic Piano"), (2, "Electric Grand Piano"), (3, "Honky-tonk Piano")],
            "E.Piano": [(4, "Electric Piano 1 (Rhodes)"), (5, "Electric Piano 2 (DX7)"), (6, "Harpsichord"), (7, "Clavinet")],
            "Organ": [(16, "Drawbar Organ"), (17, "Percussive Organ"), (18, "Rock Organ"), (19, "Church Organ"), (20, "Reed Organ")],
            "Accordion": [(21, "Accordion"), (22, "Harmonica"), (23, "Tango Accordion")],
            "Guitar": [(24, "Acoustic Guitar (nylon)"), (25, "Acoustic Guitar (steel)"), (26, "Electric Guitar (jazz)"), (27, "Electric Guitar (clean)"), (28, "Overdriven Guitar"), (29, "Distortion Guitar")],
            "Bass": [(32, "Acoustic Bass"), (33, "Electric Bass (finger)"), (34, "Electric Bass (pick)"), (35, "Fretless Bass"), (36, "Slap Bass 1"), (38, "Synth Bass 1")],
            "Strings": [(40, "Violin"), (41, "Viola"), (42, "Cello"), (48, "String Ensemble 1"), (49, "String Ensemble 2"), (50, "Synth Strings 1"), (51, "Synth Strings 2")],
            "Choir": [(52, "Choir Aahs"), (53, "Voice Oohs"), (54, "Synth Voice"), (55, "Orchestra Hit")],
            "Brass": [(56, "Trumpet"), (57, "Trombone"), (58, "Tuba"), (60, "French Horn"), (61, "Brass Section"), (62, "Synth Brass 1")],
            "Woodwind": [(68, "Oboe"), (69, "English Horn"), (70, "Bassoon"), (71, "Clarinet"), (72, "Piccolo"), (73, "Flute"), (75, "Pan Flute")],
            "Saxophone": [(64, "Soprano Sax"), (65, "Alto Sax"), (66, "Tenor Sax"), (67, "Baritone Sax")],
            "Synth Lead": [(80, "Lead 1 (square)"), (81, "Lead 2 (sawtooth)"), (82, "Lead 3 (calliope)"), (87, "Lead 8 (bass + lead)")],
            "Synth Pad": [(88, "Pad 1 (new age)"), (89, "Pad 2 (warm)"), (90, "Pad 3 (polysynth)"), (91, "Pad 4 (choir)"), (92, "Pad 5 (bowed)")],
            "Percussion": [(11, "Vibraphone"), (12, "Marimba"), (13, "Xylophone"), (14, "Tubular Bells"), (114, "Steel Drums")],
            "Drum Kits": [(128, "Standard GM Drum Kit (Ch 10)"), (129, "Room Drum Kit"), (130, "Power Drum Kit"), (131, "Electronic Kit")]
        }

        voices = catalog.get(cat_name, [(0, "Grand Piano")])
        self.voice_table.setRowCount(len(voices))
        for r, (pc, name) in enumerate(voices):
            i_pc = QTableWidgetItem(f"{pc:03d}")
            i_name = QTableWidgetItem(name)
            i_type = QTableWidgetItem(cat_name)
            i_pc.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            i_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            i_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.voice_table.setItem(r, 0, i_pc)
            self.voice_table.setItem(r, 1, i_name)
            self.voice_table.setItem(r, 2, i_type)
        self.voice_table.selectRow(0)

    def _assign_selected(self, target: str):
        row = self.voice_table.currentRow()
        if row >= 0:
            pc_str = self.voice_table.item(row, 0).text()
            name_str = self.voice_table.item(row, 1).text()
            pc = int(pc_str)
            self.voiceSelected.emit(target, pc, name_str)


class StyleSelectionPage(QWidget):
    """Page 3: PSR-S975 Style Browser."""
    styleSelected = Signal(str)
    importStyleRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        head_box = QHBoxLayout()
        lbl = QLabel("ACCOMPANIMENT STYLE SELECTOR")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        head_box.addWidget(lbl)
        head_box.addStretch()
        layout.addLayout(head_box)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Style Name", "Category", "Default BPM", "Time Sig"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("QTableWidget { background: #0E141B; border: 1px solid #223444; color: #E8EDF1; } QTableWidget::item:selected { background: #2B4560; color: #65D878; }")
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.itemDoubleClicked.connect(self._on_double_click)

        styles = [
            ("Pop Groove", "Pop & Rock", "120", "4/4"),
            ("Classic Rock", "Rock", "130", "4/4"),
            ("Slow Ballad", "Ballad", "72", "4/4"),
            ("80s Synthwave", "Dance", "124", "4/4"),
            ("Funk & Disco", "Dance / Funk", "118", "4/4"),
            ("Latin Bossa Nova", "Latin", "132", "4/4"),
            ("Jazz Swing", "Jazz", "140", "4/4"),
            ("R&B Smooth Soul", "R&B / Soul", "96", "4/4"),
            ("Country Folk", "Country", "116", "4/4"),
            ("Ethiopian Tizita", "World / Ethnic", "95", "4/4"),
            ("Reggae Sunshine", "World / Reggae", "76", "4/4"),
            ("Classical Waltz", "Classical", "138", "3/4")
        ]
        self.table.setRowCount(len(styles))
        for r, (name, cat, bpm, ts) in enumerate(styles):
            for c, val in enumerate([name, cat, bpm, ts]):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(r, c, item)

        self.table.selectRow(0)
        self.table.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.table)

        btn_box = QHBoxLayout()
        self.btn_import = QPushButton("📂 IMPORT STYLE (.STY / .PRS / .MID / .JSON)")
        self.btn_import.setStyleSheet("background: #0A1C30; color: #38B4FF; font-weight: bold; border: 1px solid #1A4070; padding: 4px 12px; border-radius: 3px;")
        self.btn_import.clicked.connect(self.importStyleRequested.emit)
        btn_box.addWidget(self.btn_import)

        btn_box.addStretch()
        self.btn_load = QPushButton("LOAD SELECTED STYLE")
        self.btn_load.setStyleSheet("background: #1E3825; color: #65D878; font-weight: bold; border: 1px solid #285435; padding: 4px 16px; border-radius: 3px;")
        self.btn_load.clicked.connect(self._on_load_clicked)
        btn_box.addWidget(self.btn_load)
        layout.addLayout(btn_box)

    def _on_item_clicked(self, item):
        row = item.row()
        name = self.table.item(row, 0).text()
        self.styleSelected.emit(name)

    def _on_load_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            name = self.table.item(row, 0).text()
            self.styleSelected.emit(name)

    def _on_double_click(self, item):
        row = item.row()
        name = self.table.item(row, 0).text()
        self.styleSelected.emit(name)


class MixerPage(QWidget):
    """Page 4: 8-Channel Arranger & Voice Mixer."""
    channelVolumeChanged = Signal(str, float)  # channel_id, 0.0-1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl = QLabel("ARRANGER & VOICE CHANNEL MIXER")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        layout.addWidget(lbl)

        strips_box = QHBoxLayout()
        strips_box.setSpacing(8)

        channels = [
            ("R1", "Right 1", 100),
            ("R2", "Right 2", 75),
            ("LEFT", "Left", 85),
            ("DRUMS", "Drums", 100),
            ("BASS", "Bass", 90),
            ("CHORD1", "Chord 1", 80),
            ("CHORD2", "Chord 2", 70),
            ("PAD", "Pad", 65),
        ]

        self.sliders: Dict[str, QSlider] = {}
        for ch_id, ch_name, init_val in channels:
            frame = QFrame()
            frame.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 3px;")
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(4, 6, 4, 6)
            f_layout.setSpacing(4)
            f_layout.setAlignment(Qt.AlignCenter)

            tag = QLabel(ch_id)
            tag.setFont(HardwareFonts.micro_bold())
            tag.setStyleSheet("color: #4DA8DA;")
            f_layout.addWidget(tag, 0, Qt.AlignCenter)

            slider = QSlider(Qt.Vertical)
            slider.setRange(0, 127)
            slider.setValue(init_val)
            slider.setStyleSheet("QSlider::groove:vertical { background: #1C242E; width: 6px; border-radius: 3px; } QSlider::handle:vertical { background: #5D6C7B; height: 16px; margin: 0 -5px; border-radius: 2px; }")
            slider.valueChanged.connect(lambda v, c=ch_id: self.channelVolumeChanged.emit(c, v / 127.0))
            self.sliders[ch_id] = slider
            f_layout.addWidget(slider, 1, Qt.AlignCenter)

            lbl_val = QLabel(str(init_val))
            lbl_val.setFont(HardwareFonts.micro_regular())
            lbl_val.setStyleSheet("color: #CCD6E0;")
            slider.valueChanged.connect(lambda v, l=lbl_val: l.setText(str(v)))
            f_layout.addWidget(lbl_val, 0, Qt.AlignCenter)

            strips_box.addWidget(frame)

        layout.addLayout(strips_box)


class VoiceEffectsPage(QWidget):
    """Page 5: DSP, Reverb, Chorus, Touch curve, and Harmony."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        # 1. Reverb Frame
        rev_box = QFrame()
        rev_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 6px;")
        rb_layout = QVBoxLayout(rev_box)
        rb_title = QLabel("REVERB PROCESSOR")
        rb_title.setFont(HardwareFonts.micro_bold())
        rb_title.setStyleSheet("color: #4DA8DA;")
        rb_layout.addWidget(rb_title)

        self.cmb_rev = QComboBox()
        self.cmb_rev.addItems(["Hall 1 (Concert)", "Hall 2 (Warm)", "Room 1 (Studio)", "Stage 1", "Plate Reverb"])
        self.cmb_rev.setStyleSheet("background: #141E28; color: #E8EDF1; border: 1px solid #223444;")
        rb_layout.addWidget(self.cmb_rev)
        layout.addWidget(rev_box, 0, 0)

        # 2. Chorus Frame
        cho_box = QFrame()
        cho_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 6px;")
        cb_layout = QVBoxLayout(cho_box)
        cb_title = QLabel("CHORUS / FLANGER")
        cb_title.setFont(HardwareFonts.micro_bold())
        cb_title.setStyleSheet("color: #4DA8DA;")
        cb_layout.addWidget(cb_title)

        self.cmb_cho = QComboBox()
        self.cmb_cho.addItems(["Chorus 1 (Subtle)", "Chorus 2 (Deep)", "Flanger 1", "Symphonic Ensemble", "Celeste"])
        self.cmb_cho.setStyleSheet("background: #141E28; color: #E8EDF1; border: 1px solid #223444;")
        cb_layout.addWidget(self.cmb_cho)
        layout.addWidget(cho_box, 0, 1)

        # 3. Touch Response Frame
        touch_box = QFrame()
        touch_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 6px;")
        tb_layout = QVBoxLayout(touch_box)
        tb_title = QLabel("KEYBOARD TOUCH RESPONSE")
        tb_title.setFont(HardwareFonts.micro_bold())
        tb_title.setStyleSheet("color: #65D878;")
        tb_layout.addWidget(tb_title)

        self.cmb_touch = QComboBox()
        self.cmb_touch.addItems(["Normal (Linear)", "Soft 1 (Light touch)", "Soft 2 (Very light)", "Hard 1 (Expressive)", "Fixed (Velocity 100)"])
        self.cmb_touch.setStyleSheet("background: #141E28; color: #E8EDF1; border: 1px solid #223444;")
        tb_layout.addWidget(self.cmb_touch)
        layout.addWidget(touch_box, 1, 0)

        # 4. Harmony / Echo Frame
        harm_box = QFrame()
        harm_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 6px;")
        hb_layout = QVBoxLayout(harm_box)
        hb_title = QLabel("HARMONY & ARPEGGIATOR")
        hb_title.setFont(HardwareFonts.micro_bold())
        hb_title.setStyleSheet("color: #FFDE59;")
        hb_layout.addWidget(hb_title)

        self.cmb_harm = QComboBox()
        self.cmb_harm.addItems(["Off", "Duet", "Trio", "Block Harmony", "Country 2-Part", "Octave", "Arpeggio 16-Beat"])
        self.cmb_harm.setStyleSheet("background: #141E28; color: #E8EDF1; border: 1px solid #223444;")
        hb_layout.addWidget(self.cmb_harm)
        layout.addWidget(harm_box, 1, 1)


class RegistrationPage(QWidget):
    """Page 6: Registration Memory Manager (Banks & Slots)."""
    importBankRequested = Signal()
    exportBankRequested = Signal()
    slotSelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        head_box = QHBoxLayout()
        lbl = QLabel("REGISTRATION MEMORY BANK MANAGER")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        head_box.addWidget(lbl)
        head_box.addStretch()

        self.btn_import = QPushButton("📂 IMPORT BANK (.RGT / .JSON)")
        self.btn_import.setStyleSheet("background: #0A1C30; color: #38B4FF; font-weight: bold; border: 1px solid #1A4070; padding: 3px 10px; border-radius: 3px;")
        self.btn_import.clicked.connect(self.importBankRequested.emit)
        head_box.addWidget(self.btn_import)

        self.btn_export = QPushButton("💾 EXPORT BANK (.RGT / .JSON)")
        self.btn_export.setStyleSheet("background: #281D08; color: #FFB726; font-weight: bold; border: 1px solid #583E10; padding: 3px 10px; border-radius: 3px;")
        self.btn_export.clicked.connect(self.exportBankRequested.emit)
        head_box.addWidget(self.btn_export)

        layout.addLayout(head_box)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Slot", "R1 Voice", "Style", "Tempo"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("QTableWidget { background: #0E141B; border: 1px solid #223444; color: #E8EDF1; } QTableWidget::item:selected { background: #2B4560; color: #4DA8DA; }")
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.table.setRowCount(8)
        for i in range(8):
            self.table.setItem(i, 0, QTableWidgetItem(f"Slot {i+1}"))
            self.table.setItem(i, 1, QTableWidgetItem("Grand Piano" if i==0 else "Empty"))
            self.table.setItem(i, 2, QTableWidgetItem("8-Beat Pop" if i==0 else "---"))
            self.table.setItem(i, 3, QTableWidgetItem("120" if i==0 else "---"))

        layout.addWidget(self.table)

        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        self.btn_recall = QPushButton("RECALL SELECTED SLOT")
        self.btn_recall.setStyleSheet("background: #1E3825; color: #65D878; font-weight: bold; border: 1px solid #285435; padding: 4px 16px; border-radius: 3px;")
        self.btn_recall.clicked.connect(self._on_recall_clicked)
        btn_bar.addWidget(self.btn_recall)
        layout.addLayout(btn_bar)

    def _on_recall_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            self.slotSelected.emit(row + 1)


class USBFileExplorerPage(QWidget):
    """Page 7: USB & Local File Manager for Styles, Registrations, and Songs."""
    importStyleRequested = Signal()
    importRegistRequested = Signal()
    exportRegistRequested = Signal()
    styleFileSelected = Signal(str)
    registFileSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Actions Header
        header = QHBoxLayout()
        lbl = QLabel("USB / STORAGE MANAGER")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #38B4FF; letter-spacing: 0.8px; font-weight: bold;")
        header.addWidget(lbl)
        header.addStretch()

        self.btn_import_style = QPushButton("📂 LOAD STYLE (.STY)")
        self.btn_import_style.setFont(HardwareFonts.micro_bold())
        self.btn_import_style.setStyleSheet("background: #0D2818; color: #39FF8A; border: 1px solid #1E5830; padding: 4px 8px; border-radius: 3px; font-weight: bold;")
        self.btn_import_style.clicked.connect(self.importStyleRequested.emit)
        header.addWidget(self.btn_import_style)

        self.btn_import_regist = QPushButton("📂 LOAD REGIST (.RGT)")
        self.btn_import_regist.setFont(HardwareFonts.micro_bold())
        self.btn_import_regist.setStyleSheet("background: #0A1C30; color: #38B4FF; border: 1px solid #1A4070; padding: 4px 8px; border-radius: 3px; font-weight: bold;")
        self.btn_import_regist.clicked.connect(self.importRegistRequested.emit)
        header.addWidget(self.btn_import_regist)

        self.btn_export_regist = QPushButton("💾 EXPORT (.RGT)")
        self.btn_export_regist.setFont(HardwareFonts.micro_bold())
        self.btn_export_regist.setStyleSheet("background: #281D08; color: #FFB726; border: 1px solid #583E10; padding: 4px 8px; border-radius: 3px; font-weight: bold;")
        self.btn_export_regist.clicked.connect(self.exportRegistRequested.emit)
        header.addWidget(self.btn_export_regist)

        layout.addLayout(header)

        # Drag & Drop Zone Prompt
        drop_banner = QFrame()
        drop_banner.setStyleSheet("background: #081018; border: 1px dashed #224466; border-radius: 5px; padding: 5px;")
        db_layout = QHBoxLayout(drop_banner)
        db_layout.setContentsMargins(6, 4, 6, 4)
        lbl_drop = QLabel("⚡ DRAG & DROP ANY FILE: Drop any .STY, .PRS, .MID, .RGT, or .JSON file directly onto KIYA Piano to load immediately!")
        lbl_drop.setFont(HardwareFonts.label_regular())
        lbl_drop.setStyleSheet("color: #88B0D8; font-weight: bold;")
        db_layout.addWidget(lbl_drop)
        layout.addWidget(drop_banner)

        # Table of Files
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "File Name", "Size", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("QTableWidget { background: #0A0F16; border: 1px solid #1A2838; color: #E8F4FF; } QTableWidget::item:selected { background: #1C3550; color: #39FF8A; }")
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemDoubleClicked.connect(self._on_table_double_clicked)
        layout.addWidget(self.table)

        self._file_paths = []
        self.refresh_file_list()

    def refresh_file_list(self):
        styles_dir = Path("resources/styles")
        reg_dir = Path("resources/registrations")

        files = []
        if styles_dir.exists():
            for f in sorted(styles_dir.iterdir()):
                if f.suffix.lower() in (".sty", ".prs", ".bcs", ".sst", ".mid", ".json"):
                    size_kb = f.stat().st_size / 1024.0
                    files.append(("STYLE", f.name, f"{size_kb:.1f} KB", str(f)))

        if reg_dir.exists():
            for f in sorted(reg_dir.iterdir()):
                if f.suffix.lower() in (".rgt", ".reg", ".json"):
                    size_kb = f.stat().st_size / 1024.0
                    files.append(("REGIST", f.name, f"{size_kb:.1f} KB", str(f)))

        self.table.setRowCount(len(files))
        self._file_paths = []
        for r, (ftype, fname, size_str, fpath) in enumerate(files):
            self._file_paths.append((ftype, fpath))
            i_type = QTableWidgetItem(f"[{ftype}]")
            i_name = QTableWidgetItem(fname)
            i_size = QTableWidgetItem(size_str)
            i_act = QTableWidgetItem("▶ LOAD")

            if ftype == "STYLE":
                i_type.setForeground(QColor("#39FF8A"))
            else:
                i_type.setForeground(QColor("#38B4FF"))
            i_act.setForeground(QColor("#FFB726"))

            for it in (i_type, i_name, i_size, i_act):
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.setItem(r, 0, i_type)
            self.table.setItem(r, 1, i_name)
            self.table.setItem(r, 2, i_size)
            self.table.setItem(r, 3, i_act)

    def _on_table_double_clicked(self, item):
        row = item.row()
        if 0 <= row < len(self._file_paths):
            ftype, fpath = self._file_paths[row]
            if ftype == "STYLE":
                self.styleFileSelected.emit(fpath)
            else:
                self.registFileSelected.emit(fpath)


class SongPlayerPage(QWidget):
    """Page 7: MIDI & Audio File Player / Recorder."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl = QLabel("MULTI-TRACK SONG PLAYER & RECORDER")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        layout.addWidget(lbl)

        song_box = QFrame()
        song_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 10px;")
        sb_layout = QVBoxLayout(song_box)

        self.lbl_current_song = QLabel("No Song File Loaded (Ready to Record)")
        self.lbl_current_song.setFont(HardwareFonts.display_bold())
        self.lbl_current_song.setStyleSheet("color: #FFFFFF;")
        sb_layout.addWidget(self.lbl_current_song)

        self.lbl_song_time = QLabel("00:00:00 / 00:00:00")
        self.lbl_song_time.setFont(HardwareFonts.sub_bold())
        self.lbl_song_time.setStyleSheet("color: #4DA8DA;")
        sb_layout.addWidget(self.lbl_song_time)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setStyleSheet("QSlider::groove:horizontal { background: #1C242E; height: 6px; border-radius: 3px; } QSlider::handle:horizontal { background: #65D878; width: 14px; margin: -4px 0; border-radius: 2px; }")
        sb_layout.addWidget(self.seek_slider)

        layout.addWidget(song_box)


class MidiStatusPage(QWidget):
    """Page 8: System MIDI Status & 16-Channel Live Activity."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl = QLabel("HARDWARE MIDI PORTS & 16-CHANNEL MONITOR")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        layout.addWidget(lbl)

        status_box = QFrame()
        status_box.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 8px;")
        sb_layout = QVBoxLayout(status_box)

        self.lbl_midi_out = QLabel("MIDI OUTPUT: Microsoft GS Wavetable Synth (pygame.midi)")
        self.lbl_midi_out.setFont(HardwareFonts.label_regular())
        self.lbl_midi_out.setStyleSheet("color: #65D878;")
        sb_layout.addWidget(self.lbl_midi_out)

        self.lbl_midi_in = QLabel("MIDI INPUT: Active (Scanning system MIDI controllers...)")
        self.lbl_midi_in.setFont(HardwareFonts.label_regular())
        self.lbl_midi_in.setStyleSheet("color: #4DA8DA;")
        sb_layout.addWidget(self.lbl_midi_in)

        layout.addWidget(status_box)

        # 16-channel LED indicators
        matrix_box = QGridLayout()
        matrix_box.setSpacing(4)
        for ch in range(16):
            btn = QPushButton(f"CH {ch+1}")
            btn.setEnabled(False)
            btn.setStyleSheet("background: #141E28; color: #5D6C7B; border: 1px solid #223444; border-radius: 2px; padding: 4px;")
            matrix_box.addWidget(btn, ch // 8, ch % 8)
        layout.addLayout(matrix_box)


class AudioSettingsPage(QWidget):
    """Page 9: Audio Driver & SoundFont Synthesizer Settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl = QLabel("AUDIO ENGINE & SOUNDFONT CONFIGURATION")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        layout.addWidget(lbl)

        card = QFrame()
        card.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 10px;")
        c_layout = QVBoxLayout(card)

        self.lbl_eng_mode = QLabel("Current Audio Backend: Hybrid (Windows GS Wavetable + Real-time DSP)")
        self.lbl_eng_mode.setFont(HardwareFonts.sub_bold())
        self.lbl_eng_mode.setStyleSheet("color: #65D878;")
        c_layout.addWidget(self.lbl_eng_mode)

        self.lbl_sr = QLabel("Sample Rate: 44,100 Hz  |  Latency Buffer: 128 samples (~2.9 ms)")
        self.lbl_sr.setFont(HardwareFonts.label_regular())
        self.lbl_sr.setStyleSheet("color: #CCD6E0;")
        c_layout.addWidget(self.lbl_sr)

        layout.addWidget(card)


class SystemSettingsPage(QWidget):
    """Page 10: System Tuning, Split Point, Keymap."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        lbl = QLabel("INSTRUMENT SYSTEM SETTINGS & KEYMAP")
        lbl.setFont(HardwareFonts.micro_bold())
        lbl.setStyleSheet("color: #7B8D9E;")
        layout.addWidget(lbl)

        card = QFrame()
        card.setStyleSheet("background: #0E141B; border: 1px solid #223444; border-radius: 4px; padding: 10px;")
        c_layout = QVBoxLayout(card)

        c1 = QLabel("Master Tuning: 440.0 Hz (Concert Pitch)")
        c1.setFont(HardwareFonts.label_regular())
        c1.setStyleSheet("color: #E8EDF1;")
        c_layout.addWidget(c1)

        c2 = QLabel("Keyboard Split Point: F#3 (Note 54) - Adjustable via Split Button")
        c2.setFont(HardwareFonts.label_regular())
        c2.setStyleSheet("color: #E8EDF1;")
        c_layout.addWidget(c2)

        c3 = QLabel("PC Keyboard Mapping: Z-M (Lower Octave), Q-U (Upper Octave), Black Keys (S,D,G,H,J,2,3,5,6,7)")
        c3.setFont(HardwareFonts.label_regular())
        c3.setStyleSheet("color: #4DA8DA;")
        c_layout.addWidget(c3)

        layout.addWidget(card)


# =========================================================================
# CENTRAL RECESSED LCD SCREEN ASSEMBLY WITH SOFTKEYS
# =========================================================================

class CentralLCDDisplay(QWidget):
    """
    Central recessed 7-inch color display module for PSR-S975:
    - Left softkeys [A], [B], [C], [D], [E]
    - Center color display stack with 10 functional pages (including USB/FILE manager)
    - Right softkeys [F], [G], [H], [I], [J]
    - Top Tab buttons [< TAB] and [TAB >]
    """
    pageChanged = Signal(int)
    softkeyPressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CentralLCDDisplay")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # 1. Left Softkeys [A] - [E]
        left_softkeys = QVBoxLayout()
        left_softkeys.setSpacing(6)
        left_softkeys.setAlignment(Qt.AlignCenter)
        self.softkeys_left: List[PhysicalButton] = []
        for name in ["A", "B", "C", "D", "E"]:
            btn = PhysicalButton(name, width=32, height=28, button_color=HardwareColors.BUTTON_DARK)
            btn.clicked.connect(lambda n=name: self.softkeyPressed.emit(n))
            self.softkeys_left.append(btn)
            left_softkeys.addWidget(btn)
        main_layout.addLayout(left_softkeys)

        # 2. Central Recessed Screen Bezel & Stack
        self.bezel = LCDScreenBezel(self)
        bezel_layout = QVBoxLayout(self.bezel)
        bezel_layout.setContentsMargins(6, 6, 6, 6)
        bezel_layout.setSpacing(4)

        # Top Page Tabs Bar
        tab_bar = QHBoxLayout()
        tab_bar.setSpacing(2)

        self.btn_tab_prev = PhysicalButton("◀", width=30, height=20, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tab_prev.clicked.connect(self.prev_page)
        tab_bar.addWidget(self.btn_tab_prev)

        self.tab_buttons: List[QPushButton] = []
        page_names = ["PERF", "VOICE", "STYLE", "MIXER", "DSP/FX", "REGIST", "USB/FILE", "SONG", "MIDI", "SYSTEM"]
        for idx, p_name in enumerate(page_names):
            btn = QPushButton(p_name)
            btn.setFont(HardwareFonts.micro_regular())
            btn.setFixedHeight(20)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { background: #141C24; color: #7B8D9E; border: 1px solid #1E2B38; border-radius: 2px; padding: 0 2px; font-size: 10px; }
                QPushButton:checked { background: #22374C; color: #65D878; font-weight: bold; border-bottom: 2px solid #65D878; }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.switch_to_page(i))
            self.tab_buttons.append(btn)
            tab_bar.addWidget(btn)

        self.btn_tab_next = PhysicalButton("▶", width=30, height=20, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tab_next.clicked.connect(self.next_page)
        tab_bar.addWidget(self.btn_tab_next)

        bezel_layout.addLayout(tab_bar)

        # QStackedWidget with the real pages
        self.stack = QStackedWidget(self.bezel)
        self.stack.setStyleSheet("background: #121A22; border-radius: 3px;")

        self.p_perf = MainPerformancePage()
        self.p_voice = VoiceSelectionPage()
        self.p_style = StyleSelectionPage()
        self.p_mixer = MixerPage()
        self.p_effects = VoiceEffectsPage()
        self.p_regist = RegistrationPage()
        self.p_file = USBFileExplorerPage()
        self.p_song = SongPlayerPage()
        self.p_midi = MidiStatusPage()
        self.p_system = SystemSettingsPage()

        self.stack.addWidget(self.p_perf)    # 0
        self.stack.addWidget(self.p_voice)   # 1
        self.stack.addWidget(self.p_style)   # 2
        self.stack.addWidget(self.p_mixer)   # 3
        self.stack.addWidget(self.p_effects) # 4
        self.stack.addWidget(self.p_regist)  # 5
        self.stack.addWidget(self.p_file)    # 6
        self.stack.addWidget(self.p_song)    # 7
        self.stack.addWidget(self.p_midi)    # 8
        self.stack.addWidget(self.p_system)  # 9

        bezel_layout.addWidget(self.stack)
        main_layout.addWidget(self.bezel, 1)

        # 3. Right Softkeys [F] - [J]
        right_softkeys = QVBoxLayout()
        right_softkeys.setSpacing(6)
        right_softkeys.setAlignment(Qt.AlignCenter)
        self.softkeys_right: List[PhysicalButton] = []
        for name in ["F", "G", "H", "I", "J"]:
            btn = PhysicalButton(name, width=32, height=28, button_color=HardwareColors.BUTTON_DARK)
            btn.clicked.connect(lambda n=name: self.softkeyPressed.emit(n))
            self.softkeys_right.append(btn)
        main_layout.addLayout(right_softkeys)

        self.switch_to_page(0)

    def switch_to_page(self, index: int):
        index = max(0, min(self.stack.count() - 1, index))
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
        self.pageChanged.emit(index)

    def next_page(self):
        curr = self.stack.currentIndex()
        self.switch_to_page((curr + 1) % self.stack.count())

    def prev_page(self):
        curr = self.stack.currentIndex()
        self.switch_to_page((curr - 1) % self.stack.count())

    def show_toast(self, text: str, color: str = "#39FF8A", duration_ms: int = 3500):
        """Display an animated HUD toast banner on the LCD screen."""
        if hasattr(self, "p_perf"):
            self.p_perf.show_toast(text, color, duration_ms)

