"""
KIYA Piano Studio Pro - Practice Exercises & Interactive Scale Trainer
Includes Major, Minor, Pentatonic, and Blues scales, alongside interactive note evaluation.
"""

from typing import Dict, List, Tuple, Optional
from app.constants import NOTE_NAMES, midi_to_note_name

class ScaleLibrary:
    """Musical scale database with formula and degree intervals."""

    SCALES: Dict[str, Tuple[List[int], str]] = {
        "Major (Ionian)": ([0, 2, 4, 5, 7, 9, 11, 12], "W - W - H - W - W - W - H"),
        "Natural Minor (Aeolian)": ([0, 2, 3, 5, 7, 8, 10, 12], "W - H - W - W - H - W - W"),
        "Harmonic Minor": ([0, 2, 3, 5, 7, 8, 11, 12], "W - H - W - W - H - 1.5 - H"),
        "Melodic Minor (Ascending)": ([0, 2, 3, 5, 7, 9, 11, 12], "W - H - W - W - W - W - H"),
        "Major Pentatonic": ([0, 2, 4, 7, 9, 12], "1 - 2 - 3 - 5 - 6"),
        "Minor Pentatonic": ([0, 3, 5, 7, 10, 12], "1 - b3 - 4 - 5 - b7"),
        "Blues Scale": ([0, 3, 5, 6, 7, 10, 12], "1 - b3 - 4 - b5 - 5 - b7"),
        "Dorian Mode": ([0, 2, 3, 5, 7, 9, 10, 12], "1 - 2 - b3 - 4 - 5 - 6 - b7"),
        "Mixolydian Mode": ([0, 2, 4, 5, 7, 9, 10, 12], "1 - 2 - 3 - 4 - 5 - 6 - b7")
    }

    @classmethod
    def get_scale_names(cls) -> List[str]:
        return list(cls.SCALES.keys())

    @classmethod
    def get_scale_notes(cls, root_index: int, scale_name: str, base_octave: int = 4) -> Dict[str, any]:
        root_idx = root_index % 12
        root_name = NOTE_NAMES[root_idx]
        intervals, formula = cls.SCALES.get(scale_name, ([0, 2, 4, 5, 7, 9, 11, 12], ""))

        base_midi = (base_octave + 1) * 12 + root_idx
        midi_notes = [base_midi + iv for iv in intervals]
        note_names = [NOTE_NAMES[(root_idx + iv) % 12] for iv in intervals]

        return {
            "root_name": root_name,
            "scale_name": scale_name,
            "display_name": f"{root_name} {scale_name}",
            "formula": formula,
            "note_names": note_names,
            "midi_notes": midi_notes
        }


class NotePracticeTrainer:
    """Interactive practice tool testing note and pitch recognition."""

    def __init__(self):
        self.target_note: int = 60  # C4
        self.score: int = 0
        self.attempts: int = 0
        self.current_streak: int = 0
        self.best_streak: int = 0
        self.last_result: Optional[str] = None

    def new_challenge(self, min_note: int = 48, max_note: int = 72) -> int:
        """Select a random target note in range."""
        import random
        # Exclude same note consecutively
        choices = [n for n in range(min_note, max_note + 1) if n != self.target_note]
        self.target_note = random.choice(choices) if choices else min_note
        self.last_result = None
        return self.target_note

    def get_target_name(self) -> str:
        return midi_to_note_name(self.target_note)

    def evaluate_note(self, played_note: int) -> Tuple[bool, str]:
        """Check if played note matches target."""
        self.attempts += 1
        is_correct = (played_note == self.target_note)
        if is_correct:
            self.score += 10
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
            msg = f"Excellent! Correct note: {midi_to_note_name(played_note)}"
        else:
            diff = played_note - self.target_note
            self.current_streak = 0
            direction = "too high" if diff > 0 else "too low"
            msg = f"Played {midi_to_note_name(played_note)} ({direction}). Target was {midi_to_note_name(self.target_note)}."

        self.last_result = msg
        return is_correct, msg

    def reset_stats(self):
        self.score = 0
        self.attempts = 0
        self.current_streak = 0
        self.best_streak = 0
        self.last_result = None
