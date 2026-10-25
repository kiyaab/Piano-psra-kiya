"""
KIYA Piano Studio Pro - FluidSynth Backend Wrapper
Provides SoundFont loading and rendering if FluidSynth native libraries are installed.
Gracefully detects missing DLLs and supplies diagnostic information for the SoundFont Wizard.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple

class FluidSynthBackend:
    """Wrapper around pyfluidsynth with status detection and fallback."""

    def __init__(self):
        self.is_available = False
        self.is_initialized = False
        self.error_message = ""
        self.fs_instance = None
        self.soundfont_id = -1
        self.soundfont_path = ""
        self._check_availability()

    def _check_availability(self):
        """Check if fluidsynth library is accessible on the system."""
        try:
            import fluidsynth
            self.is_available = True
            self.error_message = ""
        except Exception as e:
            self.is_available = False
            self.error_message = str(e)

    def initialize(self, soundfont_path: Optional[str] = None, sample_rate: int = 44100) -> bool:
        """Attempt to initialize FluidSynth engine and load SoundFont."""
        self._check_availability()
        if not self.is_available:
            return False

        try:
            import fluidsynth
            self.fs_instance = fluidsynth.Synth(samplerate=float(sample_rate))
            # Direct audio driver (e.g. dsound or wasapi)
            self.fs_instance.start(driver="dsound")

            if soundfont_path and os.path.exists(soundfont_path):
                self.load_soundfont(soundfont_path)

            self.is_initialized = True
            return True
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"FluidSynth initialization failed: {e}"
            return False

    def load_soundfont(self, sf2_path: str) -> bool:
        """Load an SF2 or SF3 SoundFont file."""
        if not self.fs_instance or not os.path.exists(sf2_path):
            return False
        try:
            sfid = self.fs_instance.sfload(sf2_path)
            if sfid >= 0:
                self.soundfont_id = sfid
                self.soundfont_path = sf2_path
                # Bind all 16 channels to soundfont
                for ch in range(16):
                    self.fs_instance.sfont_select(ch, sfid)
                return True
        except Exception as e:
            self.error_message = f"Failed to load SoundFont: {e}"
        return False

    def note_on(self, channel: int, note: int, velocity: int):
        if self.fs_instance and self.is_initialized:
            try:
                self.fs_instance.noteon(channel, note, velocity)
            except Exception:
                pass

    def note_off(self, channel: int, note: int):
        if self.fs_instance and self.is_initialized:
            try:
                self.fs_instance.noteoff(channel, note)
            except Exception:
                pass

    def program_change(self, channel: int, program: int):
        if self.fs_instance and self.is_initialized:
            try:
                self.fs_instance.program_change(channel, program)
            except Exception:
                pass

    def control_change(self, channel: int, control: int, value: int):
        if self.fs_instance and self.is_initialized:
            try:
                self.fs_instance.cc(channel, control, value)
            except Exception:
                pass

    def pitch_bend(self, channel: int, pitch: int):
        if self.fs_instance and self.is_initialized:
            try:
                self.fs_instance.pitch_bend(channel, pitch)
            except Exception:
                pass

    def close(self):
        if self.fs_instance:
            try:
                self.fs_instance.delete()
            except Exception:
                pass
            self.fs_instance = None
            self.is_initialized = False
