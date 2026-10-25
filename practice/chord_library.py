"""
KIYA Piano Studio Pro - Interactive Chord Encyclopedia
Provides chord formulas, note spellings, fingerings, and audio previews for all keys.
"""

from typing import Dict, List, Tuple
from app.constants import NOTE_NAMES

class ChordLibrary:
    """Encyclopedia of musical chords, formulas, and piano voicings."""

    CHORD_TYPES: Dict[str, Tuple[str, List[int], str]] = {
        # Name: (Display Suffix, Intervals from root, Formula description)
        "Major": ("", [0, 4, 7], "1 - 3 - 5"),
        "Minor": ("m", [0, 3, 7], "1 - b3 - 5"),
        "Dominant 7th": ("7", [0, 4, 7, 10], "1 - 3 - 5 - b7"),
        "Major 7th": ("Maj7", [0, 4, 7, 11], "1 - 3 - 5 - 7"),
        "Minor 7th": ("m7", [0, 3, 7, 10], "1 - b3 - 5 - b7"),
        "Diminished": ("dim", [0, 3, 6], "1 - b3 - b5"),
        "Diminished 7th": ("dim7", [0, 3, 6, 9], "1 - b3 - b5 - bb7"),
        "Half-Diminished (m7b5)": ("m7b5", [0, 3, 6, 10], "1 - b3 - b5 - b7"),
        "Augmented": ("aug", [0, 4, 8], "1 - 3 - #5"),
        "Suspended 4th": ("sus4", [0, 5, 7], "1 - 4 - 5"),
        "Suspended 2nd": ("sus2", [0, 2, 7], "1 - 2 - 5"),
        "Major 6th": ("6", [0, 4, 7, 9], "1 - 3 - 5 - 6"),
        "Minor 6th": ("m6", [0, 3, 7, 9], "1 - b3 - 5 - 6"),
        "Add 9": ("add9", [0, 2, 4, 7], "1 - 2 - 3 - 5"),
    }

    @classmethod
    def get_chord_types(cls) -> List[str]:
        return list(cls.CHORD_TYPES.keys())

    @classmethod
    def get_chord_info(cls, root_index: int, chord_type: str, base_octave: int = 4) -> Dict[str, any]:
        """Generate chord details: display name, note names, MIDI numbers, formula."""
        root_idx = root_index % 12
        root_name = NOTE_NAMES[root_idx]
        suffix, intervals, formula = cls.CHORD_TYPES.get(chord_type, ("", [0, 4, 7], "1 - 3 - 5"))

        base_midi = (base_octave + 1) * 12 + root_idx
        midi_notes = [base_midi + iv for iv in intervals]
        note_names = [NOTE_NAMES[(root_idx + iv) % 12] for iv in intervals]

        return {
            "root_name": root_name,
            "chord_type": chord_type,
            "display_name": f"{root_name}{suffix}",
            "formula": formula,
            "note_names": note_names,
            "midi_notes": midi_notes,
            "spelling": " - ".join(note_names)
        }
