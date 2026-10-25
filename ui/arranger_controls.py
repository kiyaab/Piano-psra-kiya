"""
KIYA Piano Studio Pro - Left Hardware Control Section (PSR-S975 Style)
Contains:
1. Master Volume & Mic/Line Level controls
2. Song Playback & Recording Transport cluster
3. Style Category Selectors
4. Real-time Tempo, Tap Tempo & Metronome controls
5. Master Transpose & Octave shift with glowing digital display
"""

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPaintEvent
)

from ui.physical_button import PhysicalButton
from ui.widgets.knob_slider import DialKnob
from ui.hardware_theme import HardwareColors, HardwareFonts


class DigitalDisplayReadout(QFrame):
    """
    Realistic backlit 7-segment LED digital display box
    used for Transpose, Octave, and Tempo values.
    """
    def __init__(self, title: str = "TRANSPOSE", initial_text: str = "+0", parent=None):
        super().__init__(parent)
        self.title = title
        self.text_value = initial_text
        self.setFixedSize(68, 38)
        self.setStyleSheet("background: transparent;")

    def set_value(self, val_text: str):
        self.text_value = val_text
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Recessed background bezel
        painter.setPen(QPen(QColor("#050608"), 1.5))
        painter.setBrush(QBrush(QColor("#080D12")))
        painter.drawRoundedRect(0, 0, w, h, 3.0, 3.0)

        # 1px top highlight
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
        painter.drawLine(2, 1, w - 3, 1)

        # Title at top
        painter.setFont(HardwareFonts.micro_bold())
        painter.setPen(QColor("#718096"))
        title_h = max(10.0, h * 0.38)
        painter.drawText(QRectF(1, 1, w - 2, title_h), Qt.AlignCenter, self.title)

        # Glowing green/amber digital readout
        painter.setFont(HardwareFonts.sub_bold())
        painter.setPen(QColor("#10B981"))
        painter.drawText(QRectF(1, title_h - 1, w - 2, h - title_h), Qt.AlignCenter, self.text_value)


class LeftControlPanel(QWidget):
    """
    Upper-left hardware panel:
    - Master Volume & Balance
    - Song Transport (Prev, Next, Play, Stop, Rec)
    - Style Category Selectors
    - Tempo / Tap / Metronome
    - Transpose / Octave controls
    """
    # Song signals
    songPrev = Signal()
    songNext = Signal()
    songPlayPause = Signal()
    songStop = Signal()
    songRecord = Signal()
    songSelect = Signal()

    # Style category signal
    styleCategorySelected = Signal(str)

    # Tempo / Performance signals
    tempoUp = Signal()
    tempoDown = Signal()
    tapTempo = Signal()
    metronomeToggle = Signal()
    transposeUp = Signal()
    transposeDown = Signal()
    octaveUp = Signal()
    octaveDown = Signal()
    masterVolumeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LeftControlPanel")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(8)

        # --- ROW 1: MASTER VOLUME & SONG CONTROLS ---
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Master Volume Knob
        vol_box = QVBoxLayout()
        vol_box.setSpacing(2)
        vol_box.setAlignment(Qt.AlignCenter)
        lbl_vol = QLabel("MASTER VOL")
        lbl_vol.setFont(HardwareFonts.micro_bold())
        lbl_vol.setStyleSheet("color: #7B8594; letter-spacing: 0.5px;")
        lbl_vol.setAlignment(Qt.AlignCenter)
        vol_box.addWidget(lbl_vol)

        self.knob_vol = DialKnob(title="", min_val=0.0, max_val=1.0, default_val=0.85)
        self.knob_vol.valueChanged.connect(self.masterVolumeChanged.emit)
        vol_box.addWidget(self.knob_vol, 0, Qt.AlignCenter)
        top_row.addLayout(vol_box)

        # Song Transport Group
        song_group = QFrame()
        song_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        sg_layout = QVBoxLayout(song_group)
        sg_layout.setContentsMargins(6, 4, 6, 4)
        sg_layout.setSpacing(4)

        sg_title = QLabel("SONG PLAYER / RECORDER")
        sg_title.setFont(HardwareFonts.micro_bold())
        sg_title.setStyleSheet("color: #657585;")
        sg_layout.addWidget(sg_title)

        sg_btns = QHBoxLayout()
        sg_btns.setSpacing(4)

        self.btn_song_prev = PhysicalButton("⏮", width=36, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_song_prev.clicked.connect(self.songPrev.emit)
        sg_btns.addWidget(self.btn_song_prev)

        self.btn_song_next = PhysicalButton("⏭", width=36, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_song_next.clicked.connect(self.songNext.emit)
        sg_btns.addWidget(self.btn_song_next)

        self.btn_song_stop = PhysicalButton("⏹", secondary_text="STOP", width=42, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_song_stop.clicked.connect(self.songStop.emit)
        sg_btns.addWidget(self.btn_song_stop)

        self.btn_song_play = PhysicalButton("▶/⏸", secondary_text="PLAY", width=44, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="green")
        self.btn_song_play.clicked.connect(self.songPlayPause.emit)
        sg_btns.addWidget(self.btn_song_play)

        self.btn_song_rec = PhysicalButton("⏺", secondary_text="REC", width=42, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="red")
        self.btn_song_rec.clicked.connect(self.songRecord.emit)
        sg_btns.addWidget(self.btn_song_rec)

        sg_layout.addLayout(sg_btns)
        top_row.addWidget(song_group)

        main_layout.addLayout(top_row)

        # --- ROW 2: STYLE CATEGORY SELECTION MATRIX ---
        cat_group = QFrame()
        cat_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        cg_layout = QVBoxLayout(cat_group)
        cg_layout.setContentsMargins(6, 4, 6, 4)
        cg_layout.setSpacing(4)

        cg_title = QLabel("STYLE CATEGORIES")
        cg_title.setFont(HardwareFonts.micro_bold())
        cg_title.setStyleSheet("color: #657585;")
        cg_layout.addWidget(cg_title)

        cat_grid = QGridLayout()
        cat_grid.setSpacing(4)

        style_cats = [
            ("POP & ROCK", 0, 0), ("BALLAD", 0, 1),
            ("DANCE", 0, 2), ("LATIN", 0, 3),
            ("JAZZ", 1, 0), ("R&B / SOUL", 1, 1),
            ("COUNTRY", 1, 2), ("WORLD / ETHNIC", 1, 3)
        ]
        self.style_cat_buttons = {}
        for cat_name, row, col in style_cats:
            btn = PhysicalButton(cat_name, width=72, height=26, button_color=HardwareColors.BUTTON_DARK)
            btn.clicked.connect(lambda c=cat_name: self.styleCategorySelected.emit(c))
            self.style_cat_buttons[cat_name] = btn
            cat_grid.addWidget(btn, row, col)

        cg_layout.addLayout(cat_grid)
        main_layout.addWidget(cat_group)

        # --- ROW 3: TEMPO, METRONOME, TRANSPOSE & OCTAVE ---
        perf_group = QFrame()
        perf_group.setStyleSheet("background: #14161A; border: 1px solid #22252C; border-radius: 4px; padding: 4px;")
        pg_layout = QVBoxLayout(perf_group)
        pg_layout.setContentsMargins(6, 4, 6, 4)
        pg_layout.setSpacing(6)

        # Sub-Row A: Tempo & Metronome
        row_tempo = QHBoxLayout()
        row_tempo.setSpacing(6)

        lbl_tempo_title = QLabel("TEMPO")
        lbl_tempo_title.setFont(HardwareFonts.micro_bold())
        lbl_tempo_title.setStyleSheet("color: #7B8594; font-size: 9px;")
        row_tempo.addWidget(lbl_tempo_title)

        self.btn_tempo_dec = PhysicalButton("−", width=32, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tempo_dec.clicked.connect(self.tempoDown.emit)
        row_tempo.addWidget(self.btn_tempo_dec)

        self.btn_tap = PhysicalButton("TAP", width=38, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_tap.clicked.connect(self.tapTempo.emit)
        row_tempo.addWidget(self.btn_tap)

        self.btn_tempo_inc = PhysicalButton("+", width=32, height=26, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tempo_inc.clicked.connect(self.tempoUp.emit)
        row_tempo.addWidget(self.btn_tempo_inc)

        row_tempo.addStretch()

        lbl_m = QLabel("METRO")
        lbl_m.setFont(HardwareFonts.micro_bold())
        lbl_m.setStyleSheet("color: #7B8594; font-size: 9px;")
        row_tempo.addWidget(lbl_m)

        self.btn_metro = PhysicalButton("ON/OFF", width=50, height=26, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_metro.clicked.connect(self.metronomeToggle.emit)
        row_tempo.addWidget(self.btn_metro)

        pg_layout.addLayout(row_tempo)

        # Sub-Row B: Transpose & Octave Shift
        row_pitch = QHBoxLayout()
        row_pitch.setSpacing(4)

        # Transpose
        self.btn_trans_dec = PhysicalButton("−", width=26, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_trans_dec.clicked.connect(self.transposeDown.emit)
        row_pitch.addWidget(self.btn_trans_dec)

        self.display_transpose = DigitalDisplayReadout(title="TRANSPOSE", initial_text="+0")
        self.display_transpose.setFixedSize(64, 30)
        row_pitch.addWidget(self.display_transpose)

        self.btn_trans_inc = PhysicalButton("+", width=26, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_trans_inc.clicked.connect(self.transposeUp.emit)
        row_pitch.addWidget(self.btn_trans_inc)

        row_pitch.addStretch()

        # Octave
        self.btn_oct_dec = PhysicalButton("OCT −", width=42, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_oct_dec.clicked.connect(self.octaveDown.emit)
        row_pitch.addWidget(self.btn_oct_dec)

        self.display_octave = DigitalDisplayReadout(title="OCTAVE", initial_text="0")
        self.display_octave.setFixedSize(54, 30)
        row_pitch.addWidget(self.display_octave)

        self.btn_oct_inc = PhysicalButton("OCT +", width=42, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_oct_inc.clicked.connect(self.octaveUp.emit)
        row_pitch.addWidget(self.btn_oct_inc)

        pg_layout.addLayout(row_pitch)

        main_layout.addWidget(perf_group)
