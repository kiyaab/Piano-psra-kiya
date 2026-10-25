"""
KIYA Piano Studio Pro - MIDI Event Representations
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class NoteEvent:
    channel: int
    note: int
    velocity: int
    is_on: bool
    timestamp: float = 0.0

@dataclass
class ControlChangeEvent:
    channel: int
    control: int
    value: int
    timestamp: float = 0.0

@dataclass
class PitchBendEvent:
    channel: int
    pitch: int
    timestamp: float = 0.0

@dataclass
class ProgramChangeEvent:
    channel: int
    program: int
    timestamp: float = 0.0
