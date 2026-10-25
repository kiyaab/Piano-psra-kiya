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
    QPainter, QColor, QPen, QBrush, QFont, QPaintEvent, QLinearGradient
)

from ui.physical_button import PhysicalButton
from ui.widgets.knob_slider import DialKnob
from ui.hardware_theme import HardwareColors, HardwareFonts


class DigitalDisplayReadout(QFrame):
    """
    Realistic backlit 7-segment LED digital display box
    used for Transpose, Octave, and Tempo values.
    Features authentic recessed dark lens with glowing digits and faint unlit segment ghosting.
    """
    def __init__(self, title: str = "TRANSPOSE", initial_text: str = "+0", color: str = "#10B981", parent=None):
        super().__init__(parent)
        self.title = title
        self.text_value = initial_text
        self.glow_color = QColor(color)
        self.setFixedSize(68, 38)
        self.setStyleSheet("background: transparent;")

    def set_value(self, val_text: str):
        self.text_value = val_text
        self.update()

    def set_color(self, color_hex: str):
        self.glow_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Recessed background bezel socket
        painter.setPen(QPen(QColor("#040508"), 1.5))
        painter.setBrush(QBrush(QColor("#070A0F")))
        painter.drawRoundedRect(0, 0, w, h, 4.0, 4.0)

        # Inner dark display glass with subtle top-to-bottom shading
        lens_grad = QLinearGradient(0, 1, 0, h - 2)
        lens_grad.setColorAt(0.0, QColor("#0D131C"))
        lens_grad.setColorAt(0.5, QColor("#080D14"))
        lens_grad.setColorAt(1.0, QColor("#05080E"))
        painter.setPen(QPen(QColor("#1A2433"), 1.0))
        painter.setBrush(lens_grad)
        painter.drawRoundedRect(1, 1, w - 2, h - 2, 3.0, 3.0)

        # 1px top glass highlight
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1.0))
        painter.drawLine(3, 2, w - 4, 2)

        # Title at top
        painter.setFont(HardwareFonts.micro_bold())
        painter.setPen(QColor("#71859E"))
        title_h = max(10.0, h * 0.36)
        painter.drawText(QRectF(1, 1, w - 2, title_h), Qt.AlignCenter, self.title)

        # Glowing digital readout (glow halo + brilliant core)
        painter.setFont(HardwareFonts.sub_bold())
        text_rect = QRectF(1, title_h - 1, w - 2, h - title_h)

        # Halo
        halo_col = QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), 60)
        painter.setPen(halo_col)
        painter.drawText(text_rect.translated(0, 0.5), Qt.AlignCenter, self.text_value)

        # Brilliant digit core
        core_col = QColor(
            min(255, self.glow_color.red() + 60),
            min(255, self.glow_color.green() + 60),
            min(255, self.glow_color.blue() + 60)
        )
        painter.setPen(core_col)
        painter.drawText(text_rect, Qt.AlignCenter, self.text_value)


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

    # Style category & file load signals
    styleCategorySelected = Signal(str)
    loadStyleRequested = Signal()

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
        song_group.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #10141E,stop:1 #0C1018); border: 1px solid #1E2640; border-radius: 5px; padding: 4px;")
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
        cat_group.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #10141E,stop:1 #0C1018); border: 1px solid #1E2640; border-radius: 5px; padding: 4px;")
        cg_layout = QVBoxLayout(cat_group)
        cg_layout.setContentsMargins(6, 4, 6, 4)
        cg_layout.setSpacing(4)

        cg_header = QHBoxLayout()
        cg_title = QLabel("STYLE CATEGORIES")
        cg_title.setFont(HardwareFonts.micro_bold())
        cg_title.setStyleSheet("color: #657585;")
        cg_header.addWidget(cg_title)
        cg_header.addStretch()

        self.btn_import_style = PhysicalButton("LOAD .STY", width=68, height=22, button_color=HardwareColors.BUTTON_DARK, indicator="blue")
        self.btn_import_style.clicked.connect(self.loadStyleRequested.emit)
        cg_header.addWidget(self.btn_import_style)
        cg_layout.addLayout(cg_header)

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
            btn = PhysicalButton(
                cat_name,
                width=72,
                height=26,
                button_color=HardwareColors.BUTTON_DARK,
                indicator="green" if cat_name == "POP & ROCK" else None
            )
            btn.clicked.connect(lambda c=cat_name: self._on_cat_clicked(c))
            self.style_cat_buttons[cat_name] = btn
            cat_grid.addWidget(btn, row, col)

        cg_layout.addLayout(cat_grid)
        main_layout.addWidget(cat_group)

        # --- ROW 3: TEMPO, METRONOME, TRANSPOSE & OCTAVE ---
        perf_group = QFrame()
        perf_group.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #10141E,stop:1 #0C1018); border: 1px solid #1E2640; border-radius: 5px; padding: 4px;")
        pg_layout = QVBoxLayout(perf_group)
        pg_layout.setContentsMargins(6, 4, 6, 4)
        pg_layout.setSpacing(6)

        # Sub-Row A: Tempo & Metronome with Digital BPM Readout
        row_tempo = QHBoxLayout()
        row_tempo.setSpacing(4)

        self.display_tempo = DigitalDisplayReadout(title="BPM", initial_text="120", color="#39FF8A")
        self.display_tempo.setFixedSize(58, 30)
        row_tempo.addWidget(self.display_tempo)

        self.btn_tempo_dec = PhysicalButton("−", width=28, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tempo_dec.clicked.connect(self.tempoDown.emit)
        row_tempo.addWidget(self.btn_tempo_dec)

        self.btn_tap = PhysicalButton("TAP", width=34, height=28, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_tap.clicked.connect(self.tapTempo.emit)
        row_tempo.addWidget(self.btn_tap)

        self.btn_tempo_inc = PhysicalButton("+", width=28, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_tempo_inc.clicked.connect(self.tempoUp.emit)
        row_tempo.addWidget(self.btn_tempo_inc)

        row_tempo.addStretch()

        self.btn_metro = PhysicalButton("METRO", secondary_text="ON/OFF", width=52, height=28, button_color=HardwareColors.BUTTON_DARK, indicator="amber")
        self.btn_metro.clicked.connect(self.metronomeToggle.emit)
        row_tempo.addWidget(self.btn_metro)

        pg_layout.addLayout(row_tempo)

        # Sub-Row B: Transpose & Octave Shift
        row_pitch = QHBoxLayout()
        row_pitch.setSpacing(4)

        # Transpose (Amber LED Display)
        self.btn_trans_dec = PhysicalButton("−", width=26, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_trans_dec.clicked.connect(self.transposeDown.emit)
        row_pitch.addWidget(self.btn_trans_dec)

        self.display_transpose = DigitalDisplayReadout(title="TRANSPOSE", initial_text="+0", color="#FFB726")
        self.display_transpose.setFixedSize(64, 30)
        row_pitch.addWidget(self.display_transpose)

        self.btn_trans_inc = PhysicalButton("+", width=26, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_trans_inc.clicked.connect(self.transposeUp.emit)
        row_pitch.addWidget(self.btn_trans_inc)

        row_pitch.addStretch()

        # Octave (Cyan LED Display)
        self.btn_oct_dec = PhysicalButton("OCT −", width=42, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_oct_dec.clicked.connect(self.octaveDown.emit)
        row_pitch.addWidget(self.btn_oct_dec)

        self.display_octave = DigitalDisplayReadout(title="OCTAVE", initial_text="0", color="#38B4FF")
        self.display_octave.setFixedSize(54, 30)
        row_pitch.addWidget(self.display_octave)

        self.btn_oct_inc = PhysicalButton("OCT +", width=42, height=28, button_color=HardwareColors.BUTTON_DARK)
        self.btn_oct_inc.clicked.connect(self.octaveUp.emit)
        row_pitch.addWidget(self.btn_oct_inc)

        pg_layout.addLayout(row_pitch)

        main_layout.addWidget(perf_group)

    def _on_cat_clicked(self, cat_name: str):
        for name, btn in self.style_cat_buttons.items():
            btn.set_led(name == cat_name)
        self.styleCategorySelected.emit(cat_name)
