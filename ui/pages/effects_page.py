"""
KIYA Piano Studio Pro - Master DSP Audio Effects Page
Controls for 3-Band Parametric EQ, Stereo Reverb, Stereo Chorus, Stereo Delay, and Limiter.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QSlider, QFrame
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)
from ui.widgets.knob_slider import DialKnob

class EffectsPage(QWidget):
    """Audio effects processing control page."""

    eq_changed = Signal(str, float)     # "low", "mid", "high", gain_db (-12.0 to +12.0)
    reverb_changed = Signal(float, float, float) # room_size, damp, mix
    chorus_changed = Signal(float, float, float) # rate, depth, mix
    delay_changed = Signal(float, float, float)  # time, feedback, mix

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # 1. 3-BAND MASTER EQUALIZER
        # -------------------------------------------------------------
        eq_group = QGroupBox("3-BAND MASTER PARAMETRIC EQUALIZER")
        eq_layout = QHBoxLayout(eq_group)
        eq_layout.setSpacing(16)

        # Low Shelf (220 Hz)
        eq_layout.addWidget(self._create_eq_band("LOW SHELF", "220 Hz", "low"))
        eq_layout.addWidget(self._create_eq_band("MID PEAK", "1.2 kHz", "mid"))
        eq_layout.addWidget(self._create_eq_band("HIGH SHELF", "5.5 kHz", "high"))

        main_layout.addWidget(eq_group, 0, 0)

        # -------------------------------------------------------------
        # 2. STEREO REVERBERATOR
        # -------------------------------------------------------------
        rev_group = QGroupBox("SCHROEDER STEREO REVERBERATOR")
        rev_layout = QHBoxLayout(rev_group)

        self.rev_room = DialKnob(title="ROOM SIZE", min_val=0.1, max_val=0.95, default_val=0.75)
        self.rev_damp = DialKnob(title="DAMPING", min_val=0.0, max_val=0.8, default_val=0.25)
        self.rev_mix = DialKnob(title="WET / DRY", min_val=0.0, max_val=1.0, default_val=0.30)

        self.rev_room.valueChanged.connect(self._emit_reverb)
        self.rev_damp.valueChanged.connect(self._emit_reverb)
        self.rev_mix.valueChanged.connect(self._emit_reverb)

        rev_layout.addWidget(self.rev_room)
        rev_layout.addWidget(self.rev_damp)
        rev_layout.addWidget(self.rev_mix)
        main_layout.addWidget(rev_group, 0, 1)

        # -------------------------------------------------------------
        # 3. STEREO CHORUS / FLANGER
        # -------------------------------------------------------------
        chorus_group = QGroupBox("STEREO MODULATION CHORUS")
        chorus_layout = QHBoxLayout(chorus_group)

        self.chorus_rate = DialKnob(title="RATE (Hz)", min_val=0.2, max_val=5.0, default_val=1.2)
        self.chorus_depth = DialKnob(title="DEPTH", min_val=0.001, max_val=0.012, default_val=0.0035)
        self.chorus_mix = DialKnob(title="WET / DRY", min_val=0.0, max_val=1.0, default_val=0.15)

        self.chorus_rate.valueChanged.connect(self._emit_chorus)
        self.chorus_depth.valueChanged.connect(self._emit_chorus)
        self.chorus_mix.valueChanged.connect(self._emit_chorus)

        chorus_layout.addWidget(self.chorus_rate)
        chorus_layout.addWidget(self.chorus_depth)
        chorus_layout.addWidget(self.chorus_mix)
        main_layout.addWidget(chorus_group, 1, 0)

        # -------------------------------------------------------------
        # 4. STEREO ECHO DELAY & MASTER LIMITER
        # -------------------------------------------------------------
        delay_group = QGroupBox("STEREO ECHO DELAY")
        delay_layout = QHBoxLayout(delay_group)

        self.delay_time = DialKnob(title="TIME (s)", min_val=0.05, max_val=1.0, default_val=0.35)
        self.delay_fb = DialKnob(title="FEEDBACK", min_val=0.0, max_val=0.80, default_val=0.40)
        self.delay_mix = DialKnob(title="WET / DRY", min_val=0.0, max_val=1.0, default_val=0.0)

        self.delay_time.valueChanged.connect(self._emit_delay)
        self.delay_fb.valueChanged.connect(self._emit_delay)
        self.delay_mix.valueChanged.connect(self._emit_delay)

        delay_layout.addWidget(self.delay_time)
        delay_layout.addWidget(self.delay_fb)
        delay_layout.addWidget(self.delay_mix)
        main_layout.addWidget(delay_group, 1, 1)

    def _create_eq_band(self, title: str, freq_str: str, band_key: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        t_lbl = QLabel(title)
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_lbl = QLabel(freq_str)
        f_lbl.setStyleSheet(f"font-size: 10px; color: {COLOR_TEXT_SECONDARY};")
        f_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(t_lbl)
        layout.addWidget(f_lbl)

        slider = QSlider(Qt.Orientation.Vertical)
        slider.setRange(-12, 12)
        slider.setValue(0)
        val_lbl = QLabel("0.0 dB")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def _on_val_changed(val: int):
            val_lbl.setText(f"{val:+d}.0 dB")
            self.eq_changed.emit(band_key, float(val))

        slider.valueChanged.connect(_on_val_changed)
        layout.addWidget(slider, 1, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(val_lbl)
        return widget

    def _emit_reverb(self):
        self.reverb_changed.emit(self.rev_room.value, self.rev_damp.value, self.rev_mix.value)

    def _emit_chorus(self):
        self.chorus_changed.emit(self.chorus_rate.value, self.chorus_depth.value, self.chorus_mix.value)

    def _emit_delay(self):
        self.delay_changed.emit(self.delay_time.value, self.delay_fb.value, self.delay_mix.value)
