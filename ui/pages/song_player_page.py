"""
KIYA Piano Studio Pro - MIDI Song Player & Piano Roll Page
Combines multi-track SMF playback with an embedded interactive Piano Roll Editor.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QFileDialog, QListWidget, QFrame
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)
from songs.piano_roll import PianoRollWidget

class SongPlayerPage(QWidget):
    """Song player and piano roll editor view."""

    load_midi_requested = Signal(str)
    play_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()
    tempo_scale_changed = Signal(float)
    transpose_changed = Signal(int)
    note_preview_requested = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # -------------------------------------------------------------
        # TOP ROW: Song Player Transport & Meta Controls
        # -------------------------------------------------------------
        player_group = QGroupBox("MIDI SONG PLAYER")
        player_layout = QHBoxLayout(player_group)
        player_layout.setSpacing(12)

        self.btn_load = QPushButton("📁 Load MIDI File...")
        self.btn_load.clicked.connect(self._on_load_clicked)
        player_layout.addWidget(self.btn_load)

        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold;")
        self.btn_play.clicked.connect(self.play_requested.emit)
        player_layout.addWidget(self.btn_play)

        self.btn_pause = QPushButton("❚❚ PAUSE")
        self.btn_pause.clicked.connect(self.pause_requested.emit)
        player_layout.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("■ STOP")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        player_layout.addWidget(self.btn_stop)

        # Progress / Title label
        self.song_title_lbl = QLabel("No MIDI song loaded")
        self.song_title_lbl.setStyleSheet(f"font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        player_layout.addWidget(self.song_title_lbl, 1)

        # Tempo Scaling
        player_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 150)
        self.speed_slider.setValue(100)
        self.speed_lbl = QLabel("1.0x")
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        player_layout.addWidget(self.speed_slider)
        player_layout.addWidget(self.speed_lbl)

        main_layout.addWidget(player_group)

        # -------------------------------------------------------------
        # PIANO ROLL EDITOR
        # -------------------------------------------------------------
        roll_group = QGroupBox("PIANO ROLL EDITOR")
        roll_layout = QVBoxLayout(roll_group)
        roll_layout.setSpacing(6)

        # Toolbar
        roll_tools = QHBoxLayout()
        self.btn_quantize = QPushButton("Quantize Grid (1/8)")
        self.btn_quantize.clicked.connect(self._on_quantize_clicked)
        roll_tools.addWidget(self.btn_quantize)

        self.btn_clear_notes = QPushButton("Clear Notes")
        self.btn_clear_notes.clicked.connect(self._on_clear_notes)
        roll_tools.addWidget(self.btn_clear_notes)

        roll_tools.addStretch()
        roll_tools.addWidget(QLabel("Tip: Double-click grid to add note | Drag note to move | Drag right edge to resize | Right-click note to delete"))
        roll_layout.addLayout(roll_tools)

        # Piano roll widget
        self.piano_roll = PianoRollWidget()
        self.piano_roll.note_clicked.connect(lambda note, vel: self.note_preview_requested.emit(note, vel))
        roll_layout.addWidget(self.piano_roll, 1)

        main_layout.addWidget(roll_group, 1)

    def _on_load_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid *.midi)")
        if path:
            self.load_midi_requested.emit(path)

    def set_song_info(self, title: str, duration_sec: float, tempo: float):
        mins = int(duration_sec // 60)
        secs = int(duration_sec % 60)
        self.song_title_lbl.setText(f"{title} ({mins}:{secs:02d} - {tempo} BPM)")

    def _on_speed_changed(self, val: int):
        mult = val / 100.0
        self.speed_lbl.setText(f"{mult:.1f}x")
        self.tempo_scale_changed.emit(mult)

    def _on_quantize_clicked(self):
        self.piano_roll.quantize_all()

    def _on_clear_notes(self):
        self.piano_roll.clear_all()
