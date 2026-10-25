"""
KIYA Piano Studio Pro - Advanced Chord Recognition Engine
Detects musical chords, qualities, inversions, and slash chords from played keys.
Supports both 'Full-Finger' and Yamaha-style 'Single-Finger' chord input modes.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from app.constants import NOTE_NAMES

@dataclass
class ChordInfo:
    root_name: str
    root_pitch: int  # 0 to 11 (C = 0, C# = 1, ...)
    quality: str     # "Maj", "m", "7", "Maj7", "m7", "dim", "aug", "sus4", "sus2", etc.
    display_name: str
    bass_name: str
    is_inversion: bool
    notes: List[int]
    intervals: Tuple[int, ...]

class ChordDetector:
    """Detects musical chords and inversions from a collection of active MIDI notes."""

    # Canonical interval definitions (relative to root = 0)
    CHORD_TEMPLATES = {
        # Triads
        (0, 4, 7): ("Maj", ""),
        (0, 3, 7): ("m", "m"),
        (0, 3, 6): ("dim", "dim"),
        (0, 4, 8): ("aug", "aug"),
        (0, 5, 7): ("sus4", "sus4"),
        (0, 2, 7): ("sus2", "sus2"),

        # Four-note 7th Chords
        (0, 4, 7, 10): ("7", "7"),
        (0, 4, 7, 11): ("Maj7", "Maj7"),
        (0, 3, 7, 10): ("m7", "m7"),
        (0, 3, 7, 11): ("mMaj7", "mMaj7"),
        (0, 3, 6, 10): ("m7b5", "m7b5"),
        (0, 3, 6, 9):  ("dim7", "dim7"),
        (0, 5, 7, 10): ("7sus4", "7sus4"),

        # 6th and Add chords
        (0, 4, 7, 9):  ("6", "6"),
        (0, 3, 7, 9):  ("m6", "m6"),
        (0, 2, 4, 7):  ("add9", "add9"),

        # Incomplete 7ths (5th omitted)
        (0, 4, 10): ("7", "7(no5)"),
        (0, 3, 10): ("m7", "m7(no5)"),
        (0, 4, 11): ("Maj7", "Maj7(no5)"),

        # Fifths / Power chord
        (0, 7): ("5", "5"),
    }

    def __init__(self, mode: str = "full"):
        self.mode = mode  # "full" or "simplified"
        self.last_detected: Optional[ChordInfo] = None

    def set_mode(self, mode: str):
        self.mode = "simplified" if mode.lower() in ("single", "simplified", "easy") else "full"

    def detect_from_notes(self, notes: List[int]) -> Optional[ChordInfo]:
        """Detect chord from list of currently played MIDI notes."""
        if not notes:
            return self.last_detected

        if self.mode == "simplified":
            return self._detect_simplified(notes)
        else:
            return self._detect_full(notes)

    def _detect_simplified(self, notes: List[int]) -> ChordInfo:
        """Yamaha-style Easy Chord recognition."""
        sorted_notes = sorted(notes)
        root_note = sorted_notes[-1]  # Highest note is root key in typical single-finger
        root_pitch = root_note % 12
        root_name = NOTE_NAMES[root_pitch]

        if len(sorted_notes) == 1:
            # 1 key: Major chord
            chord = ChordInfo(
                root_name=root_name,
                root_pitch=root_pitch,
                quality="Maj",
                display_name=root_name,
                bass_name=root_name,
                is_inversion=False,
                notes=sorted_notes,
                intervals=(0, 4, 7)
            )
        elif len(sorted_notes) == 2:
            # 2 keys: check if lower key is black or white key to the left
            lower_note = sorted_notes[0]
            is_black = (lower_note % 12) in (1, 3, 6, 8, 10)
            if is_black:
                # Black key to the left = Minor chord
                chord = ChordInfo(
                    root_name=root_name,
                    root_pitch=root_pitch,
                    quality="m",
                    display_name=f"{root_name}m",
                    bass_name=root_name,
                    is_inversion=False,
                    notes=sorted_notes,
                    intervals=(0, 3, 7)
                )
            else:
                # White key to the left = 7th chord
                chord = ChordInfo(
                    root_name=root_name,
                    root_pitch=root_pitch,
                    quality="7",
                    display_name=f"{root_name}7",
                    bass_name=root_name,
                    is_inversion=False,
                    notes=sorted_notes,
                    intervals=(0, 4, 7, 10)
                )
        else:
            # 3 keys: Minor 7th chord
            chord = ChordInfo(
                root_name=root_name,
                root_pitch=root_pitch,
                quality="m7",
                display_name=f"{root_name}m7",
                bass_name=root_name,
                is_inversion=False,
                notes=sorted_notes,
                intervals=(0, 3, 7, 10)
            )

        self.last_detected = chord
        return chord

    def _detect_full(self, notes: List[int]) -> Optional[ChordInfo]:
        """Full-finger chromatic chord detection with inversion analysis."""
        sorted_notes = sorted(notes)
        lowest_note = sorted_notes[0]
        bass_pitch = lowest_note % 12
        bass_name = NOTE_NAMES[bass_pitch]

        pitch_classes = sorted(list(set(n % 12 for n in sorted_notes)))
        n_pitches = len(pitch_classes)

        if n_pitches == 0:
            return self.last_detected

        if n_pitches == 1:
            root = pitch_classes[0]
            root_name = NOTE_NAMES[root]
            chord = ChordInfo(
                root_name=root_name,
                root_pitch=root,
                quality="Maj",
                display_name=root_name,
                bass_name=root_name,
                is_inversion=False,
                notes=sorted_notes,
                intervals=(0, 4, 7)
            )
            self.last_detected = chord
            return chord

        best_chord: Optional[ChordInfo] = None
        best_score = -1

        # Test each pitch class as candidate root
        for candidate_root in pitch_classes:
            intervals = tuple(sorted((p - candidate_root) % 12 for p in pitch_classes))
            if intervals in self.CHORD_TEMPLATES:
                quality, suffix = self.CHORD_TEMPLATES[intervals]
                root_name = NOTE_NAMES[candidate_root]
                is_inv = (candidate_root != bass_pitch)
                disp_name = f"{root_name}{suffix}"
                if is_inv:
                    disp_name = f"{disp_name}/{bass_name}"

                # Prioritize root positions and common triads/7ths
                score = 100
                if not is_inv:
                    score += 50
                if quality in ("Maj", "m"):
                    score += 30
                elif quality in ("7", "Maj7", "m7"):
                    score += 20

                if score > best_score:
                    best_score = score
                    best_chord = ChordInfo(
                        root_name=root_name,
                        root_pitch=candidate_root,
                        quality=quality,
                        display_name=disp_name,
                        bass_name=bass_name,
                        is_inversion=is_inv,
                        notes=sorted_notes,
                        intervals=intervals
                    )

        if best_chord:
            self.last_detected = best_chord
            return best_chord

        # Fallback: Treat lowest note as root major/minor estimation
        root = bass_pitch
        root_name = bass_name
        fallback = ChordInfo(
            root_name=root_name,
            root_pitch=root,
            quality="Maj",
            display_name=root_name,
            bass_name=root_name,
            is_inversion=False,
            notes=sorted_notes,
            intervals=(0, 4, 7)
        )
        self.last_detected = fallback
        return fallback
