"""
KIYA Piano Studio Pro - Practice & Learning Tools Page
Provides Metronome, Chord Encyclopedia, Musical Scales, and Interactive Note Practice.
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QSlider, QCheckBox, QFrame
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    NOTE_NAMES
)
from practice.chord_library import ChordLibrary
from practice.exercises import ScaleLibrary, NotePracticeTrainer

class PracticePage(QWidget):
    """Practice and musical learning tools screen."""

    metronome_start_stop_requested = Signal(bool) # is_running
    metronome_tempo_changed = Signal(int)
    metronome_time_sig_changed = Signal(int, int) # num, den
    metronome_sound_toggled = Signal(bool)
    play_chord_requested = Signal(list) # list of midi notes
    highlight_keys_requested = Signal(list) # list of midi notes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainer = NotePracticeTrainer()
        self.is_metronome_running = False

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # 1. METRONOME CONTROLLER
        # -------------------------------------------------------------
        metro_group = QGroupBox("METRONOME")
        metro_layout = QVBoxLayout(metro_group)
        metro_layout.setSpacing(10)

        # Tempo Row
        t_row = QHBoxLayout()
        t_row.addWidget(QLabel("Tempo:"))
        self.metro_slider = QSlider(Qt.Orientation.Horizontal)
        self.metro_slider.setRange(40, 240)
        self.metro_slider.setValue(120)
        self.metro_bpm_lbl = QLabel("120 BPM")
        self.metro_slider.valueChanged.connect(self._on_metro_slider)
        t_row.addWidget(self.metro_slider)
        t_row.addWidget(self.metro_bpm_lbl)
        metro_layout.addLayout(t_row)

        # Time signature & Options
        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Time Signature:"))
        self.combo_time_sig = QComboBox()
        self.combo_time_sig.addItem("4/4 Standard", (4, 4))
        self.combo_time_sig.addItem("3/4 Waltz", (3, 4))
        self.combo_time_sig.addItem("2/4 March", (2, 4))
        self.combo_time_sig.addItem("6/8 Compound", (6, 8))
        self.combo_time_sig.currentIndexChanged.connect(self._on_time_sig_changed)
        opt_row.addWidget(self.combo_time_sig)

        self.chk_sound = QCheckBox("Audible Click")
        self.chk_sound.setChecked(True)
        self.chk_sound.toggled.connect(self.metronome_sound_toggled.emit)
        opt_row.addWidget(self.chk_sound)
        metro_layout.addLayout(opt_row)

        # Start / Stop Button
        self.btn_metro_toggle = QPushButton("▶ START METRONOME")
        self.btn_metro_toggle.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold; min-height: 32px;")
        self.btn_metro_toggle.clicked.connect(self._toggle_metronome)
        metro_layout.addWidget(self.btn_metro_toggle)
        metro_layout.addStretch()

        main_layout.addWidget(metro_group, 0, 0)

        # -------------------------------------------------------------
        # 2. CHORD ENCYCLOPEDIA
        # -------------------------------------------------------------
        chord_group = QGroupBox("CHORD ENCYCLOPEDIA")
        chord_layout = QVBoxLayout(chord_group)
        chord_layout.setSpacing(8)

        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Root:"))
        self.combo_chord_root = QComboBox()
        for n in NOTE_NAMES:
            self.combo_chord_root.addItem(n)
        self.combo_chord_root.currentIndexChanged.connect(self._update_chord_details)
        sel_row.addWidget(self.combo_chord_root)

        sel_row.addWidget(QLabel("Type:"))
        self.combo_chord_type = QComboBox()
        for ct in ChordLibrary.get_chord_types():
            self.combo_chord_type.addItem(ct)
        self.combo_chord_type.currentIndexChanged.connect(self._update_chord_details)
        sel_row.addWidget(self.combo_chord_type)
        chord_layout.addLayout(sel_row)

        self.chord_name_lbl = QLabel("C Major")
        self.chord_name_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        chord_layout.addWidget(self.chord_name_lbl)

        self.chord_notes_lbl = QLabel("Notes: C - E - G | Formula: 1 - 3 - 5")
        self.chord_notes_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        chord_layout.addWidget(self.chord_notes_lbl)

        chord_btn_row = QHBoxLayout()
        self.btn_play_chord = QPushButton("♫ Audition Chord")
        self.btn_play_chord.clicked.connect(self._on_play_chord)
        chord_btn_row.addWidget(self.btn_play_chord)

        self.btn_highlight_chord = QPushButton("Highlight on Keys")
        self.btn_highlight_chord.clicked.connect(self._on_highlight_chord)
        chord_btn_row.addWidget(self.btn_highlight_chord)
        chord_layout.addLayout(chord_btn_row)
        chord_layout.addStretch()

        main_layout.addWidget(chord_group, 0, 1)

        # -------------------------------------------------------------
        # 3. SCALE EXPLORER
        # -------------------------------------------------------------
        scale_group = QGroupBox("MUSICAL SCALES EXPLORER")
        scale_layout = QVBoxLayout(scale_group)
        scale_layout.setSpacing(8)

        scale_sel_row = QHBoxLayout()
        scale_sel_row.addWidget(QLabel("Root:"))
        self.combo_scale_root = QComboBox()
        for n in NOTE_NAMES:
            self.combo_scale_root.addItem(n)
        self.combo_scale_root.currentIndexChanged.connect(self._update_scale_details)
        scale_sel_row.addWidget(self.combo_scale_root)

        scale_sel_row.addWidget(QLabel("Scale:"))
        self.combo_scale_type = QComboBox()
        for st in ScaleLibrary.get_scale_names():
            self.combo_scale_type.addItem(st)
        self.combo_scale_type.currentIndexChanged.connect(self._update_scale_details)
        scale_sel_row.addWidget(self.combo_scale_type)
        scale_layout.addLayout(scale_sel_row)

        self.scale_title_lbl = QLabel("C Major (Ionian)")
        self.scale_title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_ACCENT_BLUE};")
        scale_layout.addWidget(self.scale_title_lbl)

        self.scale_notes_lbl = QLabel("C - D - E - F - G - A - B - C")
        self.scale_notes_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        scale_layout.addWidget(self.scale_notes_lbl)

        self.btn_highlight_scale = QPushButton("Highlight Scale on Piano")
        self.btn_highlight_scale.clicked.connect(self._on_highlight_scale)
        scale_layout.addWidget(self.btn_highlight_scale)
        scale_layout.addStretch()

        main_layout.addWidget(scale_group, 1, 0)

        # -------------------------------------------------------------
        # 4. INTERACTIVE NOTE RECOGNITION CHALLENGE
        # -------------------------------------------------------------
        quiz_group = QGroupBox("INTERACTIVE NOTE RECOGNITION CHALLENGE")
        quiz_layout = QVBoxLayout(quiz_group)
        quiz_layout.setSpacing(10)

        # Target Display Box
        target_box = QHBoxLayout()
        target_box.addWidget(QLabel("PLAY THIS NOTE:"))
        self.target_note_lbl = QLabel("C4 (Middle C)")
        self.target_note_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_ACCENT_ORANGE}; background-color: #12151B; padding: 6px 14px; border-radius: 6px;")
        target_box.addWidget(self.target_note_lbl)
        target_box.addStretch()
        quiz_layout.addLayout(target_box)

        # Score & Streak stats
        self.stats_lbl = QLabel("Score: 0 | Streak: 0 (Best: 0) | Accuracy: 0%")
        self.stats_lbl.setStyleSheet(f"font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        quiz_layout.addWidget(self.stats_lbl)

        self.feedback_lbl = QLabel("Play notes using virtual keyboard, computer keys (Z-M), or MIDI keyboard!")
        self.feedback_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        quiz_layout.addWidget(self.feedback_lbl)

        quiz_btn_row = QHBoxLayout()
        self.btn_new_challenge = QPushButton("Next Note Challenge")
        self.btn_new_challenge.clicked.connect(self._new_challenge)
        quiz_btn_row.addWidget(self.btn_new_challenge)

        self.btn_reset_quiz = QPushButton("Reset Stats")
        self.btn_reset_quiz.clicked.connect(self._reset_quiz)
        quiz_btn_row.addWidget(self.btn_reset_quiz)
        quiz_layout.addLayout(quiz_btn_row)
        quiz_layout.addStretch()

        main_layout.addWidget(quiz_group, 1, 1)

        self._update_chord_details()
        self._update_scale_details()

    def _on_metro_slider(self, val: int):
        self.metro_bpm_lbl.setText(f"{val} BPM")
        self.metronome_tempo_changed.emit(val)

    def _on_time_sig_changed(self):
        num, den = self.combo_time_sig.currentData()
        self.metronome_time_sig_changed.emit(num, den)

    def _toggle_metronome(self):
        self.is_metronome_running = not self.is_metronome_running
        if self.is_metronome_running:
            self.btn_metro_toggle.setText("■ STOP METRONOME")
            self.btn_metro_toggle.setStyleSheet(f"background-color: {COLOR_ERROR}; color: white; font-weight: bold; min-height: 32px;")
        else:
            self.btn_metro_toggle.setText("▶ START METRONOME")
            self.btn_metro_toggle.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold; min-height: 32px;")
        self.metronome_start_stop_requested.emit(self.is_metronome_running)

    def _update_chord_details(self):
        root = self.combo_chord_root.currentIndex()
        ctype = self.combo_chord_type.currentText()
        info = ChordLibrary.get_chord_info(root, ctype)
        self.chord_name_lbl.setText(f"{info['root_name']} {info['chord_type']}")
        self.chord_notes_lbl.setText(f"Notes: {info['spelling']} | Formula: {info['formula']}")

    def _on_play_chord(self):
        root = self.combo_chord_root.currentIndex()
        ctype = self.combo_chord_type.currentText()
        info = ChordLibrary.get_chord_info(root, ctype)
        self.play_chord_requested.emit(info["midi_notes"])

    def _on_highlight_chord(self):
        root = self.combo_chord_root.currentIndex()
        ctype = self.combo_chord_type.currentText()
        info = ChordLibrary.get_chord_info(root, ctype)
        self.highlight_keys_requested.emit(info["midi_notes"])

    def _update_scale_details(self):
        root = self.combo_scale_root.currentIndex()
        sname = self.combo_scale_type.currentText()
        info = ScaleLibrary.get_scale_notes(root, sname)
        self.scale_title_lbl.setText(info["display_name"])
        self.scale_notes_lbl.setText(f"Notes: {' - '.join(info['note_names'])} | Formula: {info['formula']}")

    def _on_highlight_scale(self):
        root = self.combo_scale_root.currentIndex()
        sname = self.combo_scale_type.currentText()
        info = ScaleLibrary.get_scale_notes(root, sname)
        self.highlight_keys_requested.emit(info["midi_notes"])

    def _new_challenge(self):
        note = self.trainer.new_challenge()
        self.target_note_lbl.setText(self.trainer.get_target_name())
        self.feedback_lbl.setText("Play the note shown above!")
        self.feedback_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")

    def evaluate_played_note(self, note: int):
        """Called when a key is played to check practice accuracy."""
        is_correct, msg = self.trainer.evaluate_note(note)
        pct = int((self.trainer.score / max(1, self.trainer.attempts * 10)) * 100)
        self.stats_lbl.setText(f"Score: {self.trainer.score} | Streak: {self.trainer.current_streak} (Best: {self.trainer.best_streak}) | Accuracy: {pct}%")
        self.feedback_lbl.setText(msg)
        self.feedback_lbl.setStyleSheet(f"color: {COLOR_SUCCESS if is_correct else COLOR_ERROR}; font-weight: bold;")
        if is_correct:
            self._new_challenge()

    def _reset_quiz(self):
        self.trainer.reset_stats()
        self.stats_lbl.setText("Score: 0 | Streak: 0 (Best: 0) | Accuracy: 0%")
        self.feedback_lbl.setText("Ready for challenge!")
        self.feedback_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        self._new_challenge()
