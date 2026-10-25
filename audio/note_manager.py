"""
KIYA Piano Studio Pro - Note & Polyphony Manager
Tracks active notes, handles sustain pedal logic (MIDI CC 64),
implements velocity curves, and guarantees clean note releases without stuck notes.
"""

import threading
from typing import Dict, Set, Tuple, List, Optional
from app.constants import DEFAULT_VELOCITY

class NoteManager:
    """Thread-safe note tracking and sustain management."""

    def __init__(self):
        self._lock = threading.RLock()
        # active_notes[channel] = set of currently sounding MIDI note numbers
        self._active_notes: Dict[int, Set[int]] = {ch: set() for ch in range(16)}
        # sustained_notes[channel] = set of notes released by key while sustain pedal was pressed
        self._sustained_notes: Dict[int, Set[int]] = {ch: set() for ch in range(16)}
        # sustain_pedal[channel] = True/False
        self._sustain_pedal: Dict[int, bool] = {ch: False for ch in range(16)}
        self._velocity_curve = "linear"  # linear, soft, hard, fixed
        self._fixed_velocity = 100

    def set_velocity_curve(self, curve_type: str, fixed_val: int = 100):
        with self._lock:
            self._velocity_curve = curve_type.lower()
            self._fixed_velocity = max(1, min(127, fixed_val))

    def map_velocity(self, raw_velocity: int) -> int:
        """Map raw input velocity (1-127) using the selected velocity curve."""
        v = max(1, min(127, raw_velocity))
        if self._velocity_curve == "fixed":
            return self._fixed_velocity
        elif self._velocity_curve == "soft":
            # Easier to reach high velocities
            normalized = v / 127.0
            curved = normalized ** 0.6
            return int(max(1, min(127, round(curved * 127))))
        elif self._velocity_curve == "hard":
            # Requires harder strikes to reach high velocities
            normalized = v / 127.0
            curved = normalized ** 1.6
            return int(max(1, min(127, round(curved * 127))))
        # Linear by default
        return v

    def note_on(self, channel: int, note: int, velocity: int) -> int:
        """Register a note-on event. If previously sustained, remove from sustained set."""
        channel = max(0, min(15, channel))
        mapped_vel = self.map_velocity(velocity)
        with self._lock:
            self._active_notes[channel].add(note)
            if note in self._sustained_notes[channel]:
                self._sustained_notes[channel].remove(note)
        return mapped_vel

    def note_off(self, channel: int, note: int) -> bool:
        """
        Process a note-off event.
        If sustain pedal is currently active on this channel, hold the note in sustained_notes
        and return False (meaning: do NOT silence yet).
        Otherwise remove note and return True (silence now).
        """
        channel = max(0, min(15, channel))
        with self._lock:
            if self._sustain_pedal[channel]:
                # Hold note until sustain is released
                if note in self._active_notes[channel]:
                    self._sustained_notes[channel].add(note)
                    return False
            # Not sustained: release note immediately
            self._active_notes[channel].discard(note)
            self._sustained_notes[channel].discard(note)
            return True

    def set_sustain(self, channel: int, active: bool) -> List[int]:
        """
        Handle sustain pedal change (CC 64).
        If sustain is turned OFF, return a list of all notes that were sustained
        and must now be silenced.
        """
        channel = max(0, min(15, channel))
        released_notes: List[int] = []
        with self._lock:
            self._sustain_pedal[channel] = active
            if not active:
                # Release all notes that were sustained
                released_notes = list(self._sustained_notes[channel])
                for note in released_notes:
                    self._active_notes[channel].discard(note)
                self._sustained_notes[channel].clear()
        return released_notes

    def is_note_sounding(self, channel: int, note: int) -> bool:
        with self._lock:
            return note in self._active_notes.get(channel, set())

    def get_sounding_notes(self, channel: int = None) -> Set[int]:
        """Get set of all active notes across a given channel or all channels."""
        with self._lock:
            if channel is not None:
                return set(self._active_notes.get(channel, set()))
            all_sounding = set()
            for ch_set in self._active_notes.values():
                all_sounding.update(ch_set)
            return all_sounding

    def panic_reset(self) -> List[Tuple[int, int]]:
        """
        Clear all note tracking and return list of (channel, note) pairs
        that need note-off commands sent to hardware / synths.
        """
        to_silence: List[Tuple[int, int]] = []
        with self._lock:
            for ch in range(16):
                for note in self._active_notes[ch]:
                    to_silence.append((ch, note))
                for note in self._sustained_notes[ch]:
                    to_silence.append((ch, note))
                self._active_notes[ch].clear()
                self._sustained_notes[ch].clear()
                self._sustain_pedal[ch] = False
        return to_silence
