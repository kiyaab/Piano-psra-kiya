"""
KIYA Piano Studio Pro - Settings & Configuration Page
Audio backend selection, buffer sizes, MIDI device routing, latency testing, and SoundFont wizard.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QSlider, QMessageBox, QFrame
)
from app.constants import (
    SUPPORTED_SAMPLE_RATES,
    SUPPORTED_BUFFER_SIZES,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)
from audio.audio_devices import AudioDeviceManager
from midi.device_manager import MidiDeviceManager

class SettingsPage(QWidget):
    """Audio, MIDI, and System Configuration Page."""

    audio_config_changed = Signal(int, int, object) # sample_rate, buffer_size, device_index
    audio_backend_changed = Signal(str)            # backend_name
    midi_input_changed = Signal(str)               # port_name
    midi_output_changed = Signal(str)              # port_name
    play_test_tone_requested = Signal()
    velocity_curve_changed = Signal(str, int)      # curve_type, fixed_val
    open_soundfont_wizard_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # 1. AUDIO ENGINE CONFIGURATION
        # -------------------------------------------------------------
        audio_group = QGroupBox("AUDIO ENGINE & LATENCY SETUP")
        audio_layout = QGridLayout(audio_group)
        audio_layout.setSpacing(10)

        # Engine Mode
        audio_layout.addWidget(QLabel("Synthesis Engine:"), 0, 0)
        self.combo_backend = QComboBox()
        self.combo_backend.addItem("Hybrid (Windows Native MIDI + Real-Time DSP Audio)", "hybrid")
        self.combo_backend.addItem("Windows GS Wavetable MIDI (Zero Latency / 0% CPU)", "windows_midi")
        self.combo_backend.addItem("Real-Time Software DSP Synthesizer (NumPy/SoundDevice)", "dsp")
        self.combo_backend.addItem("FluidSynth SoundFont Engine (External SF2)", "fluidsynth")
        self.combo_backend.currentIndexChanged.connect(self._on_backend_changed)
        audio_layout.addWidget(self.combo_backend, 0, 1)

        # Audio Output Device
        audio_layout.addWidget(QLabel("Output Device:"), 1, 0)
        self.combo_audio_dev = QComboBox()
        self._populate_audio_devices()
        self.combo_audio_dev.currentIndexChanged.connect(self._on_audio_setting_changed)
        audio_layout.addWidget(self.combo_audio_dev, 1, 1)

        # Sample Rate
        audio_layout.addWidget(QLabel("Sample Rate:"), 2, 0)
        self.combo_sample_rate = QComboBox()
        for sr in SUPPORTED_SAMPLE_RATES:
            self.combo_sample_rate.addItem(f"{sr} Hz", sr)
        self.combo_sample_rate.setCurrentText("44100 Hz")
        self.combo_sample_rate.currentIndexChanged.connect(self._on_audio_setting_changed)
        audio_layout.addWidget(self.combo_sample_rate, 2, 1)

        # Buffer Size
        audio_layout.addWidget(QLabel("Buffer Size (Latency):"), 3, 0)
        self.combo_buffer_size = QComboBox()
        for bs in SUPPORTED_BUFFER_SIZES:
            self.combo_buffer_size.addItem(f"{bs} frames (~{round((bs / 44100.0) * 1000, 1)} ms)", bs)
        self.combo_buffer_size.setCurrentText("512 frames (~11.6 ms)")
        self.combo_buffer_size.currentIndexChanged.connect(self._on_audio_setting_changed)
        audio_layout.addWidget(self.combo_buffer_size, 3, 1)

        # Latency Estimate & Test Tone
        self.latency_lbl = QLabel("Estimated Latency: ~18.2 ms")
        self.latency_lbl.setStyleSheet(f"color: {COLOR_ACCENT_BLUE}; font-weight: bold;")
        audio_layout.addWidget(self.latency_lbl, 4, 0)

        self.btn_test_tone = QPushButton("♫ Play Test Note (Middle C)")
        self.btn_test_tone.clicked.connect(self.play_test_tone_requested.emit)
        audio_layout.addWidget(self.btn_test_tone, 4, 1)

        main_layout.addWidget(audio_group, 0, 0)

        # -------------------------------------------------------------
        # 2. MIDI DEVICE MANAGEMENT
        # -------------------------------------------------------------
        midi_group = QGroupBox("MIDI HARDWARE & PORTS")
        midi_layout = QGridLayout(midi_group)
        midi_layout.setSpacing(10)

        # MIDI Input Port
        midi_layout.addWidget(QLabel("MIDI Input Keyboard:"), 0, 0)
        self.combo_midi_in = QComboBox()
        self._populate_midi_ports()
        self.combo_midi_in.currentIndexChanged.connect(self._on_midi_in_changed)
        midi_layout.addWidget(self.combo_midi_in, 0, 1)

        # MIDI Output Port
        midi_layout.addWidget(QLabel("MIDI Output Synth:"), 1, 0)
        self.combo_midi_out = QComboBox()
        self._populate_midi_outputs()
        self.combo_midi_out.currentIndexChanged.connect(self._on_midi_out_changed)
        midi_layout.addWidget(self.combo_midi_out, 1, 1)

        # Refresh Ports button
        self.btn_refresh_midi = QPushButton("🔄 Refresh Device List")
        self.btn_refresh_midi.clicked.connect(self._on_refresh_ports)
        midi_layout.addWidget(self.btn_refresh_midi, 2, 0)

        self.midi_status_lbl = QLabel("Status: Ready. Virtual keyboard operational.")
        self.midi_status_lbl.setStyleSheet(f"color: {COLOR_SUCCESS};")
        midi_layout.addWidget(self.midi_status_lbl, 2, 1)

        main_layout.addWidget(midi_group, 0, 1)

        # -------------------------------------------------------------
        # 3. KEYBOARD RESPONSE & VELOCITY CURVE
        # -------------------------------------------------------------
        kb_group = QGroupBox("KEYBOARD TOUCH & VELOCITY RESPONSE")
        kb_layout = QGridLayout(kb_group)
        kb_layout.setSpacing(10)

        kb_layout.addWidget(QLabel("Touch Response Curve:"), 0, 0)
        self.combo_velocity = QComboBox()
        self.combo_velocity.addItem("Linear (Standard Workstation)", "linear")
        self.combo_velocity.addItem("Soft (Easier Forte / High Velocity)", "soft")
        self.combo_velocity.addItem("Hard (Wider Dynamic Range / Heavy Touch)", "hard")
        self.combo_velocity.addItem("Fixed (Organ / Synth Style Constant Velocity)", "fixed")
        self.combo_velocity.currentIndexChanged.connect(self._on_velocity_curve_changed)
        kb_layout.addWidget(self.combo_velocity, 0, 1)

        kb_layout.addWidget(QLabel("Fixed Velocity Level:"), 1, 0)
        self.fixed_vel_slider = QSlider(Qt.Orientation.Horizontal)
        self.fixed_vel_slider.setRange(1, 127)
        self.fixed_vel_slider.setValue(100)
        self.fixed_vel_slider.setEnabled(False)
        self.fixed_vel_lbl = QLabel("100")
        self.fixed_vel_slider.valueChanged.connect(lambda v: (self.fixed_vel_lbl.setText(str(v)), self._on_velocity_curve_changed()))
        h_box = QHBoxLayout()
        h_box.addWidget(self.fixed_vel_slider)
        h_box.addWidget(self.fixed_vel_lbl)
        kb_layout.addLayout(h_box, 1, 1)

        main_layout.addWidget(kb_group, 1, 0)

        # -------------------------------------------------------------
        # 4. SOUNDFONT & ADVANCED ENGINE WIZARD
        # -------------------------------------------------------------
        sf_group = QGroupBox("EXTERNAL SOUNDFONT & DEPENDENCY WIZARD")
        sf_layout = QVBoxLayout(sf_group)
        sf_layout.setSpacing(10)

        sf_info = QLabel(
            "KIYA Piano Studio Pro uses built-in multi-timbral synthesis and Windows native General MIDI.\n"
            "You can optionally load external SoundFont libraries (.sf2/.sf3) or install FluidSynth."
        )
        sf_info.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        sf_layout.addWidget(sf_info)

        self.btn_sf_wizard = QPushButton("🧙 Launch SoundFont Setup Wizard...")
        self.btn_sf_wizard.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold; min-height: 34px;")
        self.btn_sf_wizard.clicked.connect(self.open_soundfont_wizard_requested.emit)
        sf_layout.addWidget(self.btn_sf_wizard)
        sf_layout.addStretch()

        main_layout.addWidget(sf_group, 1, 1)

    def _populate_audio_devices(self):
        self.combo_audio_dev.clear()
        self.combo_audio_dev.addItem("System Default Output", None)
        devices = AudioDeviceManager.get_output_devices()
        for d in devices:
            self.combo_audio_dev.addItem(d['name'], d['index'])

    def _populate_midi_ports(self):
        self.combo_midi_in.clear()
        self.combo_midi_in.addItem("None (Virtual / Computer Keyboard Only)", "")
        inputs = MidiDeviceManager.get_input_devices()
        for p in inputs:
            self.combo_midi_in.addItem(f"🎹 {p}", p)

    def _populate_midi_outputs(self):
        self.combo_midi_out.clear()
        outputs = MidiDeviceManager.get_output_devices()
        for p in outputs:
            self.combo_midi_out.addItem(f"🔊 {p}", p)

    def _on_refresh_ports(self):
        self._populate_audio_devices()
        self._populate_midi_ports()
        self._populate_midi_outputs()
        QMessageBox.information(self, "Devices", "Device lists refreshed.")

    def _on_backend_changed(self):
        backend = self.combo_backend.currentData()
        self.audio_backend_changed.emit(backend)

    def _on_audio_setting_changed(self):
        sr = self.combo_sample_rate.currentData()
        bs = self.combo_buffer_size.currentData()
        dev = self.combo_audio_dev.currentData()
        lat = AudioDeviceManager.estimate_latency_ms(bs, sr, dev)
        self.latency_lbl.setText(f"Estimated Latency: ~{lat} ms")
        self.audio_config_changed.emit(sr, bs, dev)

    def _on_midi_in_changed(self):
        port = self.combo_midi_in.currentData()
        self.midi_input_changed.emit(port)

    def _on_midi_out_changed(self):
        port = self.combo_midi_out.currentData()
        self.midi_output_changed.emit(port)

    def _on_velocity_curve_changed(self):
        curve = self.combo_velocity.currentData()
        self.fixed_vel_slider.setEnabled(curve == "fixed")
        fixed_val = self.fixed_vel_slider.value()
        self.velocity_curve_changed.emit(curve, fixed_val)
