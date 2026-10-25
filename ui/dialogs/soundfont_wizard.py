"""
KIYA Piano Studio Pro - SoundFont & Library Installation Wizard Dialog
Guides user through detecting FluidSynth DLLs and loading external SoundFonts.
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from app.constants import (
    APP_NAME,
    COLOR_BG,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)
from audio.fluidsynth_backend import FluidSynthBackend

class SoundFontWizardDialog(QDialog):
    """Wizard for FluidSynth and SoundFont configuration."""

    def __init__(self, fluidsynth_backend: FluidSynthBackend, parent=None):
        super().__init__(parent)
        self.fs_backend = fluidsynth_backend
        self.setWindowTitle(f"{APP_NAME} - SoundFont Installation Wizard")
        self.setMinimumSize(540, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title
        title_lbl = QLabel("Sound Library & Synthesizer Setup Wizard")
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            "KIYA Piano Studio Pro includes an internal polyphonic DSP synthesizer and native Windows General MIDI.\n"
            "If you want to use customized SoundFont banks (.sf2 / .sf3) with high-density acoustic samples, "
            "you can configure FluidSynth below."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        # Status Box
        status_frame = QFrame()
        status_frame.setStyleSheet(f"background-color: #161A22; border: 1px solid #2B3342; border-radius: 6px; padding: 12px;")
        sf_layout = QVBoxLayout(status_frame)

        status_color = COLOR_SUCCESS if self.fs_backend.is_available else COLOR_ERROR
        status_text = "FluidSynth Library: INSTALLED & DETECTED" if self.fs_backend.is_available else "FluidSynth Library: NOT FOUND (Using Native Windows MIDI & Built-in DSP)"
        self.lib_status_lbl = QLabel(status_text)
        self.lib_status_lbl.setStyleSheet(f"font-weight: bold; color: {status_color}; font-size: 13px;")
        sf_layout.addWidget(self.lib_status_lbl)

        if not self.fs_backend.is_available:
            info_sub = QLabel(
                "• All 128 GM instruments, piano keys, styles, and drums work out of the box using our native backends!\n"
                "• To enable FluidSynth: place 'fluidsynth.dll' or 'libfluidsynth.dll' in your Windows PATH or project folder."
            )
            info_sub.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            sf_layout.addWidget(info_sub)

        layout.addWidget(status_frame)

        # SoundFont File Selection
        sf_file_box = QHBoxLayout()
        self.sf_path_lbl = QLabel("Active SoundFont: None (Using default synthesis models)")
        self.sf_path_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        sf_file_box.addWidget(self.sf_path_lbl, 1)

        self.btn_browse = QPushButton("Select SF2 File...")
        self.btn_browse.setStyleSheet(f"background-color: {COLOR_ACCENT_BLUE}; color: #101216; font-weight: bold;")
        self.btn_browse.clicked.connect(self._on_browse_soundfont)
        sf_file_box.addWidget(self.btn_browse)
        layout.addLayout(sf_file_box)

        layout.addStretch()

        # Close button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_close = QPushButton("Done / Close")
        self.btn_close.clicked.connect(self.accept)
        btn_box.addWidget(self.btn_close)
        layout.addLayout(btn_box)

    def _on_browse_soundfont(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select General MIDI SoundFont", "", "SoundFont Files (*.sf2 *.sf3)"
        )
        if file_path:
            if not self.fs_backend.is_available:
                QMessageBox.information(
                    self, "SoundFont Selected",
                    f"Selected SoundFont:\n{file_path}\n\n"
                    "Note: FluidSynth native DLL is not currently installed. The application will continue using "
                    "its built-in high-quality real-time DSP synthesizer and Windows GM Wavetable engine."
                )
            else:
                success = self.fs_backend.load_soundfont(file_path)
                if success:
                    QMessageBox.information(self, "Success", f"SoundFont loaded successfully:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to load SoundFont:\n{self.fs_backend.error_message}")
            self.sf_path_lbl.setText(f"Active SoundFont: {os.path.basename(file_path)}")
