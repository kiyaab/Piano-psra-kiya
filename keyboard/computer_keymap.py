"""
KIYA Piano Studio Pro - Computer Keyboard Mapping
Translates physical PC keyboard presses into musical MIDI notes.
Supports two concurrent octaves with sharp/flat keys, octave shift keys, and sustain hotkey.
"""

from typing import Optional, Dict

class ComputerKeymap:
    """Maps PC keyboard keys to relative MIDI semitones."""

    # Relative semitones from base root note
    # Lower octave (Z to M): Semitones 0 to 11
    # Upper octave (Q to U + I): Semitones 12 to 24
    KEY_TO_SEMITONE: Dict[str, int] = {
        # Lower Octave
        'z': 0,   # C
        's': 1,   # C#
        'x': 2,   # D
        'd': 3,   # D#
        'c': 4,   # E
        'v': 5,   # F
        'g': 6,   # F#
        'b': 7,   # G
        'h': 8,   # G#
        'n': 9,   # A
        'j': 10,  # A#
        'm': 11,  # B
        ',': 12,  # C (High C on bottom row)

        # Upper Octave
        'q': 12,  # C
        '2': 13,  # C#
        'w': 14,  # D
        '3': 15,  # D#
        'e': 16,  # E
        'r': 17,  # F
        '5': 18,  # F#
        't': 19,  # G
        '6': 20,  # G#
        'y': 21,  # A
        '7': 22,  # A#
        'u': 23,  # B
        'i': 24,  # High C
        '9': 25,  # C#
        'o': 26,  # D
        '0': 27,  # D#
        'p': 28,  # E
    }

    def __init__(self, base_note: int = 48):  # Default base note C3 (48)
        self.base_note = base_note
        self.octave_offset = 0  # Octave shift in steps of 12

    def set_octave_offset(self, offset: int):
        """Set octave shift (-2 to +2)."""
        self.octave_offset = max(-3, min(3, offset))

    def octave_up(self):
        if self.octave_offset < 3:
            self.octave_offset += 1

    def octave_down(self):
        if self.octave_offset > -3:
            self.octave_offset -= 1

    def key_to_note(self, key_char: str) -> Optional[int]:
        """Convert a pressed key character to a MIDI note number."""
        char = key_char.lower()
        if char in self.KEY_TO_SEMITONE:
            semitone = self.KEY_TO_SEMITONE[char]
            note = self.base_note + (self.octave_offset * 12) + semitone
            return max(0, min(127, note))
        return None

    def get_note_for_key(self, key) -> Optional[int]:
        """Convert a Qt key integer or character string to a MIDI note number."""
        if isinstance(key, str):
            return self.key_to_note(key)
        elif isinstance(key, int):
            # Special keys like comma
            if key == 44 or key == 0x2C:
                return self.key_to_note(',')
            try:
                char = chr(key).lower()
                return self.key_to_note(char)
            except (ValueError, OverflowError):
                pass
        return None
