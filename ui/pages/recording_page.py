"""
KIYA Piano Studio Pro - Performance Recording Studio Page
Supports MIDI multi-track recording, direct broadcast-quality WAV recording,
take playback, and file exporting.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QCheckBox, QListWidget, QFileDialog, QMessageBox
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_ERROR,
    COLOR_SUCCESS,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)

class RecordingPage(QWidget):
    """Recording studio page for MIDI and WAV captures."""

    start_recording_requested = Signal(str, bool) # mode ("midi" or "wav"), count_in
    pause_recording_requested = Signal()
    resume_recording_requested = Signal()
    stop_recording_requested = Signal()
    play_take_requested = Signal(int) # take_idx
    export_take_requested = Signal(int, str) # take_idx, filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.elapsed_seconds = 0.0

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # LEFT COLUMN: Recording Setup & Transport Controls
        # -------------------------------------------------------------
        control_group = QGroupBox("RECORDING CONTROLS")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(12)

        # Mode Selection
        mode_box = QHBoxLayout()
        mode_box.addWidget(QLabel("Recording Mode:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItem("MIDI Performance (.mid)", "midi")
        self.combo_mode.addItem("Direct Master Audio (.wav)", "wav")
        mode_box.addWidget(self.combo_mode)
        control_layout.addLayout(mode_box)

        # Options
        self.chk_count_in = QCheckBox("1-Bar Count-In before recording")
        self.chk_count_in.setChecked(True)
        control_layout.addWidget(self.chk_count_in)

        # Time counter display
        self.time_lbl = QLabel("00:00.0")
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_lbl.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {COLOR_TEXT_PRIMARY}; background-color: #12151B; padding: 12px; border-radius: 8px;")
        control_layout.addWidget(self.time_lbl)

        # Transport buttons
        btn_box = QHBoxLayout()
        self.btn_rec = QPushButton("● RECORD")
        self.btn_rec.setCheckable(True)
        self.btn_rec.setStyleSheet(f"background-color: {COLOR_ERROR}; color: white; font-weight: bold; min-height: 36px;")
        self.btn_rec.clicked.connect(self._on_rec_clicked)
        btn_box.addWidget(self.btn_rec)

        self.btn_pause = QPushButton("❚❚ PAUSE")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        btn_box.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("■ STOP")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        btn_box.addWidget(self.btn_stop)

        control_layout.addLayout(btn_box)

        self.status_lbl = QLabel("Ready to record.")
        self.status_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        control_layout.addWidget(self.status_lbl)
        control_layout.addStretch()

        main_layout.addWidget(control_group, 3)

        # -------------------------------------------------------------
        # RIGHT COLUMN: Recorded Takes & Exporting
        # -------------------------------------------------------------
        takes_group = QGroupBox("RECORDED TAKES")
        takes_layout = QVBoxLayout(takes_group)

        self.takes_list = QListWidget()
        takes_layout.addWidget(self.takes_list)

        takes_btn_box = QHBoxLayout()
        self.btn_play_take = QPushButton("▶ Play Selected")
        self.btn_play_take.clicked.connect(self._on_play_take)
        takes_btn_box.addWidget(self.btn_play_take)

        self.btn_export = QPushButton("💾 Export to File...")
        self.btn_export.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold;")
        self.btn_export.clicked.connect(self._on_export_clicked)
        takes_btn_box.addWidget(self.btn_export)

        self.btn_delete_take = QPushButton("Delete")
        self.btn_delete_take.clicked.connect(self._on_delete_take)
        takes_btn_box.addWidget(self.btn_delete_take)

        takes_layout.addLayout(takes_btn_box)
        main_layout.addWidget(takes_group, 4)

        # Elapsed timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)

    def _on_rec_clicked(self):
        if not self.is_recording:
            mode = self.combo_mode.currentData()
            count_in = self.chk_count_in.isChecked()
            self.is_recording = True
            self.elapsed_seconds = 0.0
            self.btn_rec.setText("RECORDING...")
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.status_lbl.setText(f"Recording {mode.upper()}...")
            self.timer.start(100)
            self.start_recording_requested.emit(mode, count_in)
        else:
            self._on_stop_clicked()

    def _on_pause_clicked(self):
        if self.is_recording:
            if self.btn_pause.text() == "❚❚ PAUSE":
                self.btn_pause.setText("▶ RESUME")
                self.status_lbl.setText("Recording paused.")
                self.timer.stop()
                self.pause_recording_requested.emit()
            else:
                self.btn_pause.setText("❚❚ PAUSE")
                self.status_lbl.setText("Recording resumed...")
                self.timer.start(100)
                self.resume_recording_requested.emit()

    def _on_stop_clicked(self):
        if self.is_recording:
            self.is_recording = False
            self.timer.stop()
            self.btn_rec.setChecked(False)
            self.btn_rec.setText("● RECORD")
            self.btn_pause.setEnabled(False)
            self.btn_pause.setText("❚❚ PAUSE")
            self.btn_stop.setEnabled(False)
            self.status_lbl.setText("Recording completed.")
            self.stop_recording_requested.emit()

    def add_take_item(self, title: str):
        self.takes_list.addItem(title)
        self.takes_list.setCurrentRow(self.takes_list.count() - 1)

    def _on_timer_tick(self):
        self.elapsed_seconds += 0.1
        mins = int(self.elapsed_seconds // 60)
        secs = int(self.elapsed_seconds % 60)
        tenths = int((self.elapsed_seconds * 10) % 10)
        self.time_lbl.setText(f"{mins:02d}:{secs:02d}.{tenths}")

    def _on_play_take(self):
        row = self.takes_list.currentRow()
        if row >= 0:
            self.play_take_requested.emit(row)

    def _on_export_clicked(self):
        row = self.takes_list.currentRow()
        if row < 0:
            QMessageBox.information(self, "Export", "Please select a take to export.")
            return

        mode = self.combo_mode.currentData()
        if mode == "midi":
            path, _ = QFileDialog.getSaveFileName(self, "Export MIDI File", "take.mid", "MIDI Files (*.mid)")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Export Audio File", "take.wav", "WAV Audio Files (*.wav)")

        if path:
            self.export_take_requested.emit(row, path)

    def _on_delete_take(self):
        row = self.takes_list.currentRow()
        if row >= 0:
            self.takes_list.takeItem(row)
