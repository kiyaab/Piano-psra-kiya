"""
KIYA Piano Studio Pro - Multi-Channel Workstation Mixer Page
Provides volume faders, pans, mute, and solo across master and individual tracks.
"""

from typing import Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QSlider, QFrame
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_TEXT_PRIMARY,
    COLOR_BORDER
)
from ui.widgets.knob_slider import ChannelFaderWidget, DialKnob
from ui.widgets.meter_widget import StereoMeterWidget

class MixerPage(QWidget):
    """8-Channel audio workstation mixer."""

    channel_volume_changed = Signal(str, float) # channel_key, volume
    channel_pan_changed = Signal(str, float)    # channel_key, pan (-1.0 to 1.0)
    channel_mute_toggled = Signal(str, bool)
    channel_solo_toggled = Signal(str, bool)
    master_volume_changed = Signal(float)

    CHANNELS = [
        ("right1", "Right 1", 1.0),
        ("right2", "Right 2", 0.70),
        ("left", "Left Split", 0.85),
        ("drums", "Drums", 0.85),
        ("bass", "Bass", 0.85),
        ("chords", "Chords", 0.75),
        ("phrase", "Phrase", 0.70),
        ("song", "Song Play", 0.80),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # -------------------------------------------------------------
        # Individual Channel Strips
        # -------------------------------------------------------------
        strips_group = QGroupBox("CHANNELS")
        strips_layout = QHBoxLayout(strips_group)
        strips_layout.setSpacing(10)

        self.faders: Dict[str, ChannelFaderWidget] = {}
        self.pans: Dict[str, DialKnob] = {}

        for key, name, default_vol in self.CHANNELS:
            channel_col = QVBoxLayout()
            channel_col.setSpacing(4)

            # Pan Knob
            pan_dial = DialKnob(title="PAN", min_val=-1.0, max_val=1.0, default_val=0.0)
            pan_dial.valueChanged.connect(lambda val, k=key: self.channel_pan_changed.emit(k, val))
            channel_col.addWidget(pan_dial, 0, Qt.AlignmentFlag.AlignHCenter)
            self.pans[key] = pan_dial

            # Channel Fader
            fader = ChannelFaderWidget(channel_name=name, default_vol=default_vol)
            fader.volumeChanged.connect(lambda vol, k=key: self.channel_volume_changed.emit(k, vol))
            fader.muteToggled.connect(lambda mute, k=key: self.channel_mute_toggled.emit(k, mute))
            fader.soloToggled.connect(lambda solo, k=key: self.channel_solo_toggled.emit(k, solo))
            channel_col.addWidget(fader)
            self.faders[key] = fader

            strips_layout.addLayout(channel_col)

        main_layout.addWidget(strips_group, 6)

        # -------------------------------------------------------------
        # Master Output Strip with Stereo Level Meter
        # -------------------------------------------------------------
        master_group = QGroupBox("MASTER OUTPUT")
        master_layout = QVBoxLayout(master_group)
        master_layout.setSpacing(8)

        # Stereo VU Meters
        self.meter_widget = StereoMeterWidget()
        master_layout.addWidget(self.meter_widget, 1)

        # Master Fader
        master_fader_layout = QVBoxLayout()
        self.master_slider = QSlider(Qt.Orientation.Vertical)
        self.master_slider.setRange(0, 127)
        self.master_slider.setValue(108)
        self.master_slider.valueChanged.connect(self._on_master_slider_changed)
        master_fader_layout.addWidget(self.master_slider, 1, Qt.AlignmentFlag.AlignHCenter)

        self.master_lbl = QLabel("85%")
        self.master_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        master_fader_layout.addWidget(self.master_lbl)
        master_layout.addLayout(master_fader_layout, 2)

        main_layout.addWidget(master_group, 2)

    def _on_master_slider_changed(self, val: int):
        normalized = val / 127.0
        self.master_lbl.setText(f"{int(normalized * 100)}%")
        self.master_volume_changed.emit(normalized)

    def update_meters(self, left: float, right: float):
        self.meter_widget.set_levels(left, right)
