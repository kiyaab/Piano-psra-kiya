"""
KIYA Piano Studio Pro - Configuration & Persistence Manager
Stores user preferences, audio device settings, voice mappings, and window states.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict
from app.constants import (
    DEFAULT_SAMPLE_RATE,
    DEFAULT_BUFFER_SIZE,
    DEFAULT_SPLIT_POINT,
    APP_NAME
)

class AppConfig:
    """Manages application persistent configuration with safe atomic JSON writes."""

    _DEFAULT_CONFIG: Dict[str, Any] = {
        # Audio configuration
        "audio_backend": "hybrid",  # "hybrid", "windows_midi", "sounddevice_dsp", "fluidsynth"
        "audio_device_index": None,
        "sample_rate": DEFAULT_SAMPLE_RATE,
        "buffer_size": DEFAULT_BUFFER_SIZE,
        "soundfont_path": "",
        "master_volume": 0.85,
        "polyphony_limit": 64,

        # MIDI configuration
        "midi_input_port": "",
        "midi_output_port": "Microsoft GS Wavetable Synth 0",
        "midi_thru": False,

        # Performance setup
        "right1_voice": 0,       # Acoustic Grand Piano
        "right1_volume": 1.0,
        "right1_octave": 0,
        "right1_pan": 0.0,
        "right1_mute": False,

        "layer_enabled": False,
        "right2_voice": 48,      # String Ensemble 1
        "right2_volume": 0.70,
        "right2_octave": 0,
        "right2_pan": 0.0,
        "right2_mute": False,

        "split_enabled": False,
        "split_point": DEFAULT_SPLIT_POINT,
        "left_voice": 32,        # Acoustic Bass
        "left_volume": 0.85,
        "left_octave": 0,
        "left_pan": 0.0,
        "left_mute": False,

        "keyboard_transpose": 0,
        "master_tune_cents": 0,
        "velocity_curve": "linear",  # "linear", "soft", "hard", "fixed"
        "fixed_velocity_val": 100,

        # Arranger & Styles
        "current_style": "Pop Groove",
        "tempo": 120,
        "accompaniment_enabled": True,
        "chord_recognition_mode": "full",  # "full" or "simplified"
        "sync_start": False,
        "style_volume": 0.80,
        "drums_volume": 0.85,
        "bass_volume": 0.85,
        "chords_volume": 0.75,

        # Effects & Mixer
        "reverb_send": 0.30,
        "chorus_send": 0.15,
        "delay_send": 0.0,
        "eq_low_gain": 0.0,
        "eq_mid_gain": 0.0,
        "eq_high_gain": 0.0,

        # Visuals & UI
        "theme": "dark",
        "show_note_names": True,
        "show_key_shortcuts": True,
        "keyboard_zoom": 1.0,
        "window_width": 1280,
        "window_height": 820,
        "last_registration_bank": "A",
        "recent_voices": [0, 4, 16, 24, 32, 40, 48, 56],
        "favorite_voices": [0, 4, 16, 48]
    }

    def __init__(self, config_path: str = None):
        if config_path:
            self.file_path = Path(config_path)
        else:
            # Prefer AppData/Roaming on Windows
            app_data = os.environ.get("APPDATA")
            if app_data:
                config_dir = Path(app_data) / APP_NAME.replace(" ", "_")
            else:
                config_dir = Path.home() / f".{APP_NAME.replace(' ', '_').lower()}"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.file_path = config_dir / "config.json"

        self.data: Dict[str, Any] = dict(self._DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        """Load configuration from JSON file safely."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self.data.update(saved)
            except Exception as e:
                print(f"[AppConfig] Warning: Failed to load config from {self.file_path}: {e}")

    def save(self) -> bool:
        """Atomic write configuration to JSON file."""
        tmp_path = self.file_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            if self.file_path.exists():
                self.file_path.unlink()
            tmp_path.rename(self.file_path)
            return True
        except Exception as e:
            print(f"[AppConfig] Error: Failed to save config to {self.file_path}: {e}")
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default if default is not None else self._DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def reset_to_defaults(self) -> None:
        self.data = dict(self._DEFAULT_CONFIG)
        self.save()
