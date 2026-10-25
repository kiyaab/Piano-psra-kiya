"""
KIYA Piano Studio Pro - Master Synthesizer Facade
Coordinates DSP Synthesizer, Windows GS Wavetable MIDI Synthesizer, and FluidSynth.
Provides unified note triggering, program changes, pitch bend, controller changes, and panic kill.
"""

from typing import Optional, List, Set, Tuple
from audio.note_manager import NoteManager
from audio.midi_synth import MidiSynth
from audio.dsp_synth import DSPSynthesizer
from audio.fluidsynth_backend import FluidSynthBackend

class SynthesizerFacade:
    """Master instrument synthesizer integrating DSP, Windows GS, and FluidSynth."""

    def __init__(self, sample_rate: int = 44100, midi_out_port: Optional[str] = None):
        self.sample_rate = sample_rate
        self.note_manager = NoteManager()
        self.midi_synth = MidiSynth(midi_out_port)
        self.dsp_synth = DSPSynthesizer(sample_rate=sample_rate)
        self.fluidsynth = FluidSynthBackend()

        # Engine mode: "hybrid" (both MIDI synth & DSP synth active for richest sound & WAV capture),
        # "windows_midi" (only MIDI synth), "dsp" (only DSP synth), "fluidsynth"
        self.engine_mode = "hybrid"

    @property
    def is_connected(self) -> bool:
        return self.midi_synth.is_connected or self.fluidsynth.is_initialized or True

    def set_engine_mode(self, mode: str):
        self.engine_mode = mode.lower()

    def set_program(self, channel: int, program: int):
        """Set instrument voice for channel (0-15)."""
        channel = max(0, min(15, channel))
        program = max(0, min(127, program))
        self.dsp_synth.set_program(channel, program)
        self.midi_synth.program_change(channel, program)
        if self.fluidsynth.is_initialized:
            self.fluidsynth.program_change(channel, program)

    def set_channel_volume(self, channel: int, volume: float):
        """Set volume per channel (0.0 to 1.5)."""
        channel = max(0, min(15, channel))
        self.dsp_synth.set_volume(channel, volume)
        cc_val = int(max(0.0, min(1.0, volume)) * 127)
        self.midi_synth.control_change(channel, 7, cc_val)
        if self.fluidsynth.is_initialized:
            self.fluidsynth.control_change(channel, 7, cc_val)

    def set_channel_pan(self, channel: int, pan: float):
        """Set pan per channel (-1.0 to 1.0)."""
        channel = max(0, min(15, channel))
        self.dsp_synth.set_pan(channel, pan)
        cc_val = int(((pan + 1.0) / 2.0) * 127)
        self.midi_synth.control_change(channel, 10, cc_val)
        if self.fluidsynth.is_initialized:
            self.fluidsynth.control_change(channel, 10, cc_val)

    def note_on(self, channel: int, note: int, velocity: int = 100):
        """Play a note on the designated channel."""
        channel = max(0, min(15, channel))
        note = max(0, min(127, note))
        if velocity <= 0:
            self.note_off(channel, note)
            return

        mapped_vel = self.note_manager.note_on(channel, note, velocity)

        if self.engine_mode in ("hybrid", "windows_midi"):
            self.midi_synth.note_on(channel, note, mapped_vel)
        if self.engine_mode in ("hybrid", "dsp"):
            self.dsp_synth.note_on(channel, note, mapped_vel)
        if self.engine_mode == "fluidsynth" and self.fluidsynth.is_initialized:
            self.fluidsynth.note_on(channel, note, mapped_vel)

    def note_off(self, channel: int, note: int):
        """Release note on the designated channel."""
        channel = max(0, min(15, channel))
        note = max(0, min(127, note))

        should_silence = self.note_manager.note_off(channel, note)
        if should_silence:
            if self.engine_mode in ("hybrid", "windows_midi"):
                self.midi_synth.note_off(channel, note)
            if self.engine_mode in ("hybrid", "dsp"):
                self.dsp_synth.note_off(channel, note)
            if self.engine_mode == "fluidsynth" and self.fluidsynth.is_initialized:
                self.fluidsynth.note_off(channel, note)

    def set_sustain(self, channel: int, active: bool):
        """Set sustain pedal state (CC 64). Releases sustained notes if turned off."""
        channel = max(0, min(15, channel))
        released_notes = self.note_manager.set_sustain(channel, active)

        cc_val = 127 if active else 0
        if self.engine_mode in ("hybrid", "windows_midi"):
            self.midi_synth.control_change(channel, 64, cc_val)
        if self.engine_mode == "fluidsynth" and self.fluidsynth.is_initialized:
            self.fluidsynth.control_change(channel, 64, cc_val)

        # Silence notes released when sustain pedal is lifted
        for note in released_notes:
            if self.engine_mode in ("hybrid", "windows_midi"):
                self.midi_synth.note_off(channel, note)
            if self.engine_mode in ("hybrid", "dsp"):
                self.dsp_synth.note_off(channel, note)
            if self.engine_mode == "fluidsynth" and self.fluidsynth.is_initialized:
                self.fluidsynth.note_off(channel, note)

    def pitch_bend(self, channel: int, pitch: int):
        """Send pitch bend (-8192 to +8191)."""
        channel = max(0, min(15, channel))
        if self.engine_mode in ("hybrid", "windows_midi"):
            self.midi_synth.pitch_bend(channel, pitch)
        if self.engine_mode == "fluidsynth" and self.fluidsynth.is_initialized:
            self.fluidsynth.pitch_bend(channel, pitch)

    def modulation(self, channel: int, value: int):
        """Send modulation (CC 1)."""
        channel = max(0, min(15, channel))
        val = max(0, min(127, value))
        if self.engine_mode in ("hybrid", "windows_midi"):
            self.midi_synth.control_change(channel, 1, val)
        if self.fluidsynth.is_initialized:
            self.fluidsynth.control_change(channel, 1, val)

    def panic(self):
        """Kill all active and sustained notes immediately across all backends."""
        to_silence = self.note_manager.panic_reset()
        self.midi_synth.panic()
        self.dsp_synth.all_notes_off()
        if self.fluidsynth.is_initialized:
            for ch in range(16):
                self.fluidsynth.control_change(ch, 120, 0)
                self.fluidsynth.control_change(ch, 123, 0)

    def close(self):
        self.panic()
        self.midi_synth.close()
        self.fluidsynth.close()
