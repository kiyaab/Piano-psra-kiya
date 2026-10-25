"""
KIYA Piano Studio Pro - Keyboard Split & Layer Performance Manager
Routes incoming notes according to Single, Dual/Layer, or Split mode.
Ensures clean zone transitions without stuck notes.
"""

from typing import List, Tuple, Dict, Set
from app.constants import (
    DEFAULT_SPLIT_POINT,
    MIDI_CH_RIGHT1,
    MIDI_CH_RIGHT2,
    MIDI_CH_LEFT
)
from audio.synthesizer import SynthesizerFacade

class SplitLayerManager:
    """Manages voice layering, keyboard splitting, and octave transposition."""

    def __init__(self, synth: SynthesizerFacade):
        self.synth = synth

        # Mode toggles
        self.layer_enabled = False
        self.split_enabled = False
        self.split_point = DEFAULT_SPLIT_POINT  # Note 54 (F#3)

        # Transposition & Tuning
        self.master_transpose = 0  # Semitones (-12 to +12)

        # Right 1 Settings
        self.right1_program = 0
        self.right1_octave = 0  # -2 to +2
        self.right1_volume = 1.0
        self.right1_pan = 0.0
        self.right1_mute = False

        # Right 2 (Layer) Settings
        self.right2_program = 48  # String Ensemble
        self.right2_octave = 0
        self.right2_volume = 0.70
        self.right2_pan = 0.0
        self.right2_mute = False

        # Left (Split) Settings
        self.left_program = 32   # Acoustic Bass
        self.left_octave = 0
        self.left_volume = 0.85
        self.left_pan = 0.0
        self.left_mute = False

        # Track sounding notes per input key to cleanly handle note-offs
        # sounding_routes[input_note] = list of (channel, sounding_note)
        self._sounding_routes: Dict[int, List[Tuple[int, int]]] = {}

        self.apply_all_programs()

    def set_split_point(self, split_note: int):
        """Set new split point note number (e.g. 54). Cleans up any active notes in old split."""
        self.split_point = max(24, min(108, split_note))

    def set_layer_enabled(self, enabled: bool):
        self.layer_enabled = enabled

    def set_split_enabled(self, enabled: bool):
        self.split_enabled = enabled

    def apply_all_programs(self):
        """Send current programs and volumes to the synthesizer channels."""
        # Right 1 -> MIDI_CH_RIGHT1
        self.synth.set_program(MIDI_CH_RIGHT1, self.right1_program)
        self.synth.set_channel_volume(MIDI_CH_RIGHT1, 0.0 if self.right1_mute else self.right1_volume)
        self.synth.set_channel_pan(MIDI_CH_RIGHT1, self.right1_pan)

        # Right 2 -> MIDI_CH_RIGHT2
        self.synth.set_program(MIDI_CH_RIGHT2, self.right2_program)
        self.synth.set_channel_volume(MIDI_CH_RIGHT2, 0.0 if self.right2_mute else self.right2_volume)
        self.synth.set_channel_pan(MIDI_CH_RIGHT2, self.right2_pan)

        # Left -> MIDI_CH_LEFT
        self.synth.set_program(MIDI_CH_LEFT, self.left_program)
        self.synth.set_channel_volume(MIDI_CH_LEFT, 0.0 if self.left_mute else self.left_volume)
        self.synth.set_channel_pan(MIDI_CH_LEFT, self.left_pan)

    def route_note_on(self, input_note: int, velocity: int = 100):
        """Route played key note to appropriate channels based on split and layer."""
        if input_note in self._sounding_routes:
            # If key is already sounding, release it first to avoid duplicate hang
            self.route_note_off(input_note)

        routes: List[Tuple[int, int]] = []
        eff_note = input_note + self.master_transpose

        if self.split_enabled and input_note <= self.split_point:
            # Left Hand Zone
            if not self.left_mute:
                sound_note = max(0, min(127, eff_note + (self.left_octave * 12)))
                routes.append((MIDI_CH_LEFT, sound_note))
                self.synth.note_on(MIDI_CH_LEFT, sound_note, velocity)
        else:
            # Right Hand Zone
            # Right 1
            if not self.right1_mute:
                sound_note1 = max(0, min(127, eff_note + (self.right1_octave * 12)))
                routes.append((MIDI_CH_RIGHT1, sound_note1))
                self.synth.note_on(MIDI_CH_RIGHT1, sound_note1, velocity)

            # Right 2 (Layer)
            if self.layer_enabled and not self.right2_mute:
                sound_note2 = max(0, min(127, eff_note + (self.right2_octave * 12)))
                routes.append((MIDI_CH_RIGHT2, sound_note2))
                self.synth.note_on(MIDI_CH_RIGHT2, sound_note2, velocity)

        self._sounding_routes[input_note] = routes

    def route_note_off(self, input_note: int):
        """Release all synth channels that were triggered by this input key."""
        routes = self._sounding_routes.pop(input_note, [])
        for ch, sound_note in routes:
            self.synth.note_off(ch, sound_note)

    def panic(self):
        """Clear all keyboard routing and kill synthesizer notes."""
        self._sounding_routes.clear()
        self.synth.panic()
